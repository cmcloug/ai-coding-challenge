# BrightCart H1 2025: Results and focus

Source: `brightcart_orders_cleaned.csv`. Analysis window: January 1–June 30, 2025.
Revenue = quantity × unit price × (1 − discount / 100), for Completed orders only.

## Findings

1. **Southeast led regional revenue**, with $55,904.95 (70.8% of total completed revenue) from 94 completed orders.
2. **Lumen Desk Lamp was the top product by revenue**, generating $36,765.74 (46.6% of total) from 32 completed orders.
**Sensitivity check:** excluding quantities below 1 or above 100, **Northeast** leads regional revenue ($9,248.82) and **Pulse Smartwatch** leads product revenue ($10,556.95). Treat the all-row leaders above as provisional until the flagged quantities are verified.
3. **Zephyr Headphones had the highest product return rate among products with at least five completed/returned orders**: 33.3% (23 returned of 69 completed or returned orders). Use this as a review signal, especially where the denominator is small.

## Regional results

| Region | Orders | Completed | Returned | Revenue | Revenue share | Return rate* |
|---|---:|---:|---:|---:|---:|---:|
| Southeast | 118 | 94 | 9 | $55,904.95 | 70.8% | 8.7% (103 orders) |
| Northeast | 110 | 90 | 9 | $9,248.82 | 11.7% | 9.1% (99 orders) |
| West | 108 | 84 | 9 | $8,017.29 | 10.2% | 9.7% (93 orders) |
| Midwest | 84 | 63 | 11 | $5,812.84 | 7.4% | 14.9% (74 orders) |

## Product results (top 5 by completed revenue)

| Product | Orders | Completed | Returned | Revenue | Revenue share | Return rate* |
|---|---:|---:|---:|---:|---:|---:|
| Lumen Desk Lamp | 39 | 32 | 4 | $36,765.74 | 46.6% | 11.1% (36 orders) |
| Laptop Sleeve | 49 | 41 | 1 | $14,833.05 | 18.8% | 2.4% (42 orders) |
| Pulse Smartwatch | 38 | 31 | 0 | $10,556.95 | 13.4% | 0.0% (31 orders) |
| Zephyr Headphones | 78 | 46 | 23 | $6,033.83 | 7.6% | 33.3% (69 orders) |
| Brewmaster Coffee Maker | 46 | 38 | 4 | $4,487.20 | 5.7% | 9.5% (42 orders) |

*Return rate = Returned / (Completed + Returned); Cancelled orders are excluded. Revenue includes only Completed rows with parseable quantity, unit price, and discount.*

## Recommendation

First verify the unusual quantities behind $47,700.76 in completed revenue. The apparent leaders change when those records are excluded. If source records confirm them, prioritize **Southeast** and **Lumen Desk Lamp**; otherwise use the sensitivity results (Northeast region and Pulse Smartwatch product) to guide next-quarter planning. Review the high Zephyr Headphones return rate before increasing its promotion.

## Data cautions

- 420 cleaned rows were read; 420 fall in H1 2025. 0 rows had dates that could not be parsed and were excluded from date-based analysis.
- 20 H1 rows have no customer ID (16 are Completed), limiting customer-level follow-up.
- 23 Completed H1 orders lack parseable quantity, price, or discount and are excluded from revenue; 23 counted during revenue calculation.
- 3 H1 rows have quantity below 1 or above 100. Their Completed rows contribute $47,700.76 (60.4%) to reported revenue; the two largest are 999 Lumen Desk Lamps in the Southeast and 500 Laptop Sleeves in the Southeast. Values were retained, so validate these records before acting on rankings.
- There are 38 Returned orders and 22 Cancelled orders among 420 H1 rows. Overall return rate is 10.3% across 369 Completed or Returned orders.
- Duplicate order IDs were merged by the cleaning script. Blank fields were filled from duplicate rows; conflicts, if any, use the first row's value and are documented in the cleaning audit.

## Reproducible outputs

This script also writes `brightcart_region_summary.csv` and `brightcart_product_summary.csv` beside this report.
