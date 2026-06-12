# 📊 CryptoWatch — Real-Time Crypto Intelligence Dashboard

> Live dashboard tracking 50+ crypto assets with interactive historical charts, portfolio profit/loss tracking, and automated email price alerts.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000?style=flat&logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)

---

## Features

- **Real-Time Tracking** — Live prices for 50+ crypto assets via CoinGecko API
- **Historical Charts** — Interactive 7d/30d/90d price charts using Chart.js
- **Portfolio Tracker** — Multi-currency portfolio with buy price, current value, and P/L calculation
- **Price Alerts** — Configurable email alerts via SMTP when price crosses thresholds
- **Multi-Currency** — Support for USD, EUR, INR, and other fiat currencies
- **Responsive UI** — Clean dashboard that works on desktop and mobile

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, Flask |
| Data Source | CoinGecko API |
| Charts | Chart.js |
| Alerts | SMTP (email) |
| Frontend | HTML, CSS, JavaScript |

---

## Quick Start

```bash
git clone https://github.com/ansariazad/CryptoWatch.git
cd CryptoWatch
pip install -r requirements.txt

# Set email for alerts (optional)
export SMTP_EMAIL="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

python app.py
```

Dashboard available at: http://localhost:5000

---

## Author

**Azad Ansari** · [Portfolio](https://ansariazad.github.io/hire.html) · [GitHub](https://github.com/ansariazad) · [LinkedIn](https://linkedin.com/in/azad-ansari-902035297)
