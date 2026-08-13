from dotenv import load_dotenv
import os, requests, smtplib
load_dotenv()

results = {}

# 1. Flask
try:
    r = requests.get('http://127.0.0.1:5000/api/flights', timeout=5)
    flights = r.json().get('flights', [])
    results['Flask'] = ('OK', f'{len(flights)} flight(s) in sheet')
except Exception as e:
    results['Flask'] = ('FAIL', str(e)[:80])

# 2. Sheety
try:
    r = requests.get(
        os.getenv('SHEETY_ENDPOINT'),
        headers={'Authorization': 'Bearer ' + os.getenv('SHEETY_AUTH_TOKEN', '')},
        timeout=10
    )
    results['Sheety'] = ('OK', f'HTTP {r.status_code}')
except Exception as e:
    results['Sheety'] = ('FAIL', str(e)[:80])

# 3. SerpApi
try:
    r = requests.get('https://serpapi.com/search.json', params={
        'engine': 'google_flights',
        'departure_id': 'DEL',
        'arrival_id': 'BOM',
        'outbound_date': '2026-08-17',
        'type': '2',
        'currency': 'INR',
        'hl': 'en',
        'api_key': os.getenv('SERPAPI_API_KEY')
    }, timeout=15)
    data = r.json()
    flights = data.get('best_flights', []) + data.get('other_flights', [])
    if flights:
        cheapest = min(flights, key=lambda f: float(f.get('price', 9999)))
        results['SerpApi'] = ('OK', f'{len(flights)} flights | cheapest INR {cheapest["price"]} via {cheapest["flights"][0]["airline"]}')
    else:
        results['SerpApi'] = ('OK', 'no flights found')
except Exception as e:
    results['SerpApi'] = ('FAIL', str(e)[:80])

# 4. Gmail
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASSWORD'))
    results['Gmail'] = ('OK', 'authenticated successfully')
except Exception as e:
    results['Gmail'] = ('FAIL', str(e)[:80])

print()
for svc, res in results.items():
    icon = 'v' if res[0] == 'OK' else 'x'
    print(f'  [{icon}] {svc}: {" | ".join(str(x) for x in res[1:])}')
