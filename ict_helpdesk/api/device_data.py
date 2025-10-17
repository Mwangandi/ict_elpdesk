import frappe

@frappe.whitelist(allow_guest=False)
def get_tag_number(tag_number):
    tag = frappe.db.get_value(
        "Asset Data",
        {"tag_number": tag_number},
        ["serial_number", "device_name", "device_model", "device_ram", "device_storage", "device_department", "device_directorate", "device_office", "officer_in_charge", "status"],
        as_dict=True
    )
    if tag:
        return tag
    return None

@frappe.whitelist(allow_guest=False)
def get_serial_num(serial_number):
    serial = frappe.db.get_value(
        "Asset Data",
        {"serial_number": serial_number},
        ["tag_number","device_name", "device_model", "device_ram", "device_storage", "device_department", "device_directorate", "device_office", "officer_in_charge", "status" ],
        as_dict=True
    )
    if serial:
        return serial
    return None
