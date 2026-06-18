import frappe
from frappe.model.document import Document
from manager.api import update_account_balance

class DepreciationEntry(Document):
    def on_submit(self):
        if self.amount:
            if self.depreciation_expense_account and self.accumulated_depreciation_account:
                update_account_balance(self.depreciation_expense_account, debit=self.amount)
                update_account_balance(self.accumulated_depreciation_account, credit=self.amount)
            # Update fixed asset book value
            if self.fixed_asset:
                fa = frappe.get_doc("Fixed Asset", self.fixed_asset)
                fa.db_set("depreciation", (fa.depreciation or 0) + self.amount)
                fa.db_set("book_value", (fa.book_value or fa.acquisition_cost or 0) - self.amount)
    
    def on_cancel(self):
        if self.amount:
            if self.depreciation_expense_account and self.accumulated_depreciation_account:
                update_account_balance(self.depreciation_expense_account, credit=self.amount)
                update_account_balance(self.accumulated_depreciation_account, debit=self.amount)
            if self.fixed_asset:
                fa = frappe.get_doc("Fixed Asset", self.fixed_asset)
                fa.db_set("depreciation", max(0, (fa.depreciation or 0) - self.amount))
                fa.db_set("book_value", (fa.book_value or 0) + self.amount)
