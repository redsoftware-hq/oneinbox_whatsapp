import frappe
import json
from frappe import _



@frappe.whitelist()
def is_whatsapp_enabled():
    if not frappe.db.exists("DocType", "WhatsApp Settings"):
        return False
    return frappe.get_cached_value("WhatsApp Settings", "WhatsApp Settings", "enabled")

@frappe.whitelist()
def is_whatsapp_installed():
    if not frappe.db.exists("DocType", "WhatsApp Settings"):
        return False
    return True


@frappe.whitelist()
def get_whatsapp_messages(reference_doctype = None, reference_name = None, phone = None):
    if not frappe.db.exists("DocType", "WhatsApp Message"):
        return []
    messages = []

    filters = {}

    if reference_doctype and reference_name:
        filters = {
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
        }

    or_filters = None
    if phone:
        # filter OR to check phone in to and from field
        or_filters = [
            {"from": phone},
            {"to": phone}
        ] 

    messages += frappe.get_all(
        "WhatsApp Message",
        filters=filters,
        or_filters= or_filters if or_filters else None,
        fields=[
            "name",
            "type",
            "to",
            "from",
            "content_type",
            "message_type",
            "attach",
            "template",
            "use_template",
            "message_id",
            "is_reply",
            "reply_to_message_id",
            "creation",
            "message",
            "status",
            "reference_doctype",
            "reference_name",
            "template_parameters",
            "template_header_parameters",
        ],
    )

    # Filter messages to get only Template messages
    template_messages = [
        message for message in messages if message["message_type"] == "Template"
    ]

    # Iterate through template messages
    for template_message in template_messages:
        template = frappe.get_doc("WhatsApp Templates", template_message["template"])

        # If the template is found, add the template details to the template message
        if template:
            template_message["template_name"] = template.template_name
            if template_message["template_parameters"]:
                parameters = json.loads(template_message["template_parameters"])
                template.template = parse_template_parameters(
                    template.template, parameters
                )

            template_message["template"] = template.template
            if template_message["template_header_parameters"]:
                header_parameters = json.loads(
                    template_message["template_header_parameters"]
                )
                template.header = parse_template_parameters(
                    template.header, header_parameters
                )
            template_message["header"] = template.header
            template_message["footer"] = template.footer

    # Filter messages to get only reaction messages
    reaction_messages = [
        message for message in messages if message["content_type"] == "reaction"
    ]

    # Iterate through reaction messages
    for reaction_message in reaction_messages:
        # Find the message that this reaction is reacting to
        reacted_message = next(
            (
                m
                for m in messages
                if m["message_id"] == reaction_message["reply_to_message_id"]
            ),
            None,
        )

        # If the reacted message is found, add the reaction to it
        if reacted_message:
            reacted_message["reaction"] = reaction_message["message"]

    for message in messages:
        from_name = get_from_name(message) if message["from"] else _("You")
        message["from_name"] = from_name
    # Filter messages to get only replies
    reply_messages = [message for message in messages if message["is_reply"]]

    # Iterate through reply messages
    for reply_message in reply_messages:
        # Find the message that this message is replying to
        replied_message = next(
            (
                m
                for m in messages
                if m["message_id"] == reply_message["reply_to_message_id"]
            ),
            None,
        )

        # If the replied message is found, add the reply details to the reply message
        from_name = (
            get_from_name(reply_message) if replied_message["from"] else _("You")
        )
        if replied_message:
            message = replied_message["message"]
            if replied_message["message_type"] == "Template":
                message = replied_message["template"]
            reply_message["reply_message"] = message
            reply_message["header"] = replied_message.get("header") or ""
            reply_message["footer"] = replied_message.get("footer") or ""
            reply_message["reply_to"] = replied_message["name"]
            reply_message["reply_to_type"] = replied_message["type"]
            reply_message["reply_to_from"] = from_name

    return [message for message in messages if message["content_type"] != "reaction"]

@frappe.whitelist()
def create_whatsapp_message(
    message,
    to,
    attach,
    reply_to,
    content_type="text",
    type="Outgoing",
):
    doc = frappe.new_doc("WhatsApp Message")

    if reply_to:
        reply_doc = frappe.get_doc("WhatsApp Message", reply_to)
        doc.update(
            {
                "is_reply": True,
                "reply_to_message_id": reply_doc.message_id,
            }
        )

    doc.update(
        {
            # "reference_doctype": reference_doctype,
            # "reference_name": reference_name,
            "message": message or attach,
            "to": to,
            "attach": attach,
            "content_type": content_type,
            "type": type,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def send_whatsapp_template(template, to):
    doc = frappe.new_doc("WhatsApp Message")
    doc.update(
        {
            "message_type": "Template",
            "message": "Template message",
            "content_type": "text",
            "use_template": True,
            "template": template,
            "to": to,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def react_on_whatsapp_message(emoji, reply_to_name):
    reply_to_doc = frappe.get_doc("WhatsApp Message", reply_to_name)
    to = reply_to_doc.type == "Incoming" and reply_to_doc.get("from") or reply_to_doc.to
    doc = frappe.new_doc("WhatsApp Message")
    doc.update(
        {
            "reference_doctype": reply_to_doc.reference_doctype,
            "reference_name": reply_to_doc.reference_name,
            "message": emoji,
            "to": to,
            "reply_to_message_id": reply_to_doc.message_id,
            "content_type": "reaction",
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name

def parse_template_parameters(string, parameters):
    for i, parameter in enumerate(parameters, start=1):
        placeholder = "{{" + str(i) + "}}"
        string = string.replace(placeholder, parameter)

    return string

def get_from_name(message):
    if not message["reference_doctype"] or not message["reference_name"]:
        return "Anonymous User"
    doc = frappe.get_doc(message["reference_doctype"], message["reference_name"])
    from_name = ""
    if message["reference_doctype"] == "Lead":
        from_name = doc.get("full_name") or doc.get("first_name") or doc.get("name")
    else:
        from_name = doc.get("first_name", "Anonymous User") + " " + doc.get("last_name", "")
    return from_name



@frappe.whitelist()
def get_whatsapp_contact(start=0, page_length=20):
    start = int(start)
    page_length = int(page_length)


    whatsapp_contacts = frappe.get_all(
        "WhatsApp Contact",
        fields=[
            "phone",
            "whatsapp_name",
            "unread_message_count",
            "last_message_time",
            "discard",
            "is_lead",
            "marketing_opt_in"
        ],
        filters={"is_lead": 0},
        start=start,
        page_length=page_length,
        order_by="last_message_time desc"
    )

    return whatsapp_contacts


@frappe.whitelist()
def save_as_lead(data, doctype):
    try:

        if isinstance(data, str):
            data = json.loads(data)
        variation=None
        lead_doc_meta = frappe.get_meta(doctype)
        if not lead_doc_meta:
            return {"status": "error", "message": f"{doctype} Doctype not found"}

        if isinstance(data, str):
            data = json.loads(data)

        contact_number_fields = ["mobile_no", "mobile_number", "phone", "contact_number", "contact_no", "phone_number", "phone_no"]

        contact_number_field = None

        for field in lead_doc_meta.fields:
            if field.fieldname in contact_number_fields:
                contact_number_field = field
                break
                         
        if contact_number_field:
            contact_number = data.get(contact_number_field.fieldname, "").strip()
            variation=contact_number
        
            if contact_number:
                length_of_number = len(contact_number)
                country_code = contact_number_field.default[:3:] if contact_number_field.default else ""

                if length_of_number == 12 and contact_number.startswith(country_code[0:]):  
                    contact_number = f"{country_code}-{contact_number[2:]}"  
                elif length_of_number == 12 and country_code :
                    contact_number = f"{country_code}-{contact_number[2:]}"
                
                elif length_of_number == 14 and country_code :
                    contact_number = f"{country_code[:3]}-{contact_number[4:]}"
                
                elif length_of_number == 13 and country_code :
                    contact_number = f"{country_code}-{contact_number[3:]}"
                
                elif length_of_number == 10 and country_code :
                    contact_number = f"{country_code[:3:]}-{contact_number}"

                data[contact_number_field.fieldname] = contact_number           

        doc = frappe.get_doc({"doctype": doctype, **data})
        doc.insert(ignore_permissions=True)


        query = """
            UPDATE `tabWhatsApp Contact`
            SET is_lead = 1, reference_doctype = %s, reference_name = %s
            WHERE phone LIKE %s OR phone LIKE %s
            LIMIT 1
        """

        frappe.db.sql(query, (doctype, doc.name, variation, variation))
        frappe.db.commit()

        return {"status": "success", "message": "Lead saved and contact updated"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "save_as_lead Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_form_data():
    executive=frappe.get_all("Executive",fields=["*"])
    center=frappe.get_all("Center",fields=["*"])
    return {"executive":executive,"center":center}

@frappe.whitelist()
def get_leadmapping_fields():
    fields = frappe.get_single("WhatsApp Settings")
    mappings = {"lead_reference_doctype": fields.lead_reference_doctype}

    field_mappings = []

    if fields.whatsapp_lead_field_mapping:
        for field in fields.whatsapp_lead_field_mapping:
            field_mapping = {
                key: value for key, value in field.as_dict().items()
                if key not in ["name", "creation", "modified", "modified_by", "owner", "idx", "docstatus","parent","parenfield","parenttype","doctype","parentfield"]
            }
            field_mapping["linked_records"] = []
            field_mapping["select_options"]=[]
            
            if field.doctype_field_type == "Select" and field.options:
                options_list = field.options.split("\n")
                field_mapping["select_options"]=options_list
                field_mapping["linked_records"] = []
                
                
            
            elif field.doctype_field_type == "Link":
                linked_doctype = frappe.get_meta(fields.lead_reference_doctype).get_field(field.lead_field_name).options
                field_mapping["linked_records"] = [lead.name for lead in frappe.get_all(linked_doctype, fields=["name"])]
                field_mapping["select_options"]=[]
            field_mappings.append(field_mapping)

    return {"mappings": mappings, "field_mappings": field_mappings}


@frappe.whitelist()
def reset_unread_count(phone):

    try:
        user_doc = frappe.get_all(
            "WhatsApp Contact",
            filters={"phone": phone},
            fields=["name"]
        )

        if user_doc:
            user_doc = frappe.get_doc("WhatsApp Contact", user_doc[0]["name"])
            user_doc.unread_message_count = 0
            user_doc.save(ignore_permissions=True)
            return {"status": "success", "message": "Unread message count reset successfully."}
        else:
            return {"status": "error", "message": f"Phone Number {phone} on WhatsApp Contact List"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reset Unread Count Error")
        return {"status": "error", "message": str(e)}
    
def send_message_event(doc, method=None):
    try:
        formatted_message = {
            "from": getattr(doc, "from"),
            "to": getattr(doc, "to"),
            "type": getattr(doc, "type"),
            "message": getattr(doc, "message", ""),
            "timestamp": getattr(doc, "creation"),
            "content_type": getattr(doc, "content_type"),
            "message_type": getattr(doc, "message_type"),
            "attach": getattr(doc, "attach"),
            "template": getattr(doc, "template"),
            "use_template": getattr(doc, "use_template"),
            "message_id": getattr(doc, "name"),
            "is_reply": getattr(doc, "is_reply"),
            "reply_to_message_id": getattr(doc, "reply_to_message_id"),
            "reference_doctype": getattr(doc, "reference_doctype"),
            "reference_name": getattr(doc, "reference_name"),
            "template_parameters": getattr(doc, "template_parameters"),
            "template_header_parameters": getattr(doc, "template_header_parameters"),
            
            }
        

        frappe.publish_realtime("oneinbox_whatsapp_message", formatted_message)

    except Exception as e:
        frappe.logger().error(f"Error Sending Real-Time Message Event: {frappe.get_traceback()}")
        frappe.log_error("Error Sending Real-Time Message Event", frappe.get_traceback())



import frappe

def emit_user_update_event(doc, method=None):
    try:
        before_save = doc.get_doc_before_save()  # Get the previous state of the document
        changed_fields = []

        if before_save:
            for field in ["phone", "last_message_time", "whatsapp_name", "unread_message_count", "is_lead", "discard", "marketing_opt_in"]:
                if getattr(doc, field) != getattr(before_save, field):
                    changed_fields.append(field) 
                    
        user_update_event = {
            "phone": doc.phone,
            "last_message_time": doc.last_message_time,
            "whatsapp_name": doc.whatsapp_name,
            "unread_message_count": doc.unread_message_count,
            "is_lead": doc.is_lead,
            "discard": doc.discard,
            "marketing_opt_in": doc.marketing_opt_in,
            "changed_fields": changed_fields  # Append changed fields list
        }

        frappe.publish_realtime(
            "whatsapp_contact_update",
            user_update_event,
        ) 

    except Exception as e:
        frappe.log_error(f"Error in emit_user_update_event: {str(e)}")


@frappe.whitelist(allow_guest=True)     
def is_mapping_set():
    fields = frappe.get_single("WhatsApp Settings")
    return {"set_status":fields.lead_reference_doctype!=""}
