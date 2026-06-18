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

class PurchaseInvoice(Document):
    def before_save(self):
        # self.calculate_amounts()
        self.set_status()

    def calculate_amounts(self):
        total = 0
        for item in self.get("items", []):
            item.amount = (item.quantity or 0) * (item.rate or 0)
            total += item.amount
        # self.invoice_amount = total
        # self.balance_due = total

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if self.balance_due and self.balance_due > 0:
                self.status = "Submitted"
            else:
                self.status = "Paid"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        self.set_status()
        self.update_supplier_balance()
        self.post_double_entry()

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_supplier_balance(reverse=True)
        self.post_double_entry(reverse=True)

    def update_supplier_balance(self, reverse=False):
        if self.supplier:
            supplier = frappe.get_doc("Supplier", self.supplier)
            amount = self.invoice_amount or 0
            if reverse:
                amount = -amount
            supplier.db_set("accounts_payable", (supplier.accounts_payable or 0) + amount)

    def post_double_entry(self, reverse=False):
        settings = frappe.get_single("Manager Settings")
        ap_account = settings.get("default_ap_account")
        purchase_account = settings.get("default_purchase_account")
        amount = self.invoice_amount or 0
        if reverse:
            amount = -amount
        if purchase_account and amount > 0:
            update_account_balance(purchase_account, debit=amount)
        if ap_account and amount > 0:
            update_account_balance(ap_account, credit=amount)
        # Forex gain/loss
        if hasattr(self, 'currency') and self.currency and self.currency != (settings.get('currency') or 'USD'):
            rate = self.get('exchange_rate') or 1
            if rate and rate != 1:
                base_amt = amount / rate
                diff = amount - base_amt
                if abs(diff) > 0.01:
                    gl = frappe.db.get_value("Account", {"account_name": ["like", "%Realized Gain%"]}, "name") or frappe.db.get_value("Account", {"account_name": ["like", "%Exchange%"]}, "name")
                    if gl:
                        if diff > 0: update_account_balance(gl, credit=diff)
                        else: update_account_balance(gl, debit=abs(diff))
