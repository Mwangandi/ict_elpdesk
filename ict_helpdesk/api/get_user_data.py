import frappe

# getting user info for new user creation
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


# getting ICT ticket requester info
@frappe.whitelist(allow_guest=False)
def ticket_personal_num(personal_number):
    requester_dets = frappe.db.get_value(
        "User",
        {"personal_number": personal_number},
        ["first_name","middle_name", "last_name", "mobile_no", "email", "department", "directorate", "location"],
        as_dict=True
    )
    if requester_dets:
        return requester_dets
    return None


# getting ICT Staff  DOCTYPE INFO
@frappe.whitelist(allow_guest=False)
def get_officer_dets(personal_number):
   officer = frappe.get_doc(
      "User",
      {"personal_number": personal_number},
      {"first_name","middle_name", "last_name", "email", "mobile_no"}
   ) 
   if officer:
      return officer
   else:
      return None


