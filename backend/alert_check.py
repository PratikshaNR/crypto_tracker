# backend/alert_check.py
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from backend.config.config import ALERT_THRESHOLDS, EMAIL_SETTINGS, DB_PATH
from backend.trend_analysis import generate_trend
import random

def send_email_alert_to_users(currency, price, chart_html, png_path=None):
    """Send BTC alert in storytelling style to all registered users."""
    currency = currency.upper()
    messages = [
        f"In today’s crypto saga, Bitcoin ({currency}) has just moved to {price:.2f}. Traders everywhere are watching closely!",
        f"The crypto waves are stirring! BTC ({currency}) currently sits at {price:.2f}. What a thrilling ride!",
        f"A new twist in the Bitcoin story: {currency} {price:.2f}. The market buzzes with anticipation!",
        f"Attention crypto enthusiasts! Bitcoin ({currency}) reached {price:.2f}. The next chapter unfolds.",
        f"The tale of Bitcoin continues: BTC ({currency}) stands at {price:.2f}. Stay tuned for the next move!"
    ]
    message_text = random.choice(messages)

    html_body = f"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          .chart-container {{ width: 100%; max-width: 600px; margin: auto; }}
          p {{ font-size: 14px; line-height: 1.4; }}
        </style>
      </head>
      <body>
        <p>{message_text}</p>
        <div class="chart-container">
            {chart_html if chart_html else "<p>(Chart not available)</p>"}
        </div>
        <p>Stay tuned for more updates!<br>Your Crypto Tracker</p>
      </body>
    </html>
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE email IS NOT NULL")
    users = cursor.fetchall()
    conn.close()

    recipients = [email[0] for email in users if email[0]]
    if not recipients:
        print("No registered users to send alert.")
        return

    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"🚀 BTC Update: {currency} Price Alert!"
    msg['From'] = EMAIL_SETTINGS["sender"]
    msg['To'] = ", ".join(recipients)

    msg.attach(MIMEText(message_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    if png_path and os.path.exists(png_path):
        with open(png_path, 'rb') as f:
            img = MIMEBase('application', 'octet-stream')
            img.set_payload(f.read())
            encoders.encode_base64(img)
            img.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(png_path)}"')
            msg.attach(img)

    try:
        server = smtplib.SMTP(EMAIL_SETTINGS["smtp_server"], EMAIL_SETTINGS["smtp_port"])
        server.set_debuglevel(1)
        server.starttls()
        server.login(EMAIL_SETTINGS["sender"], EMAIL_SETTINGS["password"])
        server.sendmail(EMAIL_SETTINGS["sender"], recipients, msg.as_string())
        print(f"Alert sent to {len(recipients)} users.")
    except Exception as e:
        print(f"Failed to send alert: {e}")
    finally:
        server.quit()


def run(currency="usd", timeframe="day"):
    """Check BTC price against threshold and send alert if exceeded."""
    currency = currency.upper()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM btc_price WHERE currency = ? ORDER BY id DESC LIMIT 1", (currency,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("No data found.")
        return "No alert"

    current_price = result[0]
    threshold = ALERT_THRESHOLDS.get(currency.lower())

    if threshold and current_price > threshold:
        chart_html, html_path, png_path = generate_trend(currency, timeframe)
        send_email_alert_to_users(currency, current_price, chart_html, png_path)
        return f"Alert sent! BTC {currency} is {current_price}"

    return f"No alert. BTC {currency} is {current_price}"
