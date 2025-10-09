// Copyright (c) 2025, Pantech Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("ICT Staff", {
    personal_number: function(frm){
        // Get officer data from the User information
        frappe.call({
            method: "ict_helpdesk.api.get_user_data.get_officer_dets",
            args: {personal_number: frm.doc.personal_number},
            callback: function(r){
                console.log(r); //TODO: remove after testing
                const info = ["first_name", "middle_name", "last_name", "mobile_no", "email"]
                info.forEach(function(fieldname){
                    frm.set_value(fieldname, r.message[fieldname]);
                    frm.refresh_field(fieldname);
                });
            }
        });
    }, 
    first_name: function(frm){
        frm.events.update_name(frm);
    },
    middle_name: function(frm){
        frm.events.update_name(frm);
    },
    last_name: function(frm){
        frm.events.update_name(frm);
    },
	refresh(frm) {
        frm.events.update_name(frm);
	},
    
    update_name: function(frm){
        let full_name = [
            frm.doc.first_name || "",
            frm.doc.middle_name || "",
            frm.doc.last_name || ""
        ].filter(Boolean).join(" ");

        frm.set_value("full_name", full_name);
        frm.refresh_field("full_name");
    }
    
});