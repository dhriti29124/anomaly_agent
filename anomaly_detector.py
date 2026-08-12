import pandas as pd
import numpy as np


def detect_anomalies_weekday_aware(daily_df: pd.DataFrame, metric: str, window: int = 8, z_threshold: float = 2.5) -> pd.DataFrame:
    """Flag anomalous days by comparing each day only to the same weekday in recent weeks.

    Uses shift(1) before rolling so that today's own value is never included
    in its own baseline — otherwise a big outlier drags its own comparison
    average toward itself and can hide its own anomaly.
    """
    df = daily_df.copy()
    df["DayOfWeek"] = df["Date"].dt.day_name()
    df = df.sort_values("Date")

    df[f"{metric}_zscore"] = np.nan

    for day_name, group in df.groupby("DayOfWeek"):
        group = group.sort_values("Date")
        shifted = group[metric].shift(1)  # exclude today from its own baseline
        rolling_mean = shifted.rolling(window, min_periods=3).mean()
        rolling_std = shifted.rolling(window, min_periods=3).std()
        z = (group[metric] - rolling_mean) / rolling_std
        df.loc[group.index, f"{metric}_zscore"] = z

    df[f"{metric}_anomaly"] = df[f"{metric}_zscore"].abs() >= z_threshold
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def detect_anomalies_all_metrics(daily_df: pd.DataFrame, metrics: list, window: int = 8, z_threshold: float = 2.5) -> pd.DataFrame:
    """Run weekday-aware anomaly detection across multiple metrics."""
    result = daily_df.copy()
    result["DayOfWeek"] = result["Date"].dt.day_name()

    for metric in metrics:
        metric_result = detect_anomalies_weekday_aware(daily_df, metric, window=window, z_threshold=z_threshold)
        result[f"{metric}_zscore"] = metric_result[f"{metric}_zscore"]
        result[f"{metric}_anomaly"] = metric_result[f"{metric}_anomaly"]

    result["AnyAnomaly"] = result[[f"{m}_anomaly" for m in metrics]].any(axis=1)
    return result


if __name__ == "__main__":
    from data_loader import load_raw_data, categorize_invoices, clean_sales_data, aggregate_to_daily

    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    sales_df = clean_sales_data(df)
    daily_df = aggregate_to_daily(sales_df)

    result = detect_anomalies_all_metrics(daily_df, ["Revenue", "Orders", "Quantity"])

    flagged = result[result["AnyAnomaly"]]
    print(f"Flagged {len(flagged)} days out of {len(result)} (any metric)")
    print()
    cols = ["Date", "DayOfWeek", "Revenue_anomaly", "Orders_anomaly", "Quantity_anomaly"]
    print(flagged[cols])