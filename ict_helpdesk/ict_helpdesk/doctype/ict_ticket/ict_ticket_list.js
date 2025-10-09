// public/js/doctype/my_doctype/my_doctype_list.js
frappe.listview_settings['ICT Ticket'] = {
    onload: function(listview) {
        // Prevent infinite redirect loops if already on webform
        const webform_path = '/tickets';
        if (window.location.pathname !== webform_path) {
            // Optionally preserve a next param to return after submit
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = webform_path + (next ? '?next=' + next : '');
        }
    }
};
