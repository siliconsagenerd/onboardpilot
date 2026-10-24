"""Role template definitions and checklist generation."""

from __future__ import annotations

ROLE_TEMPLATES = {
    "developer": {
        "label_de": "Entwickler/in",
        "label_en": "Developer",
        "items": [
            ("laptop", "Laptop ausgeben", "Issue laptop", "Hardware", "it_admin", 1, []),
            ("monitor", "Monitor ausgeben", "Issue monitor", "Hardware", "it_admin", 2, ["laptop"]),
            ("dock", "Dockingstation ausgeben", "Issue dock", "Hardware", "it_admin", 3, ["laptop"]),
            ("email", "E-Mail-Konto einrichten", "Provision email account", "Account", "it_admin", 4, []),
            ("m365", "Microsoft 365 / Teams Zugang", "Microsoft 365 / Teams access", "Access", "it_admin", 5, ["email"]),
            ("vpn", "VPN-Zugang einrichten", "Provision VPN access", "Access", "it_admin", 6, []),
            ("git", "Git / Repository-Zugang", "Git / repository access", "Access", "it_admin", 7, ["email"]),
            ("ide", "IDE und Dev-Tools installieren", "Install IDE and dev tools", "Software", "it_admin", 8, ["laptop"]),
            ("orientation", "IT-Einführung / Orientierung", "IT orientation session", "Orientation", "it_admin", 9, []),
            ("docs", "Dokumentation gelesen", "Read onboarding documentation", "Documentation", "employee", 10, []),
        ],
    },
    "office_hr": {
        "label_de": "Büro / HR",
        "label_en": "Office / HR",
        "items": [
            ("laptop", "Laptop ausgeben", "Issue laptop", "Hardware", "it_admin", 1, []),
            ("monitor", "Monitor ausgeben", "Issue monitor", "Hardware", "it_admin", 2, ["laptop"]),
            ("email", "E-Mail-Konto einrichten", "Provision email account", "Account", "it_admin", 3, []),
            ("m365", "Microsoft 365 / Teams Zugang", "Microsoft 365 / Teams access", "Access", "it_admin", 4, ["email"]),
            ("shared_drive", "Freigabe Netzlaufwerk", "Shared drive access", "Access", "it_admin", 5, ["email"]),
            ("hr_system", "HR-System Zugang", "HR system access", "Access", "it_admin", 6, ["email"]),
            ("printer", "Drucker einrichten", "Printer setup", "Software", "it_admin", 7, []),
            ("orientation", "IT-Einführung / Orientierung", "IT orientation session", "Orientation", "it_admin", 8, []),
            ("docs", "Dokumentation gelesen", "Read onboarding documentation", "Documentation", "employee", 9, []),
        ],
    },
    "sales": {
        "label_de": "Vertrieb",
        "label_en": "Sales",
        "items": [
            ("laptop", "Laptop ausgeben", "Issue laptop", "Hardware", "it_admin", 1, []),
            ("headset", "Headset / Telefon ausgeben", "Issue headset / phone", "Hardware", "it_admin", 2, ["laptop"]),
            ("email", "E-Mail-Konto einrichten", "Provision email account", "Account", "it_admin", 3, []),
            ("m365", "Microsoft 365 / Teams Zugang", "Microsoft 365 / Teams access", "Access", "it_admin", 4, ["email"]),
            ("shared_drive", "Freigabe Netzlaufwerk", "Shared drive access", "Access", "it_admin", 5, ["email"]),
            ("crm", "CRM-Zugang", "CRM access", "Access", "it_admin", 6, ["email"]),
            ("collateral", "Vertriebsunterlagen Zugang", "Sales collateral access", "Access", "it_admin", 7, ["email"]),
            ("orientation", "IT-Einführung / Orientierung", "IT orientation session", "Orientation", "it_admin", 8, []),
            ("docs", "Dokumentation gelesen", "Read onboarding documentation", "Documentation", "employee", 9, []),
        ],
    },
    "manager": {
        "label_de": "Führungskraft",
        "label_en": "Manager",
        "items": [
            ("laptop", "Laptop ausgeben", "Issue laptop", "Hardware", "it_admin", 1, []),
            ("monitor", "Monitor ausgeben", "Issue monitor", "Hardware", "it_admin", 2, ["laptop"]),
            ("email", "E-Mail-Konto einrichten", "Provision email account", "Account", "it_admin", 3, []),
            ("m365", "Microsoft 365 / Teams Zugang", "Microsoft 365 / Teams access", "Access", "it_admin", 4, ["email"]),
            ("reporting", "Reporting-Tools Zugang", "Reporting tools access", "Access", "it_admin", 5, ["email"]),
            ("approvals", "Freigabe-Berechtigungen", "Approval permissions", "Access", "it_admin", 6, ["email"]),
            ("orientation", "IT-Einführung / Orientierung", "IT orientation session", "Orientation", "it_admin", 7, []),
            ("docs", "Dokumentation gelesen", "Read onboarding documentation", "Documentation", "employee", 8, []),
        ],
    },
}

# German/English full titles & descriptions per key
ITEM_DETAILS = {
    "laptop": ("Laptop bereitstellen und ausgeben", "Prepare and issue laptop",
               "Laptop konfigurieren, inventarisieren und an Mitarbeiter übergeben.",
               "Configure, inventory, and hand over the laptop to the employee."),
    "monitor": ("Monitor ausgeben", "Issue monitor",
                "Monitor bereitstellen und anschließen.",
                "Provide and connect the monitor."),
    "dock": ("Dockingstation ausgeben", "Issue docking station",
             "Dockingstation bereitstellen und testen.",
             "Provide and test the docking station."),
    "headset": ("Headset / Telefon ausgeben", "Issue headset / phone",
                "Headset oder Telefon bereitstellen und koppeln.",
                "Provide and pair headset or phone."),
    "email": ("E-Mail-Konto einrichten", "Provision email account",
              "E-Mail-Konto erstellen und Zugangsdaten übergeben.",
              "Create email account and hand over credentials."),
    "m365": ("Microsoft 365 / Teams Zugang", "Microsoft 365 / Teams access",
              "Microsoft 365 und Teams Zugang bereitstellen.",
              "Provide Microsoft 365 and Teams access."),
    "vpn": ("VPN-Zugang einrichten", "Provision VPN access",
            "VPN-Konto erstellen und Client konfigurieren.",
            "Create VPN account and configure client."),
    "git": ("Git / Repository-Zugang", "Git / repository access",
            "Zugang zu Git-Repositories und Dev-Tools.",
            "Access to Git repositories and dev tools."),
    "ide": ("IDE und Dev-Tools installieren", "Install IDE and dev tools",
            "Entwicklungsumgebung und Tools installieren.",
            "Install development environment and tools."),
    "shared_drive": ("Freigabe Netzlaufwerk", "Shared drive access",
                     "Zugang zum gemeinsamen Netzlaufwerk.",
                     "Access to shared network drive."),
    "hr_system": ("HR-System Zugang", "HR system access",
                  "Zugang zum HR-System bereitstellen.",
                  "Provide HR system access."),
    "crm": ("CRM-Zugang", "CRM access",
            "Zugang zum CRM-System bereitstellen.",
            "Provide CRM system access."),
    "collateral": ("Vertriebsunterlagen Zugang", "Sales collateral access",
                   "Zugang zu Vertriebsunterlagen.",
                   "Access to sales collateral."),
    "reporting": ("Reporting-Tools Zugang", "Reporting tools access",
                  "Zugang zu Reporting-Tools.",
                  "Access to reporting tools."),
    "approvals": ("Freigabe-Berechtigungen", "Approval permissions",
                  "Freigabe-Rechte einrichten.",
                  "Set up approval permissions."),
    "printer": ("Drucker einrichten", "Printer setup",
                "Drucker installieren und testen.",
                "Install and test printer."),
    "orientation": ("IT-Einführung / Orientierung", "IT orientation session",
                    "Kurze IT-Einführung für neue Mitarbeiter.",
                    "Short IT orientation for new employees."),
    "docs": ("Dokumentation gelesen", "Read onboarding documentation",
             "Onboarding-Dokumentation lesen und bestätigen.",
             "Read and confirm onboarding documentation."),
}

CATEGORY_MAP = {
    "laptop": "Hardware", "monitor": "Hardware", "dock": "Hardware", "headset": "Hardware",
    "phone": "Hardware", "accessory": "Hardware",
    "email": "Account", "vpn": "Access", "git": "Access", "m365": "Access",
    "shared_drive": "Access", "hr_system": "Access", "crm": "Access",
    "collateral": "Access", "reporting": "Access", "approvals": "Access",
    "ide": "Software", "printer": "Software",
    "orientation": "Orientation", "docs": "Documentation",
}


def generate_checklist_items(case_id: str, role_template: str, start_date: str) -> list[dict]:
    tmpl = ROLE_TEMPLATES[role_template]
    items = []
    for key, t_de, t_en, cat, owner, order, deps in tmpl["items"]:
        title_de, title_en, desc_de, desc_en = ITEM_DETAILS.get(key, (t_de, t_en, "", ""))
        items.append({
            "case_id": case_id,
            "key": key,
            "title_de": title_de,
            "title_en": title_en,
            "description_de": desc_de,
            "description_en": desc_en,
            "category": CATEGORY_MAP.get(key, cat),
            "owner": owner,
            "status": "not_started",
            "due_date": start_date,
            "depends_on": list(deps),
            "sort_order": order,
        })
    return items
