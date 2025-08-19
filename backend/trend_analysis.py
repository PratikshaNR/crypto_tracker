# backend/trend_analysis.py
import sqlite3
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import os
from backend.config.config import DB_PATH, TREND_IMAGE_PATH

# Map frontend timeframe strings to number of days
TIMEFRAME_MAP = {
    "day": 1,
    "week": 7,
    "month": 30
}

def generate_trend(currency="BTC", timeframe="day"):
    """
    Generates a Plotly trend chart for the given currency over the selected timeframe.
    Returns (HTML string, html_file_path, png_file_path) for embedding and email use.
    """
    try:
        # Convert timeframe string to number of days
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

        # Create Plotly chart with colored segments
        fig = go.Figure()
        x_vals = df["timestamp"].tolist()
        y_vals = df["value"].tolist()

        # Draw line segments: green for increase, red for decrease
        for i in range(1, len(y_vals)):
            color = "green" if y_vals[i] >= y_vals[i-1] else "red"
            fig.add_trace(go.Scatter(
                x=[x_vals[i-1], x_vals[i]],
                y=[y_vals[i-1], y_vals[i]],
                mode="lines",
                line=dict(color=color, width=2),
                showlegend=False
            ))

        # Latest marker
        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers+text",
            name="Latest",
            text=[f"{y_vals[-1]:.2f}"],
            textposition="top center"
        ))

        fig.update_layout(
            title=f"{currency.upper()} Price Trend (Last {days} Days)",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_white",
            autosize=True
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(TREND_IMAGE_PATH), exist_ok=True)

        # Unique filenames for HTML and PNG
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        base_name = f"btc_trend_{currency}_{timestamp_str}"
        html_path = os.path.join(os.path.dirname(TREND_IMAGE_PATH), f"{base_name}.html")
        png_path = os.path.join(os.path.dirname(TREND_IMAGE_PATH), f"{base_name}.png")

        # Save interactive HTML and static PNG
        fig.write_html(
            html_path,
            include_plotlyjs='cdn',
            full_html=True,
            auto_open=False,
            config={'responsive': True}
        )
        fig.write_image(png_path)

        return fig.to_html(full_html=False), html_path, png_path

    except sqlite3.OperationalError as e:
        return f"<p style='color:red;'>Database error: {e}</p>", None, None
    except Exception as e:
        return f"<p style='color:red;'>Error generating trend: {e}</p>", None, None


def run(currency="BTC", timeframe="day"):
    """
    Wrapper function for app.py to call.
    Returns (chart_html, html_path, png_path) for frontend and email use.
    """
    return generate_trend(currency, timeframe)
