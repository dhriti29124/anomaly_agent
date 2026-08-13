from data_loader import load_raw_data, categorize_invoices, clean_sales_data, aggregate_to_daily
from anomaly_detector import detect_anomalies_all_metrics, generate_summary_for_day
from email_alert import build_email_html, send_alert


def main():
    df = load_raw_data("online_retail_II.csv")
    df = categorize_invoices(df)
    sales_df = clean_sales_data(df)
    daily_df = aggregate_to_daily(sales_df)

    metrics = ["Revenue", "Orders", "Quantity"]
    result = detect_anomalies_all_metrics(daily_df, metrics)
    flagged = result[result["AnyAnomaly"]]

    print(f"Flagged {len(flagged)} days out of {len(result)}")

    summaries = [generate_summary_for_day(row, metrics) for _, row in flagged.iterrows()]

    html = build_email_html(summaries, len(flagged), len(result))
    send_alert(html)


if __name__ == "__main__":
    main()