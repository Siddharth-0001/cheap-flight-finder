import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_whatsapp_alert(message: str):
    """
    Send a flight deal alert via email (Gmail SMTP).
    Twilio trial accounts no longer support free-form SMS/WhatsApp —
    email is the reliable free alternative.
    """
    try:
        gmail_user     = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Gmail App Password (not login password)
        notify_email   = os.getenv("NOTIFY_EMAIL") or gmail_user

        if not gmail_user or not gmail_password:
            logger.error("GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
            return None

        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✈️ Flight Deal Alert — Cheap Flight Finder"
        msg["From"]    = gmail_user
        msg["To"]      = notify_email

        # Plain text version
        text_part = MIMEText(message, "plain")

        # HTML version — nicer formatting
        html_body = message.replace("\n", "<br>").replace("*", "<strong>").replace("*", "</strong>")
        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f4f4f9;padding:20px;">
          <div style="max-width:480px;margin:auto;background:#fff;border-radius:12px;
                      padding:28px;box-shadow:0 4px 20px rgba(108,99,255,.12);">
            <h2 style="color:#6C63FF;margin-top:0;">✈️ Flight Deal Alert!</h2>
            <p style="font-size:15px;line-height:1.7;color:#1E293B;">{html_body}</p>
            <hr style="border:none;border-top:1px solid #E2E8F0;margin:20px 0;">
            <p style="font-size:12px;color:#94A3B8;">
              Sent by <strong>Cheap Flight Finder</strong> · Powered by SerpApi &amp; Google Flights
            </p>
          </div>
        </body></html>
        """
        html_part = MIMEText(html, "html")

        msg.attach(text_part)
        msg.attach(html_part)

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, notify_email, msg.as_string())

        logger.info(f"Flight alert email sent to {notify_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
        raise
