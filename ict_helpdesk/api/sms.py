import os
from dotenv import load_dotenv
import requests
import frappe

load_dotenv()

sms_gateway_url = os.getenv("SMS_GATEWAY_URL")
sms_apikey = os.getenv("SMS_APIKEY")
sms_partner_id = os.getenv("SMS_PARTNER_ID")
sms_shortcode = os.getenv("SMS_SHORTCODE")

# Validate environment variables
for var_name, var_value in [
    ("SMS_GATEWAY_URL", sms_gateway_url),
    ("SMS_APIKEY", sms_apikey),
    ("SMS_PARTNER_ID", sms_partner_id),
    ("SMS_SHORTCODE", sms_shortcode)
]:
    assert var_value, f"{var_name} not set in environment"

def send_custom_sms(number, message):
    payload = {
        "apikey": sms_apikey,
        "partnerID": sms_partner_id,
        "shortcode": sms_shortcode,
        "mobile": number,
        "message": message
    }
    response = requests.post(sms_gateway_url, data=payload)
    frappe.log_error(
        message=f"Full SMS Response: {response.text}",
        title=f"SMS to {number}"[:140]
    )

# if __name__ == "__main__":
#     send_custom_sms(["0795752053"], "Hello")
