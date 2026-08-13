import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from services.flight_service import search_cheapest_flight  # uses SerpApi
from services.sheety_service import get_all_flights, add_flight, delete_flight, update_flight
from services.notification_service import send_whatsapp_alert
import atexit

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_all_flights():
    """Background job: check all tracked flights and send alerts if price is below threshold."""
    logger.info("Running scheduled flight price check...")
    flights = get_all_flights()
    if not flights:
        logger.info("No flights to check.")
        return

    for flight in flights:
        try:
            origin = flight.get("origin", "").upper().strip()
            destination = flight.get("destination", "").upper().strip()
            threshold = float(flight.get("threshold", 0))
            date = flight.get("date", "").strip()
            row_id = flight.get("id")

            if not origin or not destination or not date:
                continue

            result = search_cheapest_flight(origin, destination, date)
            if result is None:
                logger.warning(f"No flights found for {origin} → {destination} on {date}")
                continue

            lowest_price = result["price"]
            airline = result.get("airline", "Unknown")
            departure = result.get("departure", "N/A")

            # Update last checked price in sheet
            update_flight(row_id, {"lastPrice": round(lowest_price, 2)})

            logger.info(f"{origin} → {destination}: ₹{lowest_price:.2f} (threshold: ₹{threshold:.2f})")

            if lowest_price < threshold:
                message = (
                    f"✈️ *Flight Deal Alert!*\n\n"
                    f"*Route:* {origin} → {destination}\n"
                    f"*Price:* ₹{lowest_price:.2f} (below your ₹{threshold:.2f} threshold!)\n"
                    f"*Airline:* {airline}\n"
                    f"*Departure:* {departure}\n"
                    f"*Date:* {date}\n\n"
                    f"Book now before the price goes up! 🚀"
                )
                send_whatsapp_alert(message)
                logger.info(f"Alert sent for {origin} → {destination}")

        except Exception as e:
            logger.error(f"Error checking flight {flight}: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/flights", methods=["GET"])
def api_get_flights():
    try:
        flights = get_all_flights()
        return jsonify({"success": True, "flights": flights})
    except Exception as e:
        logger.error(f"GET /api/flights error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/flights", methods=["POST"])
def api_add_flight():
    try:
        data = request.get_json()
        origin = data.get("origin", "").upper().strip()
        destination = data.get("destination", "").upper().strip()
        threshold = float(data.get("threshold", 0))
        date = data.get("date", "").strip()

        if not origin or not destination or not date or threshold <= 0:
            return jsonify({"success": False, "error": "All fields are required and threshold must be > 0"}), 400

        if len(origin) != 3 or len(destination) != 3:
            return jsonify({"success": False, "error": "Origin and destination must be 3-letter IATA codes"}), 400

        new_flight = add_flight(origin, destination, threshold, date)
        return jsonify({"success": True, "flight": new_flight})
    except Exception as e:
        logger.error(f"POST /api/flights error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/flights/<int:flight_id>", methods=["DELETE"])
def api_delete_flight(flight_id):
    try:
        delete_flight(flight_id)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"DELETE /api/flights/{flight_id} error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/check-now", methods=["POST"])
def api_check_now():
    """Manually trigger a price check."""
    try:
        check_all_flights()
        return jsonify({"success": True, "message": "Price check complete!"})
    except Exception as e:
        logger.error(f"POST /api/check-now error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/search-price", methods=["POST"])
def api_search_price():
    """Quick price lookup without saving."""
    try:
        data = request.get_json()
        origin = data.get("origin", "").upper().strip()
        destination = data.get("destination", "").upper().strip()
        date = data.get("date", "").strip()

        if not origin or not destination or not date:
            return jsonify({"success": False, "error": "Origin, destination and date required"}), 400

        result = search_cheapest_flight(origin, destination, date)
        if result:
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": "No flights found for this route/date"})
    except Exception as e:
        logger.error(f"POST /api/search-price error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ── Scheduler ─────────────────────────────────────────────────────────────────

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_all_flights, trigger="interval", hours=1, id="flight_check")
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
