import pandas as pd
import numpy as np


def detect_anomalies_weekday_aware(daily_df: pd.DataFrame, metric: str, window: int = 4, z_threshold: float = 2.0) -> pd.DataFrame:
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


if __name__ == "__main__":
    from data_loader import load_raw_data, categorize_invoices, clean_sales_data, aggregate_to_daily

    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    sales_df = clean_sales_data(df)
    daily_df = aggregate_to_daily(sales_df)

    print("--- Weekday-aware detection ---")
    result = detect_anomalies_weekday_aware(daily_df, "Revenue", window=8)
    flagged = result[result["Revenue_anomaly"]]
    print(f"Flagged {len(flagged)} anomalous days out of {len(result)}")
    print(flagged[["Date", "DayOfWeek", "Revenue", "Revenue_zscore"]])


    early_cutoff = pd.Timestamp("2010-02-01")
early_flagged = flagged[flagged["Date"] < early_cutoff]
later_flagged = flagged[flagged["Date"] >= early_cutoff]
print(f"Flagged in burn-in period (before Feb 2010): {len(early_flagged)}")
print(f"Flagged after burn-in period: {len(later_flagged)}")
print(f"Later-period flag rate: {len(later_flagged) / len(result[result['Date'] >= early_cutoff]) * 100:.1f}%")