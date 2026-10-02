#!/usr/bin/env python3
"""Normalize BrightCart orders and write row-level change and issue audits.

Run from any directory:
    python3 clean_brightcart_orders.py
Optional paths:
    python3 clean_brightcart_orders.py input.csv cleaned.csv audit.csv

The source is never modified. Missing/impossible values are retained as-is (or
blank) and flagged; this script does not infer business data or remove rows.
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from autocorrect import Speller

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "brightcart_orders.csv"
DEFAULT_OUTPUT = HERE / "brightcart_orders_cleaned.csv"
DEFAULT_AUDIT = HERE / "brightcart_orders_audit.csv"

FIELDS = ["order_id", "customer_id", "order_date", "region", "product",
          "category", "quantity", "unit_price", "discount_pct", "status", "sales_rep"]
REGION_ALIASES = {
    "ne": "Northeast", "north east": "Northeast",
    "se": "Southeast", "south east": "Southeast",
    "mw": "Midwest", "mid west": "Midwest", "mid-west": "Midwest",
    "w": "West",
}
VALID_STATUSES = {"completed": "Completed", "returned": "Returned", "cancelled": "Cancelled"}
STATUS_SPELLER = Speller("en", fast=True)

def canonical_spellings(rows, field):
    """Choose the dataset's most common spelling for each case-insensitive value.

    This learns product/rep spellings from the input instead of maintaining a
    hard-coded list. Ties favor conventional title case, then lexical order.
    """
    variants = defaultdict(Counter)
    for row in rows:
        value = row[field].strip()
        if value:
            variants[value.casefold()][value] += 1
    result = {}
    for key, counts in variants.items():
        result[key] = sorted(counts, key=lambda value: (
            -counts[value], value != value.title(), value.casefold(), value
        ))[0]
    return result

def normalize(field, raw, spellings):
    s = raw.strip()
    if field in ("order_id", "customer_id"):
        return s.upper()
    if field == "order_date":
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d", "%b %d, %Y"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        return s
    if field == "region":
        key = " ".join(s.casefold().split())
        return REGION_ALIASES.get(key, spellings.get(field, {}).get(s.casefold(), s.title()))
    if field in ("product", "sales_rep"):
        return spellings.get(field, {}).get(s.casefold(), s.title())
    if field == "category":
        return spellings.get(field, {}).get(s.casefold(), s.title())
    if field == "status":
        key = s.casefold()
        # Accept exact allowed values directly. Otherwise ask autocorrect to
        # repair spelling, and apply the result only if it matches our whitelist.
        # This prevents a general dictionary from inventing a business status.
        corrected = STATUS_SPELLER(key)
        if key in VALID_STATUSES:
            return VALID_STATUSES[key]
        if corrected in VALID_STATUSES:
            return VALID_STATUSES[corrected]
        return s.title()
    if field in ("quantity", "unit_price", "discount_pct"):
        numeric = s.replace("$", "").replace(",", "")
        if not numeric:
            return ""
        try:
            value = Decimal(numeric)
        except InvalidOperation:
            return s
        if field == "quantity":
            return str(int(value)) if value == value.to_integral_value() else s
        if field == "unit_price":
            return f"{value:.3f}"
        if field == "discount_pct":
            return str(int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        return str(value.normalize())
    return s

def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    audit = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_AUDIT
    with src.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise SystemExit(f"Unexpected columns: {reader.fieldnames!r}")
        raw_rows = list(reader)

    # Learn canonical capitalization from the most frequent spelling in the
    # source for each value. Case differences are normalized without lists of
    # every product or representative name in the script.
    spellings = {field: canonical_spellings(raw_rows, field)
                 for field in ("region", "product", "category", "status", "sales_rep")}
    normalized_rows, events = [], []
    for row_num, raw in enumerate(raw_rows, start=2):
        row = {}
        for field in FIELDS:
            value = normalize(field, raw[field], spellings)
            row[field] = value
            if value != raw[field]:
                events.append([row_num, row.get("order_id", raw["order_id"]), field,
                               raw[field], value, "normalized formatting or known alias"])
        normalized_rows.append((row_num, row))

    # Merge duplicate order IDs in source order. Blank fields are filled from
    # later copies. Conflicting populated values keep the first value and are
    # explicitly logged so they are not silently overwritten.
    retained, by_order_id = [], {}
    merged_groups = 0
    for row_num, row in normalized_rows:
        order_id = row["order_id"]
        if not order_id or order_id not in by_order_id:
            by_order_id[order_id] = len(retained) if order_id else None
            retained.append({"source_row": row_num, "row": row.copy(), "source_rows": [row_num]})
            continue

        target = retained[by_order_id[order_id]]
        target["source_rows"].append(row_num)
        if len(target["source_rows"]) == 2:
            merged_groups += 1
        events.append([row_num, order_id, "order_id", order_id, order_id,
                       f"merged into source row {target['source_row']}; source rows {','.join(map(str, target['source_rows']))}"])
        for field in FIELDS:
            old_value, new_value = target["row"][field], row[field]
            if not old_value and new_value:
                target["row"][field] = new_value
                events.append([row_num, order_id, field, "", new_value,
                               f"filled from duplicate source row {row_num}; retained record is row {target['source_row']}"])
            elif old_value and new_value and old_value != new_value:
                events.append([row_num, order_id, field, new_value, old_value,
                               f"conflict across duplicate order ID; kept source row {target['source_row']} value; review source rows {','.join(map(str, target['source_rows']))}"])

    cleaned = [item["row"] for item in retained]

    # Flag anomalies rather than guessing, changing, or deleting substantive data.
    for item in retained:
        row_num, row = item["source_row"], item["row"]
        for field in ("customer_id", "quantity", "unit_price"):
            if not row[field]:
                events.append([row_num, row["order_id"], field, "", "", "missing value; left blank for review"])
        for field, lo, hi in (("quantity", 1, 100), ("unit_price", 0, 10000), ("discount_pct", 0, 100)):
            try:
                value = Decimal(row[field])
                if value < lo or value > hi:
                    events.append([row_num, row["order_id"], field, row[field], row[field],
                                   f"out of review range {lo}..{hi}; retained, verify source"])
            except (InvalidOperation, ValueError):
                if row[field]:
                    events.append([row_num, row["order_id"], field, row[field], row[field], "not parseable; retained, verify source"])
        try:
            datetime.strptime(row["order_date"], "%Y-%m-%d")
        except ValueError:
            events.append([row_num, row["order_id"], "order_date", row["order_date"], row["order_date"], "unrecognized date; retained, verify source"])
        if row["status"] not in ("Completed", "Returned", "Cancelled"):
            events.append([row_num, row["order_id"], "status", row["status"], row["status"], "unrecognized status; retained, verify source"])

    out.parent.mkdir(parents=True, exist_ok=True)
    audit.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(cleaned)
    with audit.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_csv_row", "order_id", "field", "original_value", "cleaned_value", "action_or_issue"])
        writer.writerows(events)
    changed = sum(1 for e in events if e[5] == "normalized formatting or known alias")
    print(f"Rows: {len(raw_rows)} input -> {len(cleaned)} output; merged duplicate order-ID groups: {merged_groups}")
    print(f"Cell normalizations: {changed}; audit entries including merge decisions and unresolved issues: {len(events)}")
    print(f"Cleaned file: {out}\nAudit file: {audit}")

if __name__ == "__main__":
    main()
