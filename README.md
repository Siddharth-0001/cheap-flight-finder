# ✈️ Cheap Flight Finder

A personal flight price tracker that monitors one-way flight prices via the Amadeus API and sends WhatsApp alerts via Twilio when prices drop below your set threshold. Google Sheets (via Sheety) serves as the database.

---

## Features

- 🎯 Set price thresholds for any one-way route
- 🔍 Instantly check current cheapest price before saving
- 🔄 Auto-checks all tracked routes every hour in the background
- 📲 WhatsApp alert when a price drops below threshold
- 📊 Google Sheets as the database (via Sheety API)
- 🌐 Clean, modern web UI

---

## Setup

### 1. Google Sheet Structure

Create a Google Sheet with a tab named **`flights`** and these exact column headers in row 1:

| id | origin | destination | threshold | date | lastPrice |
|----|--------|-------------|-----------|------|-----------|

Then connect it to [Sheety](https://sheety.co) and copy the API endpoint.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
copy .env.example .env
```

```env
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886   # Twilio sandbox number
TWILIO_WHATSAPP_TO=whatsapp:+YOUR_NUMBER     # Your WhatsApp number

SHEETY_ENDPOINT=https://api.sheety.co/YOUR_USERNAME/flightTracker/flights

FLASK_SECRET_KEY=any_random_string
```

### 4. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## How it works

1. Add a flight watch: enter origin IATA code, destination IATA code, travel date, and price threshold
2. The app saves it to your Google Sheet via Sheety
3. Every hour, the background scheduler checks all tracked routes via Amadeus
4. If any price is below the threshold, a WhatsApp message is sent via Twilio
5. Use "Check All Now" for an immediate manual check

---

## IATA Code Examples

| City | Code |
|------|------|
| New York (JFK) | JFK |
| London Heathrow | LHR |
| Dubai | DXB |
| Paris CDG | CDG |
| Los Angeles | LAX |
| Mumbai | BOM |

---

## Project Structure

```
cheap-flight-finder/
├── app.py                    # Flask app + scheduler
├── requirements.txt
├── .env.example
├── services/
│   ├── flight_service.py     # Amadeus API integration
│   ├── sheety_service.py     # Sheety / Google Sheets integration
│   └── notification_service.py  # Twilio WhatsApp alerts
├── templates/
│   └── index.html            # Main UI
└── static/
    ├── css/style.css
    └── js/app.js
```
