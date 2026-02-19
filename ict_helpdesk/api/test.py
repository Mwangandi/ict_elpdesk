import frappe

def run():
    # First, let's check if the doctype exists
    print("Checking for Project Investments DocType...")
    
    # List all doctypes that might match
    doctypes = frappe.get_all("DocType", 
                               filters={"name": ["like", "%Project%"]}, 
                               fields=["name"])
    
    print(f"\nFound DocTypes with 'Project' in name:")
    for dt in doctypes:
        print(f"  - {dt.name}")
    
    # Check if Project Investments exists
    if not frappe.db.exists("DocType", "Project Investments"):
        print("\n❌ 'Project Investments' DocType does not exist!")
        print("You need to create this DocType first.")
        print("\nWould you like me to help create it? (Y/N)")
    else:
        print("\n✅ 'Project Investments' DocType exists")