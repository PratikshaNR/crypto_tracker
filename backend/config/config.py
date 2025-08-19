import os
import sqlite3

# -----------------------------
# Project Paths
# -----------------------------

# Get path to current config.py
config_dir = os.path.dirname(os.path.abspath(__file__))  # backend/config

# Navigate up to project root
project_root = os.path.abspath(os.path.join(config_dir, "..", ".."))

# Data directory
data_dir = os.path.join(project_root, "Data")

# Database path (centralized for all files)
DB_PATH = os.path.join(data_dir, "database.db")

# Password file path
password_file_path = os.path.join(data_dir, "app_password.txt")

# Chart/Trend image file path
TREND_IMAGE_PATH = os.path.join(data_dir, "btc_trend.png")

# JSON data file path
BTC_JSON_PATH = os.path.join(data_dir, "btc_price.json")

# -----------------------------
# Read Gmail App Password
# -----------------------------
try:
    with open(password_file_path, "r") as file:
        PASSWORD = file.read().strip()
except FileNotFoundError:
    raise FileNotFoundError(f"Password file not found at: {password_file_path}")

# -----------------------------
# Alert Thresholds
# -----------------------------
ALERT_THRESHOLDS = {
    'usd': 60000,
    'inr': 5000000,
    'eur': 55000,
    'jpy': 9000000
}

# -----------------------------
# Email Settings
# -----------------------------
EMAIL_SETTINGS = {
    'sender': 'pratikshanayak.nr@gmail.com',
    'password': PASSWORD,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
    # Note: 'receiver' is removed because recipients are dynamically fetched from DB
}

# -----------------------------
# DB Connection Helper
# -----------------------------
def get_db_connection():
    """Return a SQLite connection using the centralized DB_PATH"""
    return sqlite3.connect(DB_PATH)
