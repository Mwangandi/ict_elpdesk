import frappe
# Hope this works 
def get_directors():
    # Get all users who have the "Director" role
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Director"},
        fields=["parent as user"]
    )

    directors = []
    for u in users:
        user_doc = frappe.get_doc("User", u.user)

        # Only include active users
        if not user_doc.enabled:
            continue  

        directors.append({
            "email": user_doc.email,
            "full_name": user_doc.full_name or user_doc.first_name + " " + user_doc.middle_name + " " + user_doc.last_name,
            "phone": user_doc.phone or user_doc.mobile_no
        })

    return directors  # returns a list of directors
