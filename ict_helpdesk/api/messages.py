"""
ict_helpdesk/api/messages.py

Provides:
  - get_messages       → list messages for the logged-in user
  - mark_as_read       → mark a single message as read
  - delete_message     → hard-delete a message the user owns
  - send_message       → (optional) create a message record

Assumes a custom Doctype  →  "ICT Message"  (see doctype JSON).

All endpoints are whitelisted so they can be called from the front-end
via frappe.call().
"""

import frappe
from frappe import _


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _assert_ownership(message_id: str) -> dict:
    """
    Fetch the message and confirm it belongs to the session user.
    Raises PermissionError if not.
    """
    doc = frappe.get_doc("ICT Message", message_id)
    if doc.recipient != frappe.session.user:
        frappe.throw(_("You do not have permission to access this message."), frappe.PermissionError)
    return doc


def _row_to_dict(doc) -> dict:
    """Return a plain dict safe to send to the browser."""
    return {
        "name":     doc.name,
        "folder":   doc.folder or "inbox",
        "sender":   doc.sender_label or doc.sender or "System",
        "subject":  doc.subject or "(no subject)",
        "preview":  (doc.body_text or "")[:120],      # short excerpt
        "body":     doc.body_html or doc.body_text or "",
        "is_read":  bool(doc.is_read),
        "creation": str(doc.creation),
    }


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_messages() -> list:
    """
    Return all ICT Message records addressed to the current user,
    ordered newest-first.

    Front-end call:
        frappe.call({ method: 'ict_helpdesk.api.messages.get_messages' })
    """
    user = frappe.session.user

    rows = frappe.get_all(
        "ICT Message",
        filters={
            "recipient": user,
            "is_deleted": 0,
        },
        fields=[
            "name", "folder", "sender", "sender_label",
            "subject", "body_text", "body_html",
            "is_read", "creation",
        ],
        order_by="creation desc",
        limit=200,          # hard cap – adjust if needed
    )

    result = []
    for r in rows:
        result.append({
            "name":     r.name,
            "folder":   r.folder or "inbox",
            "sender":   r.sender_label or r.sender or "System",
            "subject":  r.subject or "(no subject)",
            "preview":  (r.body_text or "")[:120],
            "body":     r.body_html or r.body_text or "",
            "is_read":  bool(r.is_read),
            "creation": str(r.creation),
        })

    return result


@frappe.whitelist()
def mark_as_read(message_id: str) -> dict:
    """
    Mark a message as read.

    Front-end call:
        frappe.call({
            method: 'ict_helpdesk.api.messages.mark_as_read',
            args:   { message_id: 'ICT-MSG-0001' }
        })
    """
    doc = _assert_ownership(message_id)

    if not doc.is_read:
        doc.is_read = 1
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return {"success": True, "name": message_id}


@frappe.whitelist()
def delete_message(message_id: str) -> dict:
    """
    Soft-delete a message (sets is_deleted = 1).
    The record is kept in the database for audit purposes.

    Front-end call:
        frappe.call({
            method: 'ict_helpdesk.api.messages.delete_message',
            args:   { message_id: 'ICT-MSG-0001' }
        })
    """
    doc = _assert_ownership(message_id)
    doc.is_deleted = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "name": message_id}


@frappe.whitelist()
def archive_message(message_id: str) -> dict:
    """
    Move a message to the 'archived' folder.

    Front-end call:
        frappe.call({
            method: 'ict_helpdesk.api.messages.archive_message',
            args:   { message_id: 'ICT-MSG-0001' }
        })
    """
    doc = _assert_ownership(message_id)
    doc.folder = "archived"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "name": message_id, "folder": "archived"}


@frappe.whitelist()
def send_message(recipient: str, subject: str, body_html: str, body_text: str = "", folder: str = "inbox") -> dict:
    """
    Create a new ICT Message addressed to *recipient*.
    Typically called from server-side hooks or admin tools,
    but can also be triggered from the front-end.

    Front-end call:
        frappe.call({
            method: 'ict_helpdesk.api.messages.send_message',
            args: {
                recipient: 'jane@example.com',
                subject:   'Your ticket has been resolved',
                body_html: '<p>Hello…</p>',
            }
        })
    """
    sender       = frappe.session.user
    sender_label = frappe.db.get_value("User", sender, "full_name") or sender

    doc = frappe.get_doc({
        "doctype":      "ICT Message",
        "recipient":    recipient,
        "sender":       sender,
        "sender_label": sender_label,
        "subject":      subject,
        "body_html":    body_html,
        "body_text":    body_text or frappe.utils.strip_html(body_html),
        "folder":       folder,
        "is_read":      0,
        "is_deleted":   0,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "name": doc.name}
