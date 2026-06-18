"""Extension registry for Manager.io clone.
Defines all available extensions and their country-specific configurations.
When an extension is enabled, it creates tax codes and configures accounts.
"""
import frappe

EXTENSIONS = {
    "australia": {
        "name": "Australia",
        "label": "Australian GST, PAYG & Bank Feeds",
        "description": "BAS, payroll tax & GST codes",
        "enable_features": ["tax_codes", "bank_feeds", "payroll_tax"],
        "tax_codes": [
            {"code": "GST", "rate": 10, "name": "GST on Sales", "account": "GST Payable"},
            {"code": "GST-P", "rate": 10, "name": "GST on Purchases", "account": "GST Credits"},
            {"code": "GST-F", "rate": 0, "name": "GST Free", "account": None},
            {"code": "PAYG", "rate": 0, "name": "PAYG Withholding", "account": "PAYG Payable"},
        ],
        "default_accounts": [
            {"name": "GST Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "GST Credits", "type": "Liability", "root": "Liabilities"},
            {"name": "PAYG Payable", "type": "Liability", "root": "Liabilities"},
        ],
    },
    "bahrain": {
        "name": "Bahrain",
        "label": "Bahrain VAT",
        "description": "VAT returns & VAT codes",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 10, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 10, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
            {"code": "VAT-E", "rate": 0, "name": "VAT Exempt", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "egypt": {
        "name": "Egypt",
        "label": "Egypt eInvoicing",
        "description": "Egypt eInvoice",
        "enable_features": ["tax_codes", "e_invoicing"],
        "tax_codes": [],
        "default_accounts": [],
    },
    "ghana": {
        "name": "Ghana",
        "label": "Ghana VAT & NHIL",
        "description": "VAT, NHIL & related returns",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 12.5, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "NHIL", "rate": 2.5, "name": "NHIL Levy", "account": "NHIL Payable"},
            {"code": "GETFL", "rate": 2.5, "name": "GETFund Levy", "account": "GETFund Payable"},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "NHIL Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "GETFund Payable", "type": "Liability", "root": "Liabilities"},
        ],
    },
    "ireland": {
        "name": "Ireland",
        "label": "Ireland VAT",
        "description": "VAT3, RTD & VAT codes",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 23, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 23, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "VAT-R", "rate": 13.5, "name": "VAT Reduced Rate", "account": "VAT Payable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "jordan": {
        "name": "Jordan",
        "label": "Jordan eInvoicing",
        "description": "Jofotara GO E-Invoicing",
        "enable_features": ["e_invoicing"],
        "tax_codes": [],
        "default_accounts": [],
    },
    "malaysia": {
        "name": "Malaysia",
        "label": "Malaysia MyInvois",
        "description": "Malaysia MyInvois",
        "enable_features": ["e_invoicing", "tax_codes"],
        "tax_codes": [
            {"code": "SST", "rate": 6, "name": "SST on Sales", "account": "SST Payable"},
        ],
        "default_accounts": [
            {"name": "SST Payable", "type": "Liability", "root": "Liabilities"},
        ],
    },
    "mauritius": {
        "name": "Mauritius",
        "label": "Mauritius eInvoicing",
        "description": "MRA Go! E-Invoicing",
        "enable_features": ["e_invoicing"],
        "tax_codes": [],
        "default_accounts": [],
    },
    "new_zealand": {
        "name": "New Zealand",
        "label": "New Zealand GST",
        "description": "GST return & GST codes",
        "enable_features": ["tax_codes", "gst_return"],
        "tax_codes": [
            {"code": "GST", "rate": 15, "name": "GST on Sales", "account": "GST Payable"},
            {"code": "GST-P", "rate": 15, "name": "GST on Purchases", "account": "GST Credits"},
            {"code": "GST-Z", "rate": 0, "name": "GST Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "GST Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "GST Credits", "type": "Asset", "root": "Assets"},
        ],
    },
    "nigeria": {
        "name": "Nigeria",
        "label": "Nigeria eInvoicing",
        "description": "FIRS Go! E-Invoicing",
        "enable_features": ["e_invoicing"],
        "tax_codes": [],
        "default_accounts": [],
    },
    "oman": {
        "name": "Oman",
        "label": "Oman VAT",
        "description": "VAT return & VAT codes",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 5, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 5, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "pakistan": {
        "name": "Pakistan",
        "label": "Pakistan FBR",
        "description": "Pakistan FBR",
        "enable_features": ["tax_codes", "withholding_tax"],
        "tax_codes": [
            {"code": "ST", "rate": 15, "name": "Sales Tax on Sales", "account": "Sales Tax Payable"},
            {"code": "ST-P", "rate": 15, "name": "Sales Tax on Purchases", "account": "Sales Tax Input"},
            {"code": "WHT-S", "rate": 3, "name": "Withholding Tax (Sales)", "account": "WHT Receivable"},
            {"code": "WHT-P", "rate": 3, "name": "Withholding Tax (Purchases)", "account": "WHT Payable"},
        ],
        "default_accounts": [
            {"name": "Sales Tax Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "Sales Tax Input", "type": "Asset", "root": "Assets"},
            {"name": "WHT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "WHT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "saudi_arabia": {
        "name": "Saudi Arabia",
        "label": "Saudi Arabia VAT & ZATCA",
        "description": "VAT return & VAT codes + ZATCA E-Invoice",
        "enable_features": ["tax_codes", "vat_return", "e_invoicing"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 15, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 15, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "south_africa": {
        "name": "South Africa",
        "label": "South Africa VAT & PAYE",
        "description": "VAT201, IRP5 & tax codes",
        "enable_features": ["tax_codes", "vat_return", "payroll_tax"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 15, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 15, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "PAYE", "rate": 0, "name": "PAYE", "account": "PAYE Payable"},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
            {"name": "PAYE Payable", "type": "Liability", "root": "Liabilities"},
        ],
    },
    "uae": {
        "name": "United Arab Emirates",
        "label": "UAE VAT",
        "description": "VAT201 & VAT codes",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 5, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 5, "name": "VAT on Purchases", "account": "VAT Receivable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Receivable", "type": "Asset", "root": "Assets"},
        ],
    },
    "uk": {
        "name": "United Kingdom",
        "label": "UK VAT",
        "description": "VAT worksheet & VAT codes",
        "enable_features": ["tax_codes", "vat_return"],
        "tax_codes": [
            {"code": "VAT-S", "rate": 20, "name": "VAT on Sales", "account": "VAT Payable"},
            {"code": "VAT-P", "rate": 20, "name": "VAT on Purchases", "account": "VAT Input"},
            {"code": "VAT-R", "rate": 5, "name": "VAT Reduced Rate", "account": "VAT Payable"},
            {"code": "VAT-Z", "rate": 0, "name": "VAT Zero Rated", "account": None},
        ],
        "default_accounts": [
            {"name": "VAT Payable", "type": "Liability", "root": "Liabilities"},
            {"name": "VAT Input", "type": "Asset", "root": "Assets"},
        ],
    },
    "usa": {
        "name": "United States",
        "label": "US Sales Tax",
        "description": "Sales Tax by state",
        "enable_features": ["tax_codes"],
        "tax_codes": [
            {"code": "TAX", "rate": 0, "name": "Sales Tax", "account": "Sales Tax Payable"},
        ],
        "default_accounts": [
            {"name": "Sales Tax Payable", "type": "Liability", "root": "Liabilities"},
        ],
    },
    "coa_builder": {
        "name": "Chart of Accounts Builder",
        "label": "Chart of Accounts Builder",
        "description": "Guided COA setup wizard",
        "enable_features": ["coa_builder"],
        "tax_codes": [],
        "default_accounts": [],
        "is_global": True,
    },
    "custom_themes": {
        "name": "Custom Themes",
        "label": "Custom Themes",
        "description": "Customize the UI appearance",
        "enable_features": ["custom_themes"],
        "tax_codes": [],
        "default_accounts": [],
        "is_global": True,
    },
    "replicator": {
        "name": "Replicator",
        "label": "Replicator",
        "description": "Clone entities across businesses",
        "enable_features": ["replicator"],
        "tax_codes": [],
        "default_accounts": [],
        "is_global": True,
    },
    "dev_extension": {
        "name": "dev-extension",
        "label": "Developer Extension",
        "description": "Tools for developers",
        "enable_features": ["developer"],
        "tax_codes": [],
        "default_accounts": [],
        "is_global": True,
    },
}


def process_extension_toggle(ext_key, enable, tax_codes_to_create=None, default_accounts=None):
    """Called when an extension is toggled on or off.
    Returns: {"status": "ok", "tax_codes_created": [...], "accounts_created": [...], "warnings": [...]}
    """
    result = {"status": "ok", "tax_codes_created": [], "accounts_created": [], "warnings": []}

    ext = EXTENSIONS.get(ext_key)
    if not ext:
        result["status"] = "error"
        result["warnings"].append(f"Unknown extension: {ext_key}")
        return result

    if not enable:
        return result  # Disabling extensions doesn't delete data

    # Create default accounts if they don't exist
    accounts = default_accounts or ext.get("default_accounts", [])
    for acc in accounts:
        acc_name = acc["name"]
        if frappe.db.exists("Account", acc_name):
            continue
        try:
            acc_doc = frappe.get_doc({
                "doctype": "Account",
                "account_name": acc_name,
                "account_type": acc.get("type", "Liability"),
                "parent_account": frappe.db.get_value("Account", acc.get("root", "Liabilities"), "name"),
            })
            acc_doc.insert()
            result["accounts_created"].append(acc_name)
        except Exception as e:
            result["warnings"].append(f"Failed to create account {acc_name}: {e}")

    # Create tax codes if they don't exist
    tax_codes = tax_codes_to_create or ext.get("tax_codes", [])
    for tc in tax_codes:
        code = tc["code"]
        if frappe.db.exists("Tax Code", code):
            continue
        try:
            tc_doc = frappe.get_doc({
                "doctype": "Tax Code",
                "tax_code": code,
                "tax_code_description": tc["name"],
                "tax_rate": tc["rate"],
                "account": tc.get("account") if tc.get("account") else "",
            })
            tc_doc.insert()
            result["tax_codes_created"].append(code)
        except Exception as e:
            result["warnings"].append(f"Failed to create tax code {code}: {e}")

    frappe.db.commit()
    return result


def get_available_extensions():
    """Return all available extensions with their metadata (for frontend)."""
    result = {}
    for key, ext in EXTENSIONS.items():
        country_name = ext.get("name", key)
        result[key] = {
            "label": ext["label"],
            "description": ext["description"],
            "is_global": ext.get("is_global", False),
            "country": None if ext.get("is_global") else country_name,
            "features": ext["enable_features"],
            "tax_count": len(ext.get("tax_codes", [])),
            "account_count": len(ext.get("default_accounts", [])),
        }
    return result
