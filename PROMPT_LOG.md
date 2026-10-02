# Prompt Log

**AI tool:** OpenAI Codex
**Project:** Track 3 — BrightCart data cleaning and analysis

The following are the substantive prompts used during this work, in order. Follow-up prompts changed or extended the requested work; generated files were rerun after those changes.

1. “clean the data in brightcart orders to make it completely uniform by producing a python script that can be repeated to clean it every time, audit the changes that you make”
2. “in the script, as opposed to just makig banks that have all of the messy data and brute force correct it, create algorithms such as for lower case making everything lower() then correcting capitalization accordingly so it works for all solutions”
3. “import python autocorrect library to make misspelling corrections more reliable instead of brute forcing for status aliases”
4. “create a deduplication portion of the cleaning script, if there are multiple entries with the same order ID, combine them to fill as many fields as possible”
5. “make sure discount is an integer and unit price goes to 3 decimals”
6. “revert to 2 decimals for unit price”
7. “now using the data, create a python script to make inferences about the data from these questions

   **Which regions and products drove our results in the first half of the year,
   and where should we focus our attention next quarter?**
   Also flag anything in the data that leadership should be cautious about.”
8. “be sure to note about missing customer ID's in the data and if it was still considered for the business insights”
9. “flag negative quantities and exclude them from insights, additionally flag extremely large data (anything greater than 10 units at a time) and create 2 separate tables for region and product summary including and excluding unusually large orders in case they were actually intentional. Update the findings.md to reflect these changes”
10. “remove deduplication from customer ID but allow grouping by customer”
11. “could the unusually large quantities be a cleaning error? what records are contributing to this”

## Process notes

- The cleaning script preserves the raw CSV and writes a cleaned CSV and row-level audit.
- Normalization, deduplication, and numeric-formatting requests were incorporated into the repeatable cleaning script; the cleaned data and audit were regenerated after changes.
- The analysis script applies the H1 2025 revenue rule, excludes negative quantities, compares summaries with and without orders above 10 units, and groups known customer IDs without merging their orders.
- Missing customer IDs remain in regional and product analysis when other required fields are available, but cannot support customer-level grouping.
- The unusually large quantities were found in the raw data and retained for a sensitivity comparison pending verification.
