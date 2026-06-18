import frappe
from frappe.model.document import Document
from manager.api import update_account_balance

class GoodsReceipt(Document):
    def on_submit(self):
        # Increase inventory, credit AP clearing
        if self.total_amount and self.supplier:
            settings = frappe.get_single("Manager Settings")
            # Credit AP 
            ap = settings.get("default_ap_account")
            inv = None
            # Find inventory account
            accts = frappe.get_all("Account", filters={"account_type": "Stock"}, limit=1)
            if accts:
                inv = accts[0].name
            if inv and self.total_amount:
                update_account_balance(inv, debit=self.total_amount)
            if ap and self.total_amount:
                update_account_balance(ap, credit=self.total_amount)
    
    def on_cancel(self):
        if self.total_amount:
            settings = frappe.get_single("Manager Settings")
            ap = settings.get("default_ap_account")
            accts = frappe.get_all("Account", filters={"account_type": "Stock"}, limit=1)
            inv = accts[0].name if accts else None
            if inv and self.total_amount:
                update_account_balance(inv, credit=self.total_amount)
            if ap and self.total_amount:
                update_account_balance(ap, debit=self.total_amount)
