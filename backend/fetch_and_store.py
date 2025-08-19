# backend/fetch_and_store.py
import requests
import sqlite3
import datetime
import json

from backend.config.config import DB_PATH, BTC_JSON_PATH

TABLE_NAME = "btc_price"


def get_data(currencies):
    """Fetch BTC price data from CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": ",".join(currencies)}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("bitcoin", {})
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return {}


def init_db():
    """Initialize database and create table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            currency TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(price_data, currencies, timestamp):
    """Save fetched data into SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for cur in currencies:
        val = price_data.get(cur)
        if val is not None:
            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (value, currency, timestamp) VALUES (?, ?, ?)",
                (val, cur.upper(), timestamp)
            )

    conn.commit()
    conn.close()


def save_to_json(price_data):
    """Save fetched data into JSON file."""
    with open(BTC_JSON_PATH, "w") as f:
        json.dump(price_data, f, indent=4)


def run(currencies=None):
    if currencies is None:
        currencies = ["usd", "inr", "eur", "jpy"]

    print(f"Fetching BTC prices for: {currencies}")

    price_data = get_data(currencies)
    if not price_data:
        print("No price data received")
        return

    init_db()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_to_db(price_data, currencies, timestamp)
    print("Data stored in normalized format")

    save_to_json(price_data)
    print(f"JSON data saved to {BTC_JSON_PATH}")


if __name__ == "__main__":
    run()
