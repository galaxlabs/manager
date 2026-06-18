import frappe
from frappe.model.document import Document

def update_account_balance(account_name, debit=0, credit=0):
    """Update account balance respecting debit/credit normal balance convention.
    Asset/Expense types: normal debit balance (debit increases, credit decreases)
    Liability/Equity/Income types: normal credit balance (credit increases, debit decreases)
    """
    if not account_name:
        return
    ac = frappe.get_doc("Account", account_name)
    if ac.account_type in (
        "Asset", "Expense", "Bank", "Cash", "Receivable",
        "Fixed Asset", "Stock", "Depreciation", "Cost of Goods Sold"
    ):
        new_balance = (ac.balance or 0) + (debit or 0) - (credit or 0)
    else:
        new_balance = (ac.balance or 0) + (credit or 0) - (debit or 0)
    ac.db_set("balance", new_balance)

class AccountTransfer(Document):
    def on_submit(self):
        if self.from_account and self.to_account and self.amount:
            update_account_balance(self.from_account, credit=self.amount)
            update_account_balance(self.to_account, debit=self.amount)

    def on_cancel(self):
        if self.from_account and self.to_account and self.amount:
            update_account_balance(self.from_account, debit=self.amount)
            update_account_balance(self.to_account, credit=self.amount)
