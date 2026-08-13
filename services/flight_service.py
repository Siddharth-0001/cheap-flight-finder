import os
import logging
import requests

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def search_cheapest_flight(origin: str, destination: str, date: str) -> dict | None:
    """
    Search for the cheapest one-way flight using SerpApi Google Flights.

    Args:
        origin:      3-letter IATA departure code  (e.g. "JFK")
        destination: 3-letter IATA arrival code    (e.g. "LHR")
        date:        Departure date in YYYY-MM-DD  (e.g. "2024-12-15")

    Returns:
        dict with keys: price, airline, departure, duration
        or None if no flights found / error occurred.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        logger.error("SERPAPI_API_KEY is not set in environment variables")
        return None

    params = {
        "engine":        "google_flights",
        "departure_id":  origin,
        "arrival_id":    destination,
        "outbound_date": date,
        "type":          "2",          # 1 = round-trip, 2 = one-way
        "currency":      "INR",
        "hl":            "en",
        "api_key":       api_key,
    }

    try:
        response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # SerpApi returns flights under "best_flights" and "other_flights"
        all_flights = data.get("best_flights", []) + data.get("other_flights", [])

        if not all_flights:
            logger.warning(f"No flights found for {origin} → {destination} on {date}")
            return None

        # Each item has a "price" key and a nested "flights" list
        # Pick the one with the lowest total price
        cheapest = min(all_flights, key=lambda f: float(f.get("price", float("inf"))))

        price = float(cheapest["price"])

        # First leg details
        first_leg = cheapest.get("flights", [{}])[0]
        airline   = first_leg.get("airline", "Unknown")
        departure = first_leg.get("departure_airport", {}).get("time", "N/A")
        duration  = cheapest.get("total_duration", 0)  # minutes

        # Convert duration minutes → "Xh Ym"
        hours, mins = divmod(int(duration), 60)
        duration_str = f"{hours}h {mins}m" if hours else f"{mins}m"

        return {
            "price":     price,
            "airline":   airline,
            "departure": departure,
            "duration":  duration_str,
        }

    except requests.exceptions.Timeout:
        logger.error(f"SerpApi request timed out for {origin} → {destination}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"SerpApi HTTP error: {e} — response: {response.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error searching flights via SerpApi: {e}")
        return None
