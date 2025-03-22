import frappe

def execute(filters=None):
    # Define columns
    columns = [
        {"fieldname": "date_of_contact", "label": "Date of Contact", "fieldtype": "Date", "width": 120},
        {"fieldname": "contact_number", "label": "Contact Number", "fieldtype": "Int", "width": 150}
    ]

    # Default filter values
    from_date = filters.get("from_date") if filters else None
    to_date = filters.get("to_date") if filters else None

    # Fetch data
    data = get_data(from_date, to_date)

    return columns, data

def get_data(from_date, to_date):
    conditions = "WHERE type = 'Incoming'"
    values = {}

    if from_date and to_date:
        conditions += " AND DATE(creation) BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = from_date
        values["to_date"] = to_date

    query = f"""
        SELECT DATE(creation) AS date_of_contact, 
               COUNT(DISTINCT `from`) AS contact_number
        FROM `tabWhatsApp Message`
        {conditions}
        GROUP BY DATE(creation)
    """

    return frappe.db.sql(query, values, as_dict=True)
