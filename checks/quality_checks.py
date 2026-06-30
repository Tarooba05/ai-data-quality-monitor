import pandas as pd

def check_nulls(df, table_name, threshold=5.0):
    null_pct = df.isnull().mean() * 100
    flagged = null_pct[null_pct > threshold]
    
    results = []
    for column, pct in flagged.items():
        results.append({
            "table": table_name,
            "column": column,
            "check_type": "null_spike",
            "severity": "high" if pct > 20 else "medium",
            "value": round(pct, 2),
            "message": f"{column} has {pct:.2f}% null values, exceeding the {threshold}% threshold"
        })
    return results

def check_duplicates(df, table_name, subset_cols):
    dup_count = df.duplicated(subset=subset_cols).sum()
    
    results = []
    if dup_count > 0:
        results.append({
            "table": table_name,
            "column": ", ".join(subset_cols),
            "check_type": "duplicate",
            "severity": "high",
            "value": int(dup_count),
            "message": f"{dup_count} duplicate rows found based on key: {subset_cols}"
        })
    return results

def check_outliers_iqr(df, table_name, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    results = []
    if len(outliers) > 0:
        results.append({
            "table": table_name,
            "column": column,
            "check_type": "outlier",
            "severity": "medium",
            "value": len(outliers),
            "message": f"{len(outliers)} outliers found in {column} (outside range {lower_bound:.2f} to {upper_bound:.2f})"
        })
    return results

def run_all_checks(orders_df, order_items_df, customers_df):
    report = []
    
    report += check_nulls(orders_df, "orders")
    report += check_nulls(order_items_df, "order_items")
    report += check_nulls(customers_df, "customers")
    
    report += check_duplicates(orders_df, "orders", ["order_id"])
    report += check_duplicates(order_items_df, "order_items", ["order_id", "order_item_id"])
    report += check_duplicates(customers_df, "customers", ["customer_id"])
    
    report += check_outliers_iqr(order_items_df, "order_items", "price")
    
    return report