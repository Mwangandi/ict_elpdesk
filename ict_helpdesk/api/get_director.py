import frappe


def get_director():
    # Get all users who have the "Director" role
    director = frappe.get_all(
        "ICT Staff",
        filters={"designation": "ICT Director"},
        fields=["mobile_no", "email"]
    )
    if not director:
        return None
    print(director)
    return director[0]

# if __name__ == "__main__":
#     get_director()


 