import pandas as pd

def detect_anomalies_single_metric(daily_df: pd.DataFrame, metric: str, window: int = 7, z_threshold: float = 2.0) -> pd.DataFrame:
    """Flag anomalous days for one metric using a rolling z-score."""
    df = daily_df.copy()

    rolling_mean = df[metric].rolling(window, min_periods=3).mean()
    rolling_std = df[metric].rolling(window, min_periods=3).std()

    df[f"{metric}_zscore"] = (df[metric] - rolling_mean) / rolling_std
    df[f"{metric}_anomaly"] = df[f"{metric}_zscore"].abs() >= z_threshold

    return df


if __name__ == "__main__":
    from data_loader import load_raw_data, categorize_invoices, clean_sales_data, aggregate_to_daily

    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    sales_df = clean_sales_data(df)
    daily_df = aggregate_to_daily(sales_df)

    result = detect_anomalies_single_metric(daily_df, "Revenue")

    flagged = result[result["Revenue_anomaly"]]
    print(f"Flagged {len(flagged)} anomalous days out of {len(result)}")
    print()
    print(flagged[["Date", "Revenue", "Revenue_zscore"]])