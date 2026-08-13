# ✈️ Cheap Flight Finder

A personal flight price tracker built with **Python & Flask**. It monitors one-way flight prices via the **SerpApi Google Flights API** and sends **Gmail email alerts** when prices drop below your set threshold. **Google Sheets** (via Sheety API) is used as the database.

---

## Features

- 🎯 Set INR price thresholds for any one-way route
- 🔍 Instantly check the current cheapest price before saving
- 🔄 Auto-checks all tracked routes every hour in the background
- 📧 Gmail email alert when a price drops below your threshold
- 📊 Google Sheets as the database (via Sheety API)
- 🌐 Clean, modern web UI built with HTML, CSS & JavaScript

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Flight Prices | SerpApi (Google Flights) |
| Database | Google Sheets + Sheety API |
| Notifications | Gmail (SMTP) |
| Scheduler | APScheduler (hourly price checks) |

---

## Setup

### 1. Google Sheet Structure

Create a Google Sheet with a tab named **`flights`** and these exact column headers in row 1:

| id | origin | destination | threshold | date | lastPrice |
|----|--------|-------------|-----------|------|-----------|

Then connect it to [Sheety](https://sheety.co), enable **Bearer Token** authentication, and copy the API endpoint.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# SerpApi (Google Flights)
SERPAPI_API_KEY=your_serpapi_api_key

# Sheety API
SHEETY_ENDPOINT=https://api.sheety.co/YOUR_USERNAME/cheapFlightFinder/flights
SHEETY_AUTH_TOKEN=your_sheety_bearer_token

# Gmail Notifications
GMAIL_USER=your_gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
NOTIFY_EMAIL=your_gmail@gmail.com

# Flask
FLASK_SECRET_KEY=any_random_string
```

> **Gmail App Password:** Go to [myaccount.google.com/security](https://myaccount.google.com/security) → enable 2-Step Verification → search "App passwords" → create one for Mail → paste the 16-character password.

### 4. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## How it works

1. Add a flight watch — enter origin IATA code, destination IATA code, travel date, and INR price threshold
2. The app saves it to your Google Sheet via Sheety
3. Every hour, APScheduler checks all tracked routes via SerpApi Google Flights
4. If any price is below the threshold, an email alert is sent via Gmail
5. Use **"Check All Now"** for an immediate manual check
6. Use **"Check Current Price"** to preview the live price before saving

---

## Getting API Keys

| Service | Where to get it |
|---------|----------------|
| **SerpApi** | Sign up free at [serpapi.com](https://serpapi.com) — 100 searches/month free, no credit card |
| **Sheety** | Connect your Google Sheet at [sheety.co](https://sheety.co) |
| **Gmail App Password** | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |

---

## IATA Code Examples

| City | Code |
|------|------|
| Delhi | DEL |
| Mumbai | BOM |
| Bangalore | BLR |
| Dubai | DXB |
| London Heathrow | LHR |
| New York JFK | JFK |

---

## Project Structure

```
cheap-flight-finder/
├── app.py                        # Flask app + APScheduler (hourly checks)
├── requirements.txt
├── .env.example                  # Template for credentials
├── .gitignore
├── README.md
├── check.py                      # Utility script to verify all services
├── services/
│   ├── flight_service.py         # SerpApi Google Flights integration
│   ├── sheety_service.py         # Sheety / Google Sheets CRUD
│   └── notification_service.py  # Gmail email alerts
├── templates/
│   └── index.html                # Main UI
└── static/
    ├── css/style.css
    └── js/app.js
```
