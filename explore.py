import pandas as pd
# load the data 

def load_data(path: str) -> pd.DataFrame:
    """Load the raw CSV and parse the date column."""
    df = pd.read_csv(path)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"]) #convert invoice date from the text format to an actual datetime type
    return df


#shape and structure 
def check_structure(df: pd.DataFrame) -> None:
    """Print basic shape, columns, and data types."""
    print("SHAPE:", df.shape)
    print()
    print("COLUMNS:", list(df.columns))
    print()
    print("DTYPES:")
    print(df.dtypes)


# missing values
def check_missing_values(df: pd.DataFrame) -> None:
    """Print how many missing values each column has."""
    missing = df.isna().sum() #showing percentage matters more than raw count when you're deciding
    missing_pct = (missing / len(df) * 100).round(1)
    print("MISSING VALUES:")
    for col in df.columns:
        print(f"  {col}: {missing[col]} ({missing_pct[col]}%)")


# date range 
def check_date_range(df: pd.DataFrame) -> None:
    """Print the earliest and latest transaction dates."""
    print("DATE RANGE:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())

# data quality issues

def check_quality_issues(df: pd.DataFrame) -> None:
    """Flag known data quality issues: cancellations, bad prices, negative quantities."""
    negative_qty = (df["Quantity"] < 0).sum()
    cancellations = df["Invoice"].astype(str).str.startswith("C").sum()
    zero_price = (df["Price"] == 0).sum()
    negative_price = (df["Price"] < 0).sum()

    print("QUALITY ISSUES:")
    print(f"  Negative quantity rows: {negative_qty}")
    print(f"  Cancelled invoices (start with 'C'): {cancellations}")
    print(f"  Zero price rows: {zero_price}")
    print(f"  Negative price rows: {negative_price}")
    print()
    print("SAMPLE OF NEGATIVE QUANTITY ROWS:")
    print(df[df["Quantity"] < 0].head(3))
    print()
    print("SAMPLE OF NEGATIVE PRICE ROWS:")
    print(df[df["Price"] < 0].head(5))
    print()
    print("SAMPLE OF ZERO PRICE ROWS:")
    print(df[df["Price"] == 0].head(5))


# trying everything together 
def main():
    df = load_data("online_retail_II.csv")
    check_structure(df)
    print("\n" + "=" * 50 + "\n")
    check_missing_values(df)
    print("\n" + "=" * 50 + "\n")
    check_date_range(df)
    print("\n" + "=" * 50 + "\n")
    check_quality_issues(df)


if __name__ == "__main__":
    main()

