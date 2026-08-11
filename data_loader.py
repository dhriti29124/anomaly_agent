# for this we will find the customer id with C and A and price === 0 
import pandas as pd
import numpy as np


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CSV and parse the date column."""
    df = pd.read_csv(path)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


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