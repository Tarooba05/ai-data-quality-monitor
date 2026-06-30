# Olist Data Quality Findings — Day 1

## orders table (99,441 rows)
- No nulls in: order_id, customer_id, order_status, order_purchase_timestamp, order_estimated_delivery_date
- order_approved_at: 0.16% nulls
- order_delivered_carrier_date: 1.79% nulls
- order_delivered_customer_date: 2.98% nulls
  → likely orders that were cancelled or not yet delivered, not necessarily errors — needs cross-check against order_status
- order_id: no duplicates, 0 fully duplicate rows
- order_purchase_timestamp range: 2016-09-19 to 2018-10-17 (no future-dated or impossible values)

## order_items table (112,650 rows)
- No nulls in any column
- order_id repeats as expected (13,984 duplicates) — normal, since one order can have multiple items
- (order_id, order_item_id) combination: 0 duplicates — confirms this is the correct unique key (grain) for this table
- price: no negative or zero values found
- freight_value: no negative values found
- price outliers: top 5 range from ~4,690 to ~6,735 — high but plausible for premium products, not obviously erroneous
- price low end: minimum is 0.85, several items priced under 1.50 — worth flagging as a potential anomaly category (unusually low price relative to freight cost)
- shipping_limit_date range: 2016-09-19 to 2020-04-09 — max date is suspicious, extends ~1.5 years past the latest order_purchase_timestamp (2018-10-17), needs investigation

## customers table (99,441 rows)
- No nulls in any column
- customer_id: no duplicates (correct, one row per customer record)
- customer_zip_code_prefix: range 1003–99990, consistent with Brazilian postal code format
- customer_state: 27 unique values, all valid Brazilian state abbreviations, no typos or inconsistent formatting found

## Ideas for anomaly checks (Day 2)
- Null spike detection on delivery date fields (threshold-based, compare daily/weekly % against historical baseline)
- Duplicate detection on (order_id, order_item_id) composite key
- Price outlier detection using IQR or z-score on order_items.price
- Low-price anomaly flag (price disproportionately low vs freight_value)
- Date range / freshness check — flag shipping_limit_date values that fall outside the expected order timeline (the 2020-04-09 max needs investigation first)
- Schema/format validation on customer_state against the known list of 27 valid Brazilian state codes

# Day 2 — shipping_limit_date investigation
- Order c2bb89b5c1dd978d507284be78a04cb2: purchased 2017-05-23, delivered 2017-06-09
- shipping_limit_date for this order's items: 2020-04-09 (isolated to this one order)
- Conclusion: confirmed data entry error — shipping_limit_date logically must precede delivery,but here it's ~3 years AFTER delivery. This is a referential/ logical anomaly, not a real event.
- Good candidate for a "date logic" check on Day 2: shipping_limit_date should never exceed order_delivered_customer_date or order_estimated_delivery_date

