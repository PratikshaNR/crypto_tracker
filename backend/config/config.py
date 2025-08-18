import os

# Get path to current config.py
config_dir = os.path.dirname(os.path.abspath(__file__))  # backend/config

# Navigate up to project root, then to Data/
project_root = os.path.abspath(os.path.join(config_dir, "..", ".."))
data_dir = os.path.join(project_root, "Data")

# Path to the password file
password_file_path = os.path.join(data_dir, "app_password.txt")

# Optional: Log to verify
print("Looking for password file at:", password_file_path)

# Read the Gmail app password
with open(password_file_path, "r") as file:
    password = file.read().strip()

# Constants
ALERT_THRESHOLDS = {
    'usd': 60000,
    'inr': 5000000,
    'eur': 55000,
    'jpy': 9000000
}

EMAIL_SETTINGS = {
    'sender': 'pratikshanayak.nr@gmail.com',
    'password': password,
    'receiver': 'mvrp7143@gmail.com',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}
