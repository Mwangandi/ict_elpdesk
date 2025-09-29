import frappe


def get_director():
    # Get all users who have the "Director" role
    director = frappe.get_(
        "ICT Staff",
        filters={"designation": "ICT Director"},
        fields=["mobile_no", "email"]
    )
    if not director:
        return None
    return director
