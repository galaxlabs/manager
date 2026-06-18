import frappe
from frappe.model.document import Document


class ManagerSettings(Document):
    pass


@frappe.whitelist()
def get_default_account(account_type):
    """Get default account name from Manager Settings by account type."""
    settings = frappe.get_single("Manager Settings")
    field_map = {
        "AR": "default_ar_account",
        "AP": "default_ap_account",
        "Cash": "default_cash_account",
        "Sales": "default_sales_account",
        "Purchase": "default_purchase_account",
    }
    field = field_map.get(account_type)
    if not field:
        return None
    return settings.get(field)
