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

class JournalEntry(Document):
    def before_save(self):
        total_debit = sum((a.debit or 0) for a in self.get("accounts", []))
        total_credit = sum((a.credit or 0) for a in self.get("accounts", []))
        if total_debit != total_credit:
            frappe.throw(f"Debit ({total_debit}) does not equal Credit ({total_credit})")

    def on_submit(self):
        for a in self.get("accounts", []):
            if a.account:
                update_account_balance(a.account, debit=a.debit, credit=a.credit)

    def on_cancel(self):
        for a in self.get("accounts", []):
            if a.account:
                update_account_balance(a.account, debit=a.credit, credit=a.debit)
