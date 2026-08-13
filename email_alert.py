import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_email_html(summaries: list, flagged_count: int, total_days: int) -> str:
    """Turn a list of summary sentences into a formatted HTML email body."""
    summary_html = "".join(f"<p style='margin:8px 0;'>{s}</p>" for s in summaries)

    return f"""
    <html><body style="font-family: Arial, sans-serif; color: #222; max-width: 600px;">
      <h2>⚠️ Daily Metrics Anomaly Report</h2>
      <p style="color:#555;">{flagged_count} unusual day(s) detected out of {total_days} analyzed.</p>
      <hr>
      {summary_html}
      <hr>
      <p style="color:#888; font-size:12px;">Generated automatically by the anomaly agent.</p>
    </body></html>
    """


def send_alert(html: str, subject: str = "⚠️ Metric Anomaly Detected"):
    """Send the alert email, or write a local preview if no SMTP credentials are set."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    sender = os.environ.get("ALERT_FROM", user)
    recipient = os.environ.get("ALERT_TO")

    if not all([host, user, password, recipient]):
        with open("alert_preview.html", "w") as f:
            f.write(html)
        print("SMTP credentials not set — wrote preview to alert_preview.html")
        return

    port = int(os.environ.get("SMTP_PORT", 587))
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, [recipient], msg.as_string())

    print(f"Alert email sent to {recipient}")