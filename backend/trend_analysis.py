# backend/trend_analysis.py
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for server environments
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime
import matplotlib.ticker as mticker

def run(currency="usd"):
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
        return

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

    # ✅ Disable scientific notation for INR and JPY
    if currency in ['INR', 'JPY']:
        formatter = mticker.ScalarFormatter(useMathText=False)
        formatter.set_scientific(False)
        formatter.set_useOffset(False)  # disable offset like "+1e7"
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(style='plain', axis='y', useOffset=False)

    plt.tight_layout()

    output_path = os.path.join("static", "btc_trend.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    print(f"BTC trend chart saved to {output_path} for {currency}")
