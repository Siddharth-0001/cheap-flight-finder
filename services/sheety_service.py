import os
import logging
import requests

logger = logging.getLogger(__name__)


def _get_endpoint() -> str:
    return os.getenv("SHEETY_ENDPOINT", "").rstrip("/")


def _get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.getenv("SHEETY_AUTH_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_sheet_name() -> str:
    """
    Derive the singular sheet object name from the Sheety endpoint URL.
    e.g. .../cheapFlightFinder/flights  →  'flight'
    """
    path = _get_endpoint()
    last_segment = path.split("/")[-1]
    # Sheety wraps responses under the singular form of the sheet tab name
    if last_segment.endswith("s"):
        return last_segment[:-1]
    return last_segment


def get_all_flights() -> list[dict]:
    """Fetch all flight watch rows from the Google Sheet via Sheety."""
    try:
        response = requests.get(_get_endpoint(), headers=_get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        for key in data:
            if isinstance(data[key], list):
                return data[key]
        return []
    except Exception as e:
        logger.error(f"Error fetching flights from Sheety: {e}")
        return []


def add_flight(origin: str, destination: str, threshold: float, date: str) -> dict:
    """Add a new flight watch row to the Google Sheet."""
    sheet_name = _get_sheet_name()
    payload = {
        sheet_name: {
            "origin":      origin,
            "destination": destination,
            "threshold":   threshold,
            "date":        date,
            "lastPrice":   "",
        }
    }
    response = requests.post(_get_endpoint(), json=payload, headers=_get_headers(), timeout=10)
    response.raise_for_status()
    return response.json().get(sheet_name, {})


def delete_flight(row_id: int):
    """Delete a flight watch row by its Sheety row id."""
    url = f"{_get_endpoint()}/{row_id}"
    response = requests.delete(url, headers=_get_headers(), timeout=10)
    response.raise_for_status()


def update_flight(row_id: int, fields: dict):
    """Update specific fields on an existing row."""
    sheet_name = _get_sheet_name()
    url = f"{_get_endpoint()}/{row_id}"
    payload = {sheet_name: fields}
    try:
        response = requests.put(url, json=payload, headers=_get_headers(), timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Could not update row {row_id}: {e}")
