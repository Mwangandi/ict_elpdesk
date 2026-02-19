import os
import requests

# sms_gateway_url = "https://api.tililtech.com/sms/v3/sendsms"
# sms_apikey = "YbdIXnAUWVPu7Ks8QHtopkfRwlEicv3y6z0F9qx5Gj2LmOC4DTJSarN1eZBhMg"
# sms_partner_id = 6213
# sms_shortcode = "T-TAVETAGOV"

sms_gateway_url = "https://sms.textsms.co.ke/api/services/sendsms/?"
sms_apikey = "c710c75e3bd7ce9dc2020c207350785e"
sms_partner_id = "14137"
sms_shortcode = "TextSMS"

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

if __name__ == "__main__":
    send_custom_sms(["0795752053"], "Hello")
