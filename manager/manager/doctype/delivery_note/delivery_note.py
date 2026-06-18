import frappe
from frappe.model.document import Document

class DeliveryNote(Document):
    def before_save(self):
        self.calculate_amounts()
        self.set_status()

    def calculate_amounts(self):
        total = 0
        for item in self.get("items", []):
            item.amount = (item.quantity or 0) * (item.rate or 0)
            total += item.amount
        self.amount = total

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        self.update_inventory()

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_inventory(reverse=True)

    def update_inventory(self, reverse=False):
        for item in self.get("items", []):
            if item.item_code:
                item_doc = frappe.get_doc("Item", item.item_code)
                qty = (item.quantity or 0)
                if reverse:
                    qty = -qty
                item_doc.db_set("stock_quantity", (item_doc.stock_quantity or 0) - qty)
