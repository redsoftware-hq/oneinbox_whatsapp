// Copyright (c) 2025, Shridhar Patil and contributors
// For license information, please see license.txt

frappe.query_reports["Unique Number Contacted"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1,  // Required field
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)  // Default: Last 7 days
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1,  // Required field
            "default": frappe.datetime.get_today()  
        }
    ]
};
