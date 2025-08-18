import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from backend.config.config import ALERT_THRESHOLDS, EMAIL_SETTINGS
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  # Ensure non-GUI backend for server env
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def generate_btc_plot(currency="usd"):
    currency = currency.upper()
    conn = sqlite3.connect("Data/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, value FROM btc_price 
        WHERE currency = ? ORDER BY id DESC LIMIT 50
    """, (currency,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        print(f"No data found for {currency}")
        return None

    timestamps = [
        datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").strftime("%b-%d %H:%M")
        for row in data
    ][::-1]
    prices = [row[1] for row in data][::-1]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, prices, marker='o', linestyle='-', color='blue')
    plt.title(f"BTC Price Trend - {datetime.now().year}")
    plt.xlabel("Timestamp (Month-Day Hour:Min)")
    plt.ylabel(f"Price ({currency})")
    plt.xticks(rotation=90)

    ax = plt.gca()

    # Disable scientific notation for INR and JPY
    if currency in ['INR', 'JPY']:
        formatter = mticker.ScalarFormatter(useMathText=False)
        formatter.set_scientific(False)
        formatter.set_useOffset(False)
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(style='plain', axis='y', useOffset=False)

    plt.tight_layout()

    output_path = os.path.join("static", "btc_trend.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    return output_path


def run(currency="usd"):
    currency = currency.upper()

    conn = sqlite3.connect("Data/database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT value FROM btc_price 
            WHERE currency = ? ORDER BY id DESC LIMIT 1
        """, (currency,))
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        print(f"Error querying the database for {currency}")
        conn.close()
        return

    conn.close()

    if not result:
        print("No data found.")
        return

    current_price = result[0]
    threshold = ALERT_THRESHOLDS.get(currency.lower())

    print(f"Checking alert for {currency}... BTC price is {current_price}")

    if threshold and current_price > threshold:
        # Generate the plot and get image path
        image_path = generate_btc_plot(currency)
        send_email_alert(currency, current_price, image_path)
    else:
        print(f"No alert: BTC {currency} is {current_price}, threshold is {threshold}")


def send_email_alert(currency, price, image_path=None):
    subject = f"🚨 BTC Price Alert in {currency}"
    # Storytelling style body message without threshold mention
    body = (
        f"Hello,\n\n"
        f"The Bitcoin price in {currency} has just reached {price:.2f}.\n"
        f"This is an exciting moment to keep an eye on the market.\n\n"
        f"Attached is the latest BTC price trend chart to help you visualize the recent movements.\n\n"
        f"Best regards,\n"
        f"Your Crypto Tracker"
    )

    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SETTINGS["sender"]
    msg['To'] = EMAIL_SETTINGS["receiver"]

    # Attach the text body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the image if exists
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            img = MIMEBase('application', 'octet-stream')
            img.set_payload(f.read())
            encoders.encode_base64(img)
            img.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(image_path)}"')
            msg.attach(img)
    else:
        print("Warning: BTC trend image not found, sending email without attachment.")

    try:
        print("Sending alert email...")
        with smtplib.SMTP(EMAIL_SETTINGS["smtp_server"], EMAIL_SETTINGS["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_SETTINGS["sender"], EMAIL_SETTINGS["password"])
            server.sendmail(EMAIL_SETTINGS["sender"], EMAIL_SETTINGS["receiver"], msg.as_string())
            print(f"Alert sent to {EMAIL_SETTINGS['receiver']}")
    except Exception as e:
        print(f"Failed to send alert: {e}")
