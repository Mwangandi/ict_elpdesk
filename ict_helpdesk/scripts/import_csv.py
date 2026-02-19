import frappe
import csv

def run():
    file_path = "/home/frappe/helpdesk/frappe-bench/sites/server.braid-skate.ts.net/public/files/Projects.csv"
    inserted = 0
    skipped = 0
    
    with open(file_path, newline='', encoding="utf-8-sig") as csvfile:  # utf-8-sig removes BOM
        reader = csv.reader(csvfile)
        
        # Read first line and parse header
        first_line = next(reader, None)
        if not first_line:
            print("❌ CSV file is empty")
            return
        
        # Clean headers - remove quotes and strip whitespace
        if len(first_line) == 1:
            headers = [h.strip().strip('"') for h in first_line[0].split(",")]
        else:
            headers = [h.strip().strip('"') for h in first_line]
        
        print(f"Headers: {headers}")
        print(f"Number of headers: {len(headers)}")
        print("-" * 50)
        
        for row in reader:
            if not row:
                continue
            
            # Each row is one quoted string - split it
            if len(row) == 1:
                values = [v.strip() for v in row[0].split(",")]
            else:
                values = [v.strip() for v in row]
            
            # Handle rows with mismatched columns (due to commas in fields)
            if len(values) != len(headers):
                # Try to handle the case where Department field contains comma
                # Look for pattern where we have extra values
                if len(values) > len(headers):
                    # This is likely due to comma in Department field
                    # We need to merge the split department parts
                    print(f"⚠ Row has {len(values)} values but expected {len(headers)} - attempting to fix")
                    # For now, skip these complex cases
                    skipped += 1
                    continue
                else:
                    print(f"⚠ Row has {len(values)} values but expected {len(headers)}")
                    skipped += 1
                    continue
            
            # Create dictionary
            row_dict = dict(zip(headers, values))
            
            # Extract and clean values
            reference_number = (row_dict.get("Reference Number") or "").strip()
            project_name = (row_dict.get("Project Name") or "").strip()
            scope_of_work = (row_dict.get("Scope of work") or "").strip()
            financial_year = (row_dict.get("Financial Year") or "").strip()
            amount = (row_dict.get("Amount") or "").strip()
            status = (row_dict.get("Status") or "").strip()
            department = (row_dict.get("Department") or "").strip()
            directorate = (row_dict.get("Directorate") or "").strip()
            sub_county = (row_dict.get("Sub County") or "").strip()
            ward = (row_dict.get("Ward") or "").strip()
            contractor = (row_dict.get("Contractor") or "").strip()
            
            # Skip invalid rows
            if not reference_number or not project_name:
                print(f"⚠ Skipping row: Missing required fields (ref='{reference_number}', name='{project_name}')")
                skipped += 1
                continue
            
            # Skip duplicates
            if frappe.db.exists("Project Investments", {"reference_number": reference_number}):
                print(f"⚠ Skipping {reference_number}: Already exists")
                skipped += 1
                continue
            
            try:
                # Convert amount safely
                amount_float = 0
                if amount:
                    try:
                        amount_float = float(amount)
                    except ValueError:
                        print(f"⚠ Invalid amount for {reference_number}: {amount}")
                
                doc = frappe.get_doc({
                    "doctype": "Project Investments",
                    "reference_number": reference_number,
                    "project_name": project_name,
                    "scope_of_work": scope_of_work,
                    "financial_year": financial_year,
                    "amount": amount_float,
                    "status": status,
                    "department": department,
                    "directorate": directorate,
                    "sub_county": sub_county,
                    "ward": ward,
                    "contractor": contractor
                })
                doc.insert(ignore_permissions=True)
                print(f"✅ Inserted: {reference_number} - {project_name}")
                inserted += 1
                
            except Exception as e:
                print(f"❌ Error inserting {reference_number}: {e}")
                import traceback
                traceback.print_exc()
                skipped += 1
        
        frappe.db.commit()
    
    print(f"\n{'='*50}")
    print(f"✅ Import Complete")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print(f"{'='*50}")