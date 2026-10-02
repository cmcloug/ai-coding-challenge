# Track 3: Messy Data to Insight

## The situation

You have just joined the analytics team at **BrightCart**, an online retailer that
sells electronics, home goods, fitness gear, and accessories across four U.S.
regions. Leadership is planning next quarter and wants to know what happened in
the first half of the year.

An export of order data (January to June 2025) has landed in your lap. It was
pulled from several systems and **it is not clean**.

File: `brightcart_orders.csv`

## The business question

> **Which regions and products drove our results in the first half of the year,
> and where should we focus our attention next quarter?**
> Also flag anything in the data that leadership should be cautious about.

## What to deliver

1. **Cleaned dataset or reproducible script.** Save a cleaned CSV, or the code
   that cleans it. Python (standard library, or anything already installed on
   your machine), Excel, or Google Sheets are all fine.
2. **Data quality log.** A short list of every problem you found, how you handled
   it, and why. If you made an assumption, say so.
3. **Two to three findings.** Each finding needs a clear statement, the numbers
   that support it, and a simple chart or table.
4. **One recommendation** for next quarter, tied to your findings.
5. **Prompt log and reflection** (see the main instruction sheet).

## Data dictionary

| Column | Meaning |
|---|---|
| order_id | Unique order identifier |
| customer_id | Customer identifier |
| order_date | Date the order was placed |
| region | Sales region (Northeast, Southeast, Midwest, West) |
| product | Product name |
| category | Product category |
| quantity | Units ordered |
| unit_price | Price per unit in USD |
| discount_pct | Discount applied, as a percent (10 means 10% off) |
| status | Completed, Returned, or Cancelled |
| sales_rep | Sales representative |

## Business rules

- **Revenue** = quantity x unit_price x (1 - discount_pct / 100).
- Only **Completed** orders count toward revenue.
- Returned and Cancelled orders do not count as revenue, but a high return rate
  is still worth knowing about.

## Tips

- Look at the raw file before you touch it. Open it, scroll it, and see what is
  there.
- Decide what "clean" means *before* you ask an AI to clean it, and check what it
  actually did to your data. Count rows before and after.
- There is no single correct answer. A well-explained judgment call beats a
  silent one.
