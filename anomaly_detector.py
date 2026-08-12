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


def generate_summary_for_day(row: pd.Series, metrics: list) -> str:
    """Turn one flagged day's row into a plain-English sentence."""
    date_str = row["Date"].strftime("%B %d, %Y")
    flagged_metrics = [m for m in metrics if row[f"{m}_anomaly"]]

    def direction(metric):
        return "increased" if row[f"{metric}_zscore"] > 0 else "decreased"

    # Case 1: all metrics flagged together — broad, simple movement
    if len(flagged_metrics) == len(metrics):
        directions = {direction(m) for m in flagged_metrics}
        if len(directions) == 1:
            word = directions.pop()
            return f"On {date_str}, revenue, orders, and items sold all {word} together — a broad, across-the-board {word.replace('increased', 'spike').replace('decreased', 'drop')}."
        else:
            return f"On {date_str}, all key metrics moved unusually, but in mixed directions — worth a closer look."

    # Case 2: Revenue flagged alone — pricing/mix story
    if "Revenue" in flagged_metrics and "Orders" not in flagged_metrics and "Quantity" not in flagged_metrics:
        return (f"On {date_str}, revenue {direction('Revenue')} sharply while order volume and items sold stayed normal. "
                f"This suggests a change in pricing or product mix rather than a change in customer traffic.")

    # Case 3: Orders/Quantity flagged without Revenue — volume without matching revenue
    if "Revenue" not in flagged_metrics and ("Orders" in flagged_metrics or "Quantity" in flagged_metrics):
        return (f"On {date_str}, order activity {direction(flagged_metrics[0])} sharply but revenue stayed normal. "
                f"This suggests more orders at lower value — worth checking for discounting or a shift toward cheaper items.")

    # Case 3.5: Revenue + Quantity together, no Orders — existing customers buying more per order
    if "Revenue" in flagged_metrics and "Quantity" in flagged_metrics and "Orders" not in flagged_metrics:
        return (f"On {date_str}, revenue and items sold both {direction('Revenue')} together while the number of orders stayed normal. "
                f"This suggests existing customers are buying more per order, rather than more customers showing up.")

    # Case 4: fallback — some other partial combination
    parts = [f"{m} {direction(m)}" for m in flagged_metrics]
    return f"On {date_str}: " + ", ".join(parts) + "."


if __name__ == "__main__":
    from data_loader import load_raw_data, categorize_invoices, clean_sales_data, aggregate_to_daily

    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    sales_df = clean_sales_data(df)
    daily_df = aggregate_to_daily(sales_df)

    metrics = ["Revenue", "Orders", "Quantity"]
    result = detect_anomalies_all_metrics(daily_df, metrics)

    flagged = result[result["AnyAnomaly"]]
    print(f"Flagged {len(flagged)} days out of {len(result)} (any metric)\n")

    for _, row in flagged.head(15).iterrows():
        print(generate_summary_for_day(row, metrics))
        print()