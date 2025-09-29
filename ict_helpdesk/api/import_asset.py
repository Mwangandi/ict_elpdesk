import frappe
import csv

def import_asset_data():
    # Direct file path
    csv_file_path = "/home/pat/frappe-bench/apps/ict_helpdesk/random_ict_assets.csv"

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Avoid duplicate by checking serial_number
                if not frappe.db.exists("Asset Data", {"serial_number": row["serial_number"]}):
                    doc = frappe.get_doc({
                        "doctype": "Asset Data",
                        "tag_number": row["tag_number"],
                        "serial_number": row["serial_number"],
                        "device_name": row["device_name"],
                        "device_model": row["device_model"],
                        "device_ram": row["device_ram"],
                        "device_storage": row["device_storage"],
                        "device_department": row["device_department"],
                        "device_directorate": row["device_directorate"],
                        "device_office": row["device_office"],
                        "officer_in_charge": row["officer_in_charge"],
                        "status": row["status"]
                    })
                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()
                    print(f"Inserted Asset Data: {row['serial_number']}")
                else:
                    print(f"Skipped duplicate: {row['serial_number']}")
            except Exception as e:
                frappe.log_error(message=str(e), title="Asset Data Import Error")
                print(f"Error inserting row: {row} - {e}")

if __name__ == "__main__":
    import_asset_data()
