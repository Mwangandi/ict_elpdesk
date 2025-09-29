// Copyright (c) 2025, Pantech Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("ICT Ticket", {
    // Auto populating requester details from personal_number
    personal_number: function(frm){
        if(!frm.doc.personal_number) return;

        frappe.call({
            method: "ict_helpdesk.api.get_user_data.ticket_personal_num",
            args: {personal_number: frm.doc.personal_number},
            callback: function(r){
                console.log(r.message) // For Testing TODO: delete 
                const full_name = r.message.first_name+ " " + r.message.middle_name + " " + r.message.last_name;
                frm.set_value("full_name", full_name);
                frm.set_df_property("full_name", "hidden", 0);
                frm.refresh_field("full_name");
                const fields = [
                    "phone_number", "email", "mobile_no","department", "directorate", "location", "designation"
                ]
                fields.forEach(function(fieldname) {
                    if(r.message[fieldname]){
                        frm.set_value(fieldname, r.message[fieldname]);
                        frm.set_df_property(fieldname, "hidden", 0);
                        frm.refresh_field(fieldname);
                    }
                });
            }
        })
    },
    tag_number: function(frm){
        if(!frm.doc.tag_number) return;

        if (frm.doc.tag_number){ 
            frappe.call({
                method: "ict_helpdesk.api.device_data.get_tag_number",
                args: {"tag_number": frm.doc.tag_number},
                callback: function(r){
                    console.log(r.message);
                    const fields = [
                        "serial_number","county_device_type", "device_model", "device_ram", "device_storage", 
                        "device_department", "device_directorate", "device_office", "officer_in_charge"
                    ]
                    const specific_fields = [
                        "device_ram", "device_storage"
                    ]
                    // if device is all-in-one || laptop || system unit then show ram and storage
                    fields.forEach(function(fieldname) {
                        if(r.message[fieldname]){
                            frm.set_value(fieldname, r.message[fieldname]);
                            frm.set_df_property(fieldname, "hidden", 0);
                            frm.refresh_field(fieldname);
                        }
                    });
                    if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit"){
                        specific_fields.forEach(function(fieldname){
                            if(r.message[fieldname]){
                                frm.set_value(fieldname, r.message[f]);
                                frm.set_df_property(fieldname, "hidden", 0);
                                frm.refresh_field(fieldname);
                            }
                        });
                    }

                }
            });
        }
    },
    serial_number: function (frm){
        if(!frm.doc.serial_number) return;

        frappe.call({
            method: "ict_helpdesk.api.device_data.get_serial_num" ,
            args: {"serial_number": frm.doc.serial_number},
            callback: function(r){
                console.log(r.message);
                const fields = [
                    "tag_number","device_name", "device_model", 
                    "device_department", "device_directorate", "device_office", "officer_in_charge"
                ]
                const specific_fields = [
                    "device_ram", "device_storage"
                ]
                // if device is all-in-one || laptop || system unit then show ram and storage
                fields.forEach(function(fieldname) {
                    if(r.message[fieldname]){
                        frm.set_value(fieldname, r.message[fieldname]);
                        frm.set_df_property(fieldname, "hidden", 0);
                        frm.refresh_field(fieldname);
                    }
                });
                if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit"){
                    specific_fields.forEach(function(fieldname){
                        if(r.message[fieldname]){
                            frm.set_value(fieldname, r.message[f]);
                            frm.set_df_property(fieldname, "hidden", 0);
                            frm.refresh_field(fieldname);
                        }
                    });
                }
            }
        });
    },
    software_issue_check: function(frm){
        if(software_issue_check == 0){
            const software_section = [
                "software_issue_select", "software_issue_description"
            ]
            software_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
            });
            frm.refresh_field(software_section);
        }
        // Remeber revenue is under finance
        // TODO: Fill in the departments and their directories
        const finance_issues = [
            "IFMIS", "IB", "Windows"
        ]
        const hr_issues = [
            "Windows", "Excel", "office"
        ]
        const health_issues = [
            "SHA Portal", "Windows", "Office"
        ]
        // Check department and directorate
        if(frm.doc.department == "Finance and Economic PLanning"){
            finance_issues.forEach(function (fieldname){
                frm.set_df_property("issue_type", "options", finance_issues.join("\n"));
                frm.refresh_field(fieldname);
            })
        }
        if(frm.doc.department == "Health Services"){
            health_issues.forEach(function (fieldname){
                frm.set_df_property("issue_type", "options", health_issues.join("\n"));
                frm.refresh_field(fieldname);
            });
        }
        if(frm.doc.department == "Devolution"){
            health_issues.forEach(function (fieldname){
                frm.set_df_property("issue_type", "options", hr_issues.join("\n"));
                frm.refresh_field(fieldname);
            });
        }
    },
     // CLEAR FIELDS IF CHECK UNCHECKED: IF FAILS FALL TO RELOAD THE WHOLE PAGE
    hardware_issue_check: function(frm){
        if(frm.doc.hardware_issue_check == 0){
            // Clear all the fields in the hardware section
            // TODO: Confirm the fields in the array
            const hardware_section = [
                "hardware_issue_description", "county_laptop_check", "device_ram", "device_storage", "device_department",
                "device_directorate", "office", "status"
            ]
            hardware_section.forEach(function(fieldname){
                frm,set_value(fieldname, null);
                frm.refresh_field(fieldname);
            });
            
        }
    },
    county_device_check: function(frm){
        if(frm.doc.county_device_check == 0){
            const device_section = [
                "device_ram", "device_storage", "device_department",
                "device_directorate", "office", "status"
            ]
            device_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            
        }
    },
    internet_issue_check: function(frm){
        if(internet_issue_check == 0){
            const internet_section = [
                "internet_issue_type", "internet_issue_description"
            ]
            internet_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            
        }
    },
     clearance_issue_check: function(frm){
        if(clearance_issue_check == 0){
            frm.set_value("clearance_issue_description", "");
            frm.refresh_field("clearance_issue_description");
        }
    },
	refresh(frm) {

	},
    validate: function(frm) {
        if (!frm.doc.software_issue_check && !frm.doc.hardware_issue_check && !frm.doc.internet_issue_check && !frm.doc.clearance_issue_check) {
            frappe.throw(__("You must select at least one issue type: Software, Hardware, or Clearance."));
        }
    },
});
