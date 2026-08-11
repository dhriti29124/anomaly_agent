# for this we will find the customer id with C and A and price === 0 
import pandas as pd
import numpy as np


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CSV and parse the date column."""
    df = pd.read_csv(path)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only real sales, and compute a Revenue column (Quantity x Price)."""
    sales_df = df[df["RowType"] == "sale"].copy()
    sales_df["Revenue"] = sales_df["Quantity"] * sales_df["Price"]
    return sales_df

def aggregate_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Group sales data into one row per day with daily totals."""
    df["Date"] = df["InvoiceDate"].dt.date

    daily_df = df.groupby("Date").agg(
        Revenue=("Revenue", "sum"),
        Orders=("Invoice", "nunique"),
        Quantity=("Quantity", "sum"),
    ).reset_index()

    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    return daily_df


def categorize_invoices(df: pd.DataFrame) -> pd.DataFrame:
    is_cancellation = df["Invoice"].astype(str).str.startswith("C")
    is_adjustment = df["Invoice"].astype(str).str.startswith("A")
    is_correction = df["Price"] == 0

    conditions = [is_cancellation, is_adjustment, is_correction]
    choices = ["cancellation", "adjustment", "correction"]

    df["RowType"] = np.select(conditions, choices, default="sale")
    return df


if __name__ == "__main__":
    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    print(df["RowType"].value_counts())

    sales_df = clean_sales_data(df)
    print()
    print("Sales rows:", len(sales_df))

    daily_df = aggregate_to_daily(sales_df)
    print()
    print("Daily rows:", len(daily_df))
    print(daily_df.head(10))
    print()
    print(daily_df.describe())



