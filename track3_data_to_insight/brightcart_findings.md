# BrightCart H1 2025: Results and focus

Source: `brightcart_orders_cleaned.csv`. Analysis window: January 1–June 30, 2025.
Revenue = quantity × unit price × (1 − discount / 100), for Completed orders only.

## Findings

1. **Southeast led regional revenue**, with $55,904.95 (70.8% of total completed revenue) from 94 completed orders.
2. **Lumen Desk Lamp was the top product by revenue**, generating $36,765.74 (46.6% of total) from 32 completed orders.
**Sensitivity check:** excluding orders above 10 units, **Northeast** leads regional revenue ($9,248.82) and **Pulse Smartwatch** leads product revenue ($10,556.95).
3. **Zephyr Headphones had the highest product return rate among products with at least five completed/returned orders**: 33.3% (23 returned of 69 completed or returned orders). Use this as a review signal, especially where the denominator is small.

## Regional summary

| Region | Orders incl. >10 | Completed incl. >10 | Revenue incl. >10 | Share incl. >10 | Orders excl. >10 | Completed excl. >10 | Revenue excl. >10 | Share excl. >10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Southeast | 118 | 94 | $55,904.95 | 70.8% | 116 | 92 | $8,204.19 | 26.2% |
| Northeast | 109 | 89 | $9,248.82 | 11.7% | 109 | 89 | $9,248.82 | 29.6% |
| West | 108 | 84 | $8,017.29 | 10.2% | 108 | 84 | $8,017.29 | 25.6% |
| Midwest | 84 | 63 | $5,812.84 | 7.4% | 84 | 63 | $5,812.84 | 18.6% |

## Product summary

| Product | Orders incl. >10 | Completed incl. >10 | Revenue incl. >10 | Share incl. >10 | Orders excl. >10 | Completed excl. >10 | Revenue excl. >10 | Share excl. >10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Lumen Desk Lamp | 39 | 32 | $36,765.74 | 46.6% | 38 | 31 | $1,810.73 | 5.8% |
| Laptop Sleeve | 49 | 41 | $14,833.05 | 18.8% | 48 | 40 | $2,087.30 | 6.7% |
| Pulse Smartwatch | 38 | 31 | $10,556.95 | 13.4% | 38 | 31 | $10,556.95 | 33.8% |
| Zephyr Headphones | 78 | 46 | $6,033.83 | 7.6% | 78 | 46 | $6,033.83 | 19.3% |
| Brewmaster Coffee Maker | 45 | 37 | $4,487.20 | 5.7% | 45 | 37 | $4,487.20 | 14.3% |
| Nova Webcam | 33 | 27 | $2,975.00 | 3.8% | 33 | 27 | $2,975.00 | 9.5% |
| FlexBand Set | 41 | 37 | $1,234.51 | 1.6% | 41 | 37 | $1,234.51 | 4.0% |
| Trail Water Bottle | 45 | 38 | $1,120.28 | 1.4% | 45 | 38 | $1,120.28 | 3.6% |
| USB-C Cable 3-pack | 51 | 41 | $977.35 | 1.2% | 51 | 41 | $977.35 | 3.1% |

## Customer summary (top 10 by completed revenue)

| Customer ID | Orders incl. >10 | Revenue incl. >10 | Orders excl. >10 | Revenue excl. >10 |
|---|---:|---:|---:|---:|
| C1111 | 1 | $34,955.01 | 0 | $0.00 |
| C1016 | 2 | $12,758.49 | 1 | $12.74 |
| C1138 | 3 | $1,313.40 | 3 | $1,313.40 |
| C1089 | 3 | $902.97 | 3 | $902.97 |
| C1118 | 4 | $761.49 | 4 | $761.49 |
| C1180 | 3 | $624.62 | 3 | $624.62 |
| C1162 | 5 | $620.49 | 5 | $620.49 |
| C1105 | 5 | $528.01 | 5 | $528.01 |
| C1164 | 5 | $520.98 | 5 | $520.98 |
| C1190 | 2 | $516.20 | 2 | $516.20 |

Orders with negative quantities are excluded from all summaries. `Incl. >10` includes orders with more than 10 units; `excl. >10` removes them. Revenue includes only Completed orders with parseable inputs. Return rate = Returned / (Completed + Returned); Cancelled orders are excluded.

## Recommendation

Verify the >10-unit orders, which account for $47,700.76 in completed revenue. The all-order leaders are **Southeast** and **Lumen Desk Lamp**, while the leaders excluding >10-unit orders are **Northeast** and **Pulse Smartwatch**. Use both scenarios in planning until the quantities are confirmed. Review the high Zephyr Headphones return rate before increasing its promotion.

## Data cautions

- 420 cleaned rows were read; 420 fall in H1 2025. 0 rows had dates that could not be parsed and were excluded from date-based analysis.
- 1 H1 row(s) have negative quantities and were excluded from all insight calculations: ORD-1101 (-3 units).
- 2 H1 row(s) have quantities greater than 10 and are shown in both scenarios. Together, their Completed orders contribute $47,700.76 when included: ORD-1205 (999 × Lumen Desk Lamp, Southeast), ORD-1165 (500 × Laptop Sleeve, Southeast).
- 20 H1 nonnegative-quantity rows have no customer ID (16 are Completed). These rows are included in regional/product, revenue, and return insights whenever the other required fields are present, but are not combined into a single customer group. Customer IDs group orders for the customer summary; orders remain separate transactions.
- 22 Completed H1 orders lack parseable quantity, price, or discount and are excluded from revenue; 22 counted during revenue calculation.
- There are 38 Returned orders and 22 Cancelled orders among 419 included H1 rows. Overall return rate is 10.3% across 368 Completed or Returned orders.
- Duplicate order IDs were merged by the cleaning script. Blank fields were filled from duplicate rows; conflicts, if any, use the first row's value and are documented in the cleaning audit.

## Reproducible outputs

This script also writes region and product summaries that compare results with and without >10-unit orders, plus `brightcart_customer_summary.csv` with orders grouped by known customer ID. Customer IDs are grouping keys, not deduplication keys.
