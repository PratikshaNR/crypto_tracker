# 💰 Crypto Tracker

## 📌 Overview
Crypto Tracker is a Python + Flask web application that tracks **Bitcoin (BTC)** prices in multiple currencies (USD, INR, EUR, JPY) using the [CoinGecko API](https://www.coingecko.com/en/api/documentation).  
It stores data in **SQLite**, sends alerts if prices cross defined thresholds, and displays price trends using **Matplotlib** charts.

---

## 🚀 Features
- 📡 **Real-time BTC Price Fetching** (USD, INR, EUR, JPY)
- 💾 **SQLite Database Storage**
- 🔔 **Custom Price Alerts**
- 📊 **Trend Visualization** with Matplotlib
- 🌐 **Web Dashboard** built with Flask
- 👤 **Login/Sign-Up System** (if implemented)
- 📱 **Responsive UI**

---

## 📂 Project Structure

## How to Run

### Backend
```bash
pip install -r requirements.txt
cd backend
python fetch_and_store.py
python alert_check.py
python trend_analysis.py
```

### Frontend
```bash
cd frontend
python app.py
```

Open `http://127.0.0.1:5000` in your browser to view the dashboard.

## API Used
[CoinGecko Simple Price API](https://www.coingecko.com/en/api/documentation)

No API key required.
