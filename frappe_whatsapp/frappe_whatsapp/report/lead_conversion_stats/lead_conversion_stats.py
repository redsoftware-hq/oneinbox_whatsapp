import frappe

def execute(filters=None):
    # Define columns
    columns = [
        {"fieldname": "conversion_date", "label": "Conversion Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "lead_count", "label": "Lead Count", "fieldtype": "Int", "width": 120}
    ]

    # Get filter values
    from_date = filters.get("from_date") if filters else None
    to_date = filters.get("to_date") if filters else None

    # Fetch data
    data = get_data(from_date, to_date)

    return columns, data

def get_data(from_date, to_date):
    conditions = "WHERE is_lead = 1"
    values = {}

    if from_date and to_date:
        conditions += " AND DATE(modified) BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = from_date
        values["to_date"] = to_date

    query = f"""
        SELECT DATE(modified) AS conversion_date, 
               COUNT(phone) AS lead_count
        FROM `tabWhatsApp Contact`
        {conditions}
        GROUP BY conversion_date
        ORDER BY conversion_date
    """

    return frappe.db.sql(query, values, as_dict=True)
