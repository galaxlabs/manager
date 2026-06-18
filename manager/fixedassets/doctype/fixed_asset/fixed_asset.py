import frappe
from frappe.model.document import Document

class FixedAsset(Document):
    def before_save(self):
        cost = self.acquisition_cost or 0
        depr = self.depreciation or 0
        self.book_value = cost - depr
