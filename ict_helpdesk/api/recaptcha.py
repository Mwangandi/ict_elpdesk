import frappe, requests

site_key = frappe.db.get_single_value("Recaptcha Settings", "site_key")

@frappe.whitelist(allow_guest=True)
def verify_recaptcha(token):
    """Verify Google reCAPTCHA v3 token before ticket submission"""
    if not token:
        frappe.throw("Missing reCAPTCHA token")

    # Retrieve secret key from Single Doctype: 'Recaptcha Settings'
    secret_key = frappe.db.get_single_value("Recaptcha", "secret_key")

    if not secret_key:
        frappe.throw("Missing reCAPTCHA secret key in Recaptcha Settings")

    # Verify token with Google
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret_key, "response": token}
    )

    result = response.json()
    frappe.logger().info(f"reCAPTCHA response: {result}")

    # Validate response
    if not result.get("success"):
        frappe.throw("reCAPTCHA verification failed. Please try again.")

    score = result.get("score", 0)
    action = result.get("action", "")

    # Adjust threshold as needed
    if score < 0.5:
        frappe.throw("Suspicious activity detected. Please try again later.")

    # return {"success": True, "score": score, "action": action}
    return True