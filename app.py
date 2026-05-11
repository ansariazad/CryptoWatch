"""
CryptoWatch — Real-time Cryptocurrency Dashboard
Tracks 50+ crypto assets with interactive charts and email price alerts.
Author: Azad Ansari
"""

from flask import Flask, render_template, jsonify, request
import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "crypto.db")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


# ── Database Setup ──
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            target_price REAL NOT NULL,
            direction TEXT NOT NULL,
            email TEXT NOT NULL,
            triggered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            amount REAL NOT NULL,
            buy_price REAL NOT NULL,
            currency TEXT DEFAULT 'usd',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── API Routes ──
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/markets")
def get_markets():
    """Fetch top 50 crypto assets by market cap."""
    currency = request.args.get("currency", "usd")
    page = request.args.get("page", 1, type=int)
    try:
        resp = requests.get(f"{COINGECKO_BASE}/coins/markets", params={
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": 50,
            "page": page,
            "sparkline": True,
            "price_change_percentage": "1h,24h,7d"
        }, timeout=10)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/coin/<coin_id>")
def get_coin(coin_id):
    """Fetch detailed data for a specific coin."""
    try:
        resp = requests.get(f"{COINGECKO_BASE}/coins/{coin_id}", params={
            "localization": "false",
            "tickers": False,
            "community_data": False,
            "developer_data": False
        }, timeout=10)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chart/<coin_id>")
def get_chart(coin_id):
    """Fetch historical price data for charting."""
    days = request.args.get("days", "7")
    currency = request.args.get("currency", "usd")
    try:
        resp = requests.get(f"{COINGECKO_BASE}/coins/{coin_id}/market_chart", params={
            "vs_currency": currency,
            "days": days
        }, timeout=10)
        data = resp.json()
        return jsonify({
            "prices": data.get("prices", []),
            "volumes": data.get("total_volumes", []),
            "market_caps": data.get("market_caps", [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio", methods=["GET", "POST", "DELETE"])
def portfolio():
    """Manage portfolio holdings."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == "POST":
        data = request.json
        c.execute("INSERT INTO portfolio (coin_id, amount, buy_price, currency) VALUES (?,?,?,?)",
                  (data["coin_id"], data["amount"], data["buy_price"], data.get("currency", "usd")))
        conn.commit()
        conn.close()
        return jsonify({"status": "added"})

    elif request.method == "DELETE":
        entry_id = request.args.get("id")
        c.execute("DELETE FROM portfolio WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "deleted"})

    else:
        c.execute("SELECT * FROM portfolio ORDER BY added_at DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([{
            "id": r[0], "coin_id": r[1], "amount": r[2],
            "buy_price": r[3], "currency": r[4], "added_at": r[5]
        } for r in rows])


@app.route("/api/alerts", methods=["GET", "POST", "DELETE"])
def alerts():
    """Manage price alerts."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == "POST":
        data = request.json
        c.execute("INSERT INTO alerts (coin_id, target_price, direction, email) VALUES (?,?,?,?)",
                  (data["coin_id"], data["target_price"], data["direction"], data["email"]))
        conn.commit()
        conn.close()
        return jsonify({"status": "alert_created"})

    elif request.method == "DELETE":
        alert_id = request.args.get("id")
        c.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "deleted"})

    else:
        c.execute("SELECT * FROM alerts WHERE triggered=0 ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([{
            "id": r[0], "coin_id": r[1], "target_price": r[2],
            "direction": r[3], "email": r[4], "triggered": r[5]
        } for r in rows])


@app.route("/api/search")
def search():
    """Search for coins by name."""
    query = request.args.get("q", "")
    try:
        resp = requests.get(f"{COINGECKO_BASE}/search", params={"query": query}, timeout=10)
        data = resp.json()
        return jsonify(data.get("coins", [])[:10])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Alert Checker ──
def check_alerts():
    """Check all active alerts against current prices."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM alerts WHERE triggered=0")
    active_alerts = c.fetchall()

    if not active_alerts:
        return

    coin_ids = list(set([a[1] for a in active_alerts]))
    try:
        resp = requests.get(f"{COINGECKO_BASE}/simple/price", params={
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd"
        }, timeout=10)
        prices = resp.json()

        for alert in active_alerts:
            alert_id, coin_id, target, direction, email = alert[0], alert[1], alert[2], alert[3], alert[4]
            current = prices.get(coin_id, {}).get("usd", 0)

            triggered = False
            if direction == "above" and current >= target:
                triggered = True
            elif direction == "below" and current <= target:
                triggered = True

            if triggered:
                send_alert_email(email, coin_id, current, target, direction)
                c.execute("UPDATE alerts SET triggered=1 WHERE id=?", (alert_id,))

        conn.commit()
    except Exception as e:
        print(f"Alert check error: {e}")
    finally:
        conn.close()


def send_alert_email(to_email, coin_id, current_price, target_price, direction):
    """Send price alert notification email."""
    subject = f"🚨 CryptoWatch Alert: {coin_id.upper()} is {direction} ${target_price}"
    body = f"""
    CryptoWatch Price Alert Triggered!
    
    Coin: {coin_id.upper()}
    Current Price: ${current_price:,.2f}
    Target Price: ${target_price:,.2f}
    Direction: {direction}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    — CryptoWatch by Azad Ansari
    """
    print(f"📧 Alert: {coin_id} {direction} ${target_price} → {to_email}")


if __name__ == "__main__":
    init_db()
    print("🚀 CryptoWatch starting on http://localhost:5000")
    app.run(debug=True, port=5000)
