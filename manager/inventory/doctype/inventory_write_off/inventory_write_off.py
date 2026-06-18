import frappe
from frappe.model.document import Document
from manager.api import update_account_balance

class InventoryWriteoff(Document):
    def on_submit(self):
        if self.quantity and self.write_off_account:
            # Reduce inventory, charge write-off account
            item = frappe.get_doc("Item", self.item) if self.item else None
            cost = (item.purchase_price or 0) * abs(self.quantity) if item else abs(self.quantity)
            accts = frappe.get_all("Account", filters={"account_type": "Stock"}, limit=1)
            inv = accts[0].name if accts else None
            if inv and cost:
                update_account_balance(inv, credit=cost)
            if self.write_off_account and cost:
                update_account_balance(self.write_off_account, debit=cost)
    
    def on_cancel(self):
        if self.quantity and self.write_off_account:
            item = frappe.get_doc("Item", self.item) if self.item else None
            cost = (item.purchase_price or 0) * abs(self.quantity) if item else abs(self.quantity)
            accts = frappe.get_all("Account", filters={"account_type": "Stock"}, limit=1)
            inv = accts[0].name if accts else None
            if inv and cost:
                update_account_balance(inv, debit=cost)
            if self.write_off_account and cost:
                update_account_balance(self.write_off_account, credit=cost)
