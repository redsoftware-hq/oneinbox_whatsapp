import frappe

def create_whatsapp_manager_role():
    if not frappe.db.exists("Role", "WhatsApp Manager"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "WhatsApp Manager",
            "desk_access": 1
        })
        role.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint("WhatsApp Manager role has been created successfully.")
