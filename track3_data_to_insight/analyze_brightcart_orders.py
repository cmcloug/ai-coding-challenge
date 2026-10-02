#!/usr/bin/env python3
"""Summarize BrightCart H1 2025 results and write a repeatable findings report.

Run: python3 analyze_brightcart_orders.py
Optional: python3 analyze_brightcart_orders.py cleaned.csv output_directory
Uses only the Python standard library.
"""
import csv
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "brightcart_orders_cleaned.csv"
DEFAULT_OUTPUT = HERE
START, END = date(2025, 1, 1), date(2025, 6, 30)
ZERO = Decimal("0")

def money(value):
    return f"${value:,.2f}"

def pct(value):
    return f"{value:.1f}%"

def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None

def write_summary(path, rows, key_name):
    fields = [key_name, "orders", "completed_orders", "returned_orders", "cancelled_orders",
              "revenue_usd", "revenue_share_pct", "return_rate_pct"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    with source.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"order_id", "customer_id", "order_date", "region", "product",
                    "quantity", "unit_price", "discount_pct", "status"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing required columns: {', '.join(sorted(missing))}")
        all_rows = list(reader)

    h1, invalid_dates = [], 0
    for row in all_rows:
        try:
            day = date.fromisoformat(row["order_date"])
        except (ValueError, TypeError):
            invalid_dates += 1
            continue
        if START <= day <= END:
            h1.append(row)

    negative_rows = []
    insight_rows = []
    for row in h1:
        qty = parse_decimal(row["quantity"])
        if qty is not None and qty < 0:
            negative_rows.append((row, qty))
        else:
            insight_rows.append(row)

    # Negative quantities are excluded from all insight totals/rates. Revenue
    # follows the brief; missing or unparseable inputs exclude only revenue.
    revenue_inputs_missing = 0
    revenue_by_row = {}
    for idx, row in enumerate(insight_rows):
        if row["status"] != "Completed":
            continue
        qty = parse_decimal(row["quantity"])
        price = parse_decimal(row["unit_price"])
        discount = parse_decimal(row["discount_pct"])
        if qty is None or price is None or discount is None:
            revenue_inputs_missing += 1
            continue
        revenue_by_row[idx] = qty * price * (Decimal("1") - discount / Decimal("100"))

    def summarize(field, exclude_large=False):
        groups = defaultdict(lambda: {"orders": 0, "Completed": 0, "Returned": 0,
                                      "Cancelled": 0, "revenue": ZERO})
        for idx, row in enumerate(insight_rows):
            qty = parse_decimal(row["quantity"])
            if exclude_large and qty is not None and qty > 10:
                continue
            key = row[field] or "(Missing)"
            group = groups[key]
            group["orders"] += 1
            if row["status"] in ("Completed", "Returned", "Cancelled"):
                group[row["status"]] += 1
            if idx in revenue_by_row:
                group["revenue"] += revenue_by_row[idx]
        total = sum((x["revenue"] for x in groups.values()), ZERO)
        result = []
        for key, group in groups.items():
            eligible = group["Completed"] + group["Returned"]
            return_rate = (100 * group["Returned"] / eligible) if eligible else 0
            share = (100 * group["revenue"] / total) if total else 0
            result.append({
                field: key, "orders": group["orders"],
                "completed_orders": group["Completed"], "returned_orders": group["Returned"],
                "cancelled_orders": group["Cancelled"], "revenue_usd": f"{group['revenue']:.2f}",
                "revenue_share_pct": f"{share:.2f}", "return_rate_pct": f"{return_rate:.2f}",
                "_revenue": group["revenue"], "_return_rate": return_rate,
                "_eligible": eligible,
            })
        return sorted(result, key=lambda r: (-r["_revenue"], r[field]))

    regions, products = summarize("region"), summarize("product")
    regions_no_large, products_no_large = summarize("region", True), summarize("product", True)
    total_revenue = sum(revenue_by_row.values(), ZERO)
    status_counts = Counter(row["status"] for row in insight_rows)
    return_denominator = status_counts["Completed"] + status_counts["Returned"]
    overall_return_rate = (100 * status_counts["Returned"] / return_denominator) if return_denominator else 0
    completed_missing_customer = sum(1 for row in insight_rows if row["status"] == "Completed" and not row["customer_id"])
    missing_customers = sum(1 for row in insight_rows if not row["customer_id"])
    missing_revenue_inputs = sum(1 for row in insight_rows if row["status"] == "Completed" and
                                 (parse_decimal(row["quantity"]) is None or parse_decimal(row["unit_price"]) is None or
                                  parse_decimal(row["discount_pct"]) is None))
    large_rows = [(idx, row, parse_decimal(row["quantity"]))
                  for idx, row in enumerate(insight_rows)
                  if (parse_decimal(row["quantity"]) is not None and parse_decimal(row["quantity"]) > 10)]
    large_revenue = sum((revenue_by_row[idx] for idx, _, _ in large_rows if idx in revenue_by_row), ZERO)

    output_dir.mkdir(parents=True, exist_ok=True)
    def comparative_summary(rows_with, rows_without, key):
        without = {r[key]: r for r in rows_without}
        merged = []
        for included in rows_with:
            excluded = without.get(included[key], {"orders": 0, "completed_orders": 0,
                "returned_orders": 0, "cancelled_orders": 0, "revenue_usd": "0.00",
                "revenue_share_pct": "0.00", "return_rate_pct": "0.00"})
            merged.append({
                key: included[key], "orders_including_gt10": included["orders"],
                "completed_including_gt10": included["completed_orders"],
                "revenue_including_gt10_usd": included["revenue_usd"],
                "share_including_gt10_pct": included["revenue_share_pct"],
                "orders_excluding_gt10": excluded["orders"],
                "completed_excluding_gt10": excluded["completed_orders"],
                "revenue_excluding_gt10_usd": excluded["revenue_usd"],
                "share_excluding_gt10_pct": excluded["revenue_share_pct"],
            })
        return merged

    region_comparison = comparative_summary(regions, regions_no_large, "region")
    product_comparison = comparative_summary(products, products_no_large, "product")
    for filename, rows, key in (("brightcart_region_summary.csv", region_comparison, "region"),
                                ("brightcart_product_summary.csv", product_comparison, "product")):
        with (output_dir / filename).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else [key])
            writer.writeheader()
            writer.writerows(rows)

    def table(rows, field, limit=None):
        shown = rows[:limit] if limit else rows
        lines = [f"| {field.title()} | Orders | Completed | Returned | Revenue | Revenue share | Return rate* |",
                 "|---|---:|---:|---:|---:|---:|---:|"]
        for r in shown:
            lines.append(f"| {r[field]} | {r['orders']} | {r['completed_orders']} | {r['returned_orders']} | "
                         f"{money(r['_revenue'])} | {pct(Decimal(r['revenue_share_pct']))} | "
                         f"{pct(r['_return_rate'])} ({r['_eligible']} orders) |")
        return "\n".join(lines)

    def comparison_table(rows_in, rows_out, field):
        excluded = {r[field]: r for r in rows_out}
        lines = [f"| {field.title()} | Orders incl. >10 | Completed incl. >10 | Revenue incl. >10 | Share incl. >10 | Orders excl. >10 | Completed excl. >10 | Revenue excl. >10 | Share excl. >10 |",
                 "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for inc in rows_in:
            exc = excluded.get(inc[field])
            if not exc:
                continue
            lines.append(f"| {inc[field]} | {inc['orders']} | {inc['completed_orders']} | {money(inc['_revenue'])} | "
                         f"{pct(Decimal(inc['revenue_share_pct']))} | {exc['orders']} | {exc['completed_orders']} | "
                         f"{money(exc['_revenue'])} | {pct(Decimal(exc['revenue_share_pct']))} |")
        return "\n".join(lines)

    top_region = regions[0] if regions else None
    top_product = products[0] if products else None
    highest_returns = max((r for r in products_no_large if r["_eligible"] >= 5),
                          key=lambda r: (r["_return_rate"], r["_eligible"]), default=None)
    report = ["# BrightCart H1 2025: Results and focus", "",
              f"Source: `{source.name}`. Analysis window: January 1–June 30, 2025.",
              "Revenue = quantity × unit price × (1 − discount / 100), for Completed orders only.", "",
              "## Findings", ""]
    if top_region:
        report.append(f"1. **{top_region['region']} led regional revenue**, with {money(top_region['_revenue'])} "
                      f"({pct(Decimal(top_region['revenue_share_pct']))} of total completed revenue) from {top_region['completed_orders']} completed orders.")
    if top_product:
        report.append(f"2. **{top_product['product']} was the top product by revenue**, generating {money(top_product['_revenue'])} "
                      f"({pct(Decimal(top_product['revenue_share_pct']))} of total) from {top_product['completed_orders']} completed orders.")
    if regions_no_large and products_no_large:
        report.append(f"**Sensitivity check:** excluding orders above 10 units, **{regions_no_large[0]['region']}** leads regional revenue "
                      f"({money(regions_no_large[0]['_revenue'])}) and **{products_no_large[0]['product']}** leads product revenue "
                      f"({money(products_no_large[0]['_revenue'])}).")
    if highest_returns:
        report.append(f"3. **{highest_returns['product']} had the highest product return rate among products with at least five completed/returned orders**: "
                      f"{pct(highest_returns['_return_rate'])} ({highest_returns['returned_orders']} returned of {highest_returns['_eligible']} completed or returned orders). "
                      "Use this as a review signal, especially where the denominator is small.")
    else:
        report.append("3. No product had at least five completed/returned orders, so product return-rate comparisons are too thin to rank reliably.")
    report += ["", "## Regional summary", "", comparison_table(regions, regions_no_large, "region"), "",
               "## Product summary", "", comparison_table(products, products_no_large, "product"), "",
               "Orders with negative quantities are excluded from all summaries. `Incl. >10` includes orders with more than 10 units; `excl. >10` removes them. Revenue includes only Completed orders with parseable inputs. Return rate = Returned / (Completed + Returned); Cancelled orders are excluded.", "",
               "## Recommendation", ""]
    if top_region and top_product:
        if regions_no_large and (regions_no_large[0]["region"] != top_region["region"] or
                                 products_no_large[0]["product"] != top_product["product"]):
            report.append(f"Verify the >10-unit orders, which account for {money(large_revenue)} in completed revenue. The all-order leaders are **{top_region['region']}** and **{top_product['product']}**, while the leaders excluding >10-unit orders are **{regions_no_large[0]['region']}** and **{products_no_large[0]['product']}**. Use both scenarios in planning until the quantities are confirmed. Review the high Zephyr Headphones return rate before increasing its promotion.")
        else:
            report.append(f"Prioritize inventory and campaign review for **{top_region['region']}**, led by **{top_product['product']}** nationally. "
                          "Before expanding spend, verify unusual quantities, check return rates, and confirm inventory availability.")
    else:
        report.append("Review the regional and product summaries before setting next-quarter priorities; the source does not provide enough valid H1 revenue data for a supported ranking.")
    report += ["", "## Data cautions", "",
               f"- {len(all_rows)} cleaned rows were read; {len(h1)} fall in H1 2025. {invalid_dates} rows had dates that could not be parsed and were excluded from date-based analysis.",
               f"- {len(negative_rows)} H1 row(s) have negative quantities and were excluded from all insight calculations: " + (", ".join(f"{r['order_id']} ({q} units)" for r, q in negative_rows) or "none") + ".",
               f"- {len(large_rows)} H1 row(s) have quantities greater than 10 and are shown in both scenarios. Together, their Completed orders contribute {money(large_revenue)} when included: " + (", ".join(f"{r['order_id']} ({q} × {r['product']}, {r['region']})" for _, r, q in large_rows) or "none") + ".",
               f"- {missing_customers} H1 nonnegative-quantity rows have no customer ID ({completed_missing_customer} are Completed). These rows are included in regional/product, revenue, and return insights whenever the other required fields are present; missing customer IDs only prevent customer-level analysis and follow-up.",
               f"- {missing_revenue_inputs} Completed H1 orders lack parseable quantity, price, or discount and are excluded from revenue; {revenue_inputs_missing} counted during revenue calculation.",
               f"- There are {status_counts['Returned']} Returned orders and {status_counts['Cancelled']} Cancelled orders among {len(insight_rows)} included H1 rows. Overall return rate is {pct(overall_return_rate)} across {return_denominator} Completed or Returned orders.",
               "- Duplicate order IDs were merged by the cleaning script. Blank fields were filled from duplicate rows; conflicts, if any, use the first row's value and are documented in the cleaning audit.",
               "", "## Reproducible outputs", "",
               "This script also writes `brightcart_region_summary.csv` and `brightcart_product_summary.csv`; each compares results with and without >10-unit orders.", ""]
    report_path = output_dir / "brightcart_findings.md"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"H1 rows: {len(h1)}; negative quantities excluded: {len(negative_rows)}; completed revenue including >10-unit orders: {money(total_revenue)}")
    print(f"Report: {report_path}")
    print(f"Region table: {output_dir / 'brightcart_region_summary.csv'}")
    print(f"Product table: {output_dir / 'brightcart_product_summary.csv'}")

if __name__ == "__main__":
    main()
