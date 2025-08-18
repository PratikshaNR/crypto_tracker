from flask import Flask, render_template, request, redirect, url_for, session, flash 
from backend.fetch_and_store import run as fetch_run
from backend.alert_check import run as alert_run
from backend.trend_analysis import run as trend_run
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="static")
app.secret_key = "MySecretKey123!"  # Keep this secret in production!

# Initialize the users table if it doesn't existpython
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
    conn.commit()
    conn.close()

init_db()

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

    return [
        {"timestamp": row[0], "value": row[1], "currency": row[2]}
        for row in rows
    ]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("Data/database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Choose another.", "error")

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    currency = "inr"
    data = []

    if request.method == 'POST':
        currency = request.form.get("currency", "usd").lower()
        fetch_run([currency])
        alert_run(currency)
        trend_run(currency)
        data = get_latest_data(currency)
        return render_template("index.html", currency=currency, show_chart=True, data=data)

    return render_template("index.html", currency=currency, show_chart=False, data=data)

if __name__ == "__main__":
    app.run(debug=True)
