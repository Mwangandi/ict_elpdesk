import frappe

@frappe.whitelist()
def get_ict_officers():
    officers = frappe.get_all(
        "ICT Staff",
        filters={"designation": ["!=", "ICT Director"]},
        fields=["full_name"],
        as_dict=True
    )
    return officers

@frappe.whitelist()
def get_officer_details(officer_name):
    officer = frappe.get_value(
        "ICT Staff",
        {"full_name": officer_name},
        ["email", "mobile_no"],
        as_dict=True
    )
    return officer
