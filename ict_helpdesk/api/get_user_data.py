import frappe

@frappe.whitelist(allow_guest=True)
def get_user_details(personal_number):
    employee = frappe.db.get_value(
        "Staff Details",
        {"personal_number":personal_number},
        ["first_name","middle_name", "last_name", "mobile_no", "email", "department", "directorate", "location", "gender", "date_of_birth"],
        as_dict=True
    )
    if employee:
        return employee
    return None