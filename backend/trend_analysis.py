#backend/trend_analysis.py 
import sqlite3
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import os
from backend.config.config import DB_PATH, TREND_IMAGE_PATH

TIMEFRAME_MAP = {"day": 1, "week": 7, "month": 30}

def generate_trend(currency="BTC", timeframe="day"):
    try:
        print(f"[DEBUG] generate_trend called with currency='{currency}', timeframe='{timeframe}'")
        days = TIMEFRAME_MAP.get(str(timeframe).lower(), 1)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        query = """
            SELECT timestamp, value
            FROM btc_price
            WHERE currency = ? AND timestamp >= ?
            ORDER BY id ASC
        """
        cursor.execute(query, (currency.upper(), start_time))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return f"<p>No data available for {currency} in the last {days} days.</p>", None, None

        df = pd.DataFrame(rows, columns=["timestamp", "value"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        x_vals = df["timestamp"].tolist()
        y_vals = df["value"].tolist()
        fig = go.Figure()

        # Line segments: green for increase, red for decrease
        for i in range(1, len(y_vals)):
            color = "green" if y_vals[i] >= y_vals[i-1] else "red"
            fig.add_trace(go.Scatter(
                x=[x_vals[i-1], x_vals[i]],
                y=[y_vals[i-1], y_vals[i]],
                mode="lines",
                line=dict(color=color, width=2),
                showlegend=False
            ))

        # Latest marker with dynamic color
        if len(y_vals) > 1:
            latest_color = "green" if y_vals[-1] >= y_vals[-2] else "red"
        else:
            latest_color = "blue"
        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers+text",
            name="Latest",
            marker=dict(color=latest_color, size=10),
            text=[f"{y_vals[-1]:.2f}"],
            textposition="top center"
        ))

        currency_label = currency.upper()
        fig.update_layout(
            title=f"{currency_label} Price Trend (Last {days} Days)",
            xaxis_title="Time",
            yaxis_title=f"Price ({currency_label})",
            yaxis=dict(tickformat=".2f"),
            template="plotly_white",
            autosize=True
        )

        os.makedirs(os.path.dirname(TREND_IMAGE_PATH), exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        base_name = f"btc_trend_{currency}_{timestamp_str}"
        html_path = os.path.join(os.path.dirname(TREND_IMAGE_PATH), f"{base_name}.html")
        png_path = os.path.join(os.path.dirname(TREND_IMAGE_PATH), f"{base_name}.png")
        fig.write_html(html_path, include_plotlyjs='cdn', full_html=True, auto_open=False, config={'responsive': True})
        fig.write_image(png_path)
        return fig.to_html(full_html=False), html_path, png_path

    except sqlite3.OperationalError as e:
        return f"<p style='color:red;'>Database error: {e}</p>", None, None
    except Exception as e:
        return f"<p style='color:red;'>Error generating trend: {e}</p>", None, None

def run(currency="BTC", timeframe="day"):
    return generate_trend(currency, timeframe)

if __name__ == "__main__":
    generate_trend(currency="BTC", timeframe="week")
