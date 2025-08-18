from backend.fetch_and_store import run as fetch_run
from backend.alert_check import run as alert_run
from backend.trend_analysis import run as trend_run

def run_all(currencies=None):
    if currencies is None:
        currencies = ["usd", "inr", "eur", "jpy"]
    
    fetch_run(currencies)
    
    for currency in currencies:
        alert_run(currency)
        trend_run(currency)

if __name__ == "__main__":
    run_all()
