# AI Anomaly Agent: Python based Data analytics Automation Project 


A tool that reads real e-commerce transaction data, cleans it, detects
statistically unusual days in daily business metrics, and generates a
plain-English alert explaining what changed and why it might matter.

## What it does

1. Loads raw transaction data (Online Retail II, UCI/Kaggle — ~1M rows,
   2009–2011, real UK online retailer)
2. Classifies every row as a real sale, a cancellation, a bad-debt
   adjustment, or a manual stock correction and filters to real sales only
3. Aggregates transactions into daily metrics: Revenue, Orders, Quantity
4. Detects anomalies using a weekday-aware rolling z-score (compares each
   day only to the same weekday in recent weeks, so Sundays aren't
   unfairly compared to Tuesdays)
5. Generates a plain-English summary per anomaly, based on *which*
   metrics moved — e.g. revenue up alone suggests a pricing change;
   orders up without revenue suggests discounting
6. Builds and sends (or previews) an HTML email alert

## Files

| File | Purpose |
|---|---|
| `data_loader.py` | Load raw CSV, classify rows, filter to sales, aggregate to daily |
| `anomaly_detector.py` | Weekday-aware z-score detection + summary generation |
| `email_alert.py` | Build HTML email, send via SMTP or preview locally |
| `main.py` | Runs the full pipeline end to end |
| `explore.py` | Standalone script used to investigate the raw data before building the pipeline |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas openpyxl numpy
```

Download the dataset from [Kaggle: Online Retail II (UCI)](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
and place `online_retail_II.csv` in this folder (not committed to Git
see `.gitignore`).

## Run it

```bash
python main.py
```

Without SMTP credentials set, this writes `alert_preview.html` instead of
sending — open it in a browser to see the alert.

To send a real email, set:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=youraddress@gmail.com
SMTP_PASS=your_app_password
ALERT_FROM=youraddress@gmail.com
ALERT_TO=teammate@company.com
```

## Key decisions and what I learned

- **Real data needed real cleaning.** The dataset had three categories of
  non-sale rows I hadn't planned for going in: cancellations (`C`-prefixed
  invoices), bad-debt write-offs (`A`-prefixed, explicitly labeled
  "Adjust bad debt"), and manual stock corrections (zero-price rows with
  inventory-style descriptions). Filtering these out was necessary before
  any metric meant anything.
- **A plain rolling average falsely flagged Sundays and holidays.** The
  store has a natural weekly rhythm (lower Sunday volume, closed on bank
  holidays). Comparing each day only to the same weekday over recent
  weeks fixed this.
- **Found and fixed a real bug**: an early version let each day's value
  leak into its own baseline via `rolling()`, which let big outliers
  suppress their own anomaly score. Fixed with `shift(1)` before rolling.
- **Tuned the threshold empirically**, not by guessing — checked the
  actual flag rate against what's statistically expected (~5%) and
  adjusted window size and z-threshold until the rate was sane (~8%).

## Known limitations

- The detector flags *statistically* unusual days it doesn't judge
  whether unusual is good or bad. A growing business will keep beating
  its own rolling baseline, which shows up as frequent "anomalies" that
  are actually just growth. A human still has to read the summary and
  decide if it matters.
- No live scheduling yet this runs once per invocation. Could be
  extended with cron/Task Scheduler for a real daily "watcher."
