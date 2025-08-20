from flask import Flask, render_template, request, redirect, url_for, session, flash
from backend.fetch_and_store import run as fetch_run
from backend.alert_check import run as alert_run
from backend.trend_analysis import run as trend_run
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="static")
app.secret_key = "MySecretKey123!"

# =============================
# Initialize DB
# =============================
def init_db():
    conn = sqlite3.connect("Data/database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "email" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        print("Added 'email' column to users table.")
    conn.commit()
    conn.close()

init_db()

# =============================
# Helpers
# =============================
def get_latest_data(currency):
    conn = sqlite3.connect("Data/database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, value, currency FROM btc_price
        WHERE currency = ?
        ORDER BY id DESC LIMIT 10
    """, (currency.upper(),))
    rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": row[0], "value": row[1], "currency": row[2]} for row in rows]

# =============================
# Auth Routes
# =============================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        if not username or not password or not email:
            flash("Username, email, and password are required.", "error")
            return render_template('signup.html')
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect("Data/database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                flash("Username already exists. Choose another.", "error")
            elif "email" in str(e):
                flash("Email already registered. Use another.", "error")
            else:
                flash("An error occurred. Please try again.", "error")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('login.html')
        conn = sqlite3.connect("Data/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and check_password_hash(result[0], password):
            session['user'] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# =============================
# Index Route (Chart + Data)
# =============================
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    currency = request.form.get("currency", request.args.get("currency", "usd")).lower()
    timeframe = request.form.get("timeframe", request.args.get("timeframe", "day")).lower()
    print(f"[DEBUG] index() received currency='{currency}', timeframe='{timeframe}'")
    currency_upper = currency.upper()
    fetch_run([currency])
    alert_msg = alert_run(currency, timeframe)
    chart_html, html_path, png_path = trend_run(currency_upper, timeframe)
    data = get_latest_data(currency)
    return render_template(
        "index.html",
        currency=currency,
        timeframe=timeframe,
        show_chart=bool(chart_html),
        chart_html=chart_html,
        data=data,
        alert=alert_msg
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
