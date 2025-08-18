# backend/fetch_and_store.py
import requests
import sqlite3
import datetime
import os
import json

def run(currencies=None):
    if currencies is None:
        currencies = ["usd", "inr", "eur", "jpy"]

    print(f"Fetching BTC prices for: {currencies}")

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": ",".join(currencies)
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to fetch data from API")
        return

    price_data = response.json().get("bitcoin", {})
    if not price_data:
        print("No price data received")
        return

    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "database.db")

    # Current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Connect to database and insert
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS btc_price (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            currency TEXT,
            timestamp TEXT
        )
    """)

    for cur in currencies:
        val = price_data.get(cur)
        if val is not None:
            cursor.execute(
                "INSERT INTO btc_price (value, currency, timestamp) VALUES (?, ?, ?)",
                (val, cur.upper(), timestamp)
            )

    conn.commit()
    conn.close()
    print("Data stored in normalized format")

    # Save JSON file (optional)
    with open(os.path.join(data_dir, "btc_price.json"), "w") as f:
        json.dump(price_data, f)
    print("JSON data saved to btc_price.json")
