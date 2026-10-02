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

    # Revenue follows the brief exactly. Missing or unparseable inputs exclude
    # that completed order from the revenue sum and are counted for caution.
    revenue_inputs_missing = 0
    revenue_by_row = {}
    for idx, row in enumerate(h1):
        if row["status"] != "Completed":
            continue
        qty = parse_decimal(row["quantity"])
        price = parse_decimal(row["unit_price"])
        discount = parse_decimal(row["discount_pct"])
        if qty is None or price is None or discount is None:
            revenue_inputs_missing += 1
            continue
        revenue_by_row[idx] = qty * price * (Decimal("1") - discount / Decimal("100"))

    def summarize(field):
        groups = defaultdict(lambda: {"orders": 0, "Completed": 0, "Returned": 0,
                                      "Cancelled": 0, "revenue": ZERO})
        for idx, row in enumerate(h1):
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
    total_revenue = sum(revenue_by_row.values(), ZERO)
    status_counts = Counter(row["status"] for row in h1)
    return_denominator = status_counts["Completed"] + status_counts["Returned"]
    overall_return_rate = (100 * status_counts["Returned"] / return_denominator) if return_denominator else 0
    completed_missing_customer = sum(1 for row in h1 if row["status"] == "Completed" and not row["customer_id"])
    missing_customers = sum(1 for row in h1 if not row["customer_id"])
    missing_revenue_inputs = sum(1 for row in h1 if row["status"] == "Completed" and
                                 (parse_decimal(row["quantity"]) is None or parse_decimal(row["unit_price"]) is None or
                                  parse_decimal(row["discount_pct"]) is None))
    unusual_qty = [(row, parse_decimal(row["quantity"])) for row in h1]
    unusual_qty = [(r, q) for r, q in unusual_qty if q is not None and (q < 1 or q > 100)]

    output_dir.mkdir(parents=True, exist_ok=True)
    write_summary(output_dir / "brightcart_region_summary.csv", [{k:v for k,v in r.items() if not k.startswith("_")} for r in regions], "region")
    write_summary(output_dir / "brightcart_product_summary.csv", [{k:v for k,v in r.items() if not k.startswith("_")} for r in products], "product")

    def table(rows, field, limit=None):
        shown = rows[:limit] if limit else rows
        lines = [f"| {field.title()} | Orders | Completed | Returned | Revenue | Revenue share | Return rate* |",
                 "|---|---:|---:|---:|---:|---:|---:|"]
        for r in shown:
            lines.append(f"| {r[field]} | {r['orders']} | {r['completed_orders']} | {r['returned_orders']} | "
                         f"{money(r['_revenue'])} | {pct(Decimal(r['revenue_share_pct']))} | "
                         f"{pct(r['_return_rate'])} ({r['_eligible']} orders) |")
        return "\n".join(lines)

    top_region = regions[0] if regions else None
    top_product = products[0] if products else None
    highest_returns = max((r for r in products if r["_eligible"] >= 5),
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
    if highest_returns:
        report.append(f"3. **{highest_returns['product']} had the highest product return rate among products with at least five completed/returned orders**: "
                      f"{pct(highest_returns['_return_rate'])} ({highest_returns['returned_orders']} returned of {highest_returns['_eligible']} completed or returned orders). "
                      "Use this as a review signal, especially where the denominator is small.")
    else:
        report.append("3. No product had at least five completed/returned orders, so product return-rate comparisons are too thin to rank reliably.")
    report += ["", "## Regional results", "", table(regions, "region"), "",
               "## Product results (top 5 by completed revenue)", "", table(products, "product", 5), "",
               "*Return rate = Returned / (Completed + Returned); Cancelled orders are excluded. Revenue includes only Completed rows with parseable quantity, unit price, and discount.*", "",
               "## Recommendation", ""]
    if top_region and top_product:
        report.append(f"Prioritize inventory and campaign review for **{top_region['region']}**, led by **{top_product['product']}** nationally. "
                      "Before expanding spend, check the product and region return rates and confirm inventory availability; investigate any elevated return signal in the tables.")
    else:
        report.append("Review the regional and product summaries before setting next-quarter priorities; the source does not provide enough valid H1 revenue data for a supported ranking.")
    report += ["", "## Data cautions", "",
               f"- {len(all_rows)} cleaned rows were read; {len(h1)} fall in H1 2025. {invalid_dates} rows had dates that could not be parsed and were excluded from date-based analysis.",
               f"- {missing_customers} H1 rows have no customer ID ({completed_missing_customer} are Completed), limiting customer-level follow-up.",
               f"- {missing_revenue_inputs} Completed H1 orders lack parseable quantity, price, or discount and are excluded from revenue; {revenue_inputs_missing} counted during revenue calculation.",
               f"- {len(unusual_qty)} H1 rows have quantity below 1 or above 100. These values were retained and included where Completed and parseable, so validate them before acting on revenue rankings.",
               f"- There are {status_counts['Returned']} Returned orders and {status_counts['Cancelled']} Cancelled orders among {len(h1)} H1 rows. Overall return rate is {pct(overall_return_rate)} across {return_denominator} Completed or Returned orders.",
               "- Duplicate order IDs were merged by the cleaning script. Blank fields were filled from duplicate rows; conflicts, if any, use the first row's value and are documented in the cleaning audit.",
               "", "## Reproducible outputs", "",
               "This script also writes `brightcart_region_summary.csv` and `brightcart_product_summary.csv` beside this report.", ""]
    report_path = output_dir / "brightcart_findings.md"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"H1 rows: {len(h1)}; completed revenue: {money(total_revenue)}")
    print(f"Report: {report_path}")
    print(f"Region table: {output_dir / 'brightcart_region_summary.csv'}")
    print(f"Product table: {output_dir / 'brightcart_product_summary.csv'}")

if __name__ == "__main__":
    main()
