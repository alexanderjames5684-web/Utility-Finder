import time

# ─────────────────────────────────────────────
#   ASCII BANNER
# ─────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗               ║
║   ██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝               ║
║   ██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝                ║
║   ██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝                 ║
║   ╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║                  ║
║    ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                  ║
║                                                                      ║
║    ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗                    ║
║    ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗                   ║
║    █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝                   ║
║    ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗                   ║
║    ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║                   ║
║    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝                   ║
║                                                                      ║
║          >>> Compare Electricity, Gas & Water Rates <<<             ║
║                    by ZIP Code  |  v1.1                             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#   UTILITY DATABASE
#   Last updated: 2025-04
#   To update rates: find the provider name below
#   and change the number next to "elec", "gas",
#   or "water". Units: $/kWh, $/therm, $/1000 gal
# ─────────────────────────────────────────────

UTILITY_DB = {
    # ── Midwest (OH, MI, IN) — ZIP prefix 4 ──
    "4": [
        {"name": "FirstEnergy / Ohio Edison",  "elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "AEP Ohio",                   "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",        "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Toledo Edison",               "elec": 0.1280, "gas": 1.11, "water": 5.10, "phone": "1-800-447-3333"},
        {"name": "Toledo City Water",           "elec": None,   "gas": None, "water": 4.60, "phone": "419-936-2020"},
    ],
    # ── Northeast (CT, MA) — ZIP prefix 0 ────
    "0": [
        {"name": "Eversource Energy",           "elec": 0.2210, "gas": 1.45, "water": 7.80, "phone": "1-800-286-2000"},
        {"name": "National Grid",               "elec": 0.2050, "gas": 1.38, "water": 7.20, "phone": "1-800-642-4272"},
        {"name": "UI (United Illuminating)",    "elec": 0.2380, "gas": None, "water": None, "phone": "1-800-722-5584"},
        {"name": "Aquarion Water Company",      "elec": None,   "gas": None, "water": 8.10, "phone": "1-800-732-9678"},
    ],
    # ── NY / NJ — ZIP prefix 1 ───────────────
    "1": [
        {"name": "Con Edison",                  "elec": 0.2340, "gas": 1.52, "water": 9.10, "phone": "1-800-752-6633"},
        {"name": "Orange & Rockland",           "elec": 0.2100, "gas": 1.44, "water": 8.50, "phone": "1-877-434-4100"},
        {"name": "New York American Water",     "elec": None,   "gas": None, "water": 8.90, "phone": "1-877-426-6999"},
        {"name": "PSE&G (NJ)",                  "elec": 0.1680, "gas": 1.30, "water": 6.70, "phone": "1-800-436-7734"},
    ],
    # ── Southeast (FL, GA) — ZIP prefix 3 ────
    "3": [
        {"name": "Duke Energy Florida",         "elec": 0.1190, "gas": 1.05, "water": 4.30, "phone": "1-800-700-8744"},
        {"name": "Florida Power & Light (FPL)", "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "Georgia Power",               "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "TECO Peoples Gas",            "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "JEA (Jacksonville)",          "elec": 0.1155, "gas": 1.08, "water": 4.15, "phone": "1-904-665-6000"},
    ],
    # ── South / TX — ZIP prefix 7 ────────────
    "7": [
        {"name": "Oncor Electric",              "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "CenterPoint Energy",          "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",               "elec": 0.1080, "gas": 0.92, "water": None, "phone": "1-800-968-8243"},
        {"name": "Texas Gas Service",           "elec": None,   "gas": 0.90, "water": None, "phone": "1-800-700-2443"},
        {"name": "City of Houston Water",       "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],
    # ── West / CA — ZIP prefix 9 ─────────────
    "9": [
        {"name": "Pacific Gas & Electric (PG&E)","elec": 0.3100,"gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Southern California Edison",  "elec": 0.2850, "gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                    "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Gas & Electric",    "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "East Bay MUD",                "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
    ],
    # ── Pacific NW — ZIP prefix 97 ───────────
    "97": [
        {"name": "Portland General Electric",  "elec": 0.1250, "gas": 1.20, "water": 5.50, "phone": "1-800-542-8818"},
        {"name": "NW Natural Gas",             "elec": None,   "gas": 1.15, "water": None, "phone": "1-800-422-4012"},
        {"name": "Pacific Power",              "elec": 0.1190, "gas": None, "water": None, "phone": "1-888-221-7070"},
    ],
    # ── National fallback ────────────────────
    "default": [
        {"name": "Generic National Electric Co.", "elec": 0.1400, "gas": 1.20, "water": 5.50, "phone": "N/A"},
        {"name": "National Gas Services",          "elec": None,   "gas": 1.18, "water": None, "phone": "N/A"},
        {"name": "American Water Works",           "elec": None,   "gas": None, "water": 5.80, "phone": "1-800-684-3256"},
    ],
}

# Mapping of filter key → display label, cost key, rate key, unit label, default usage
UTILITY_CONFIG = {
    "elec":  {"label": "Electricity", "cost_key": "elec_cost",  "rate_key": "elec",  "unit": "kWh",    "default": 900,  "divisor": 1},
    "gas":   {"label": "Natural Gas", "cost_key": "gas_cost",   "rate_key": "gas",   "unit": "therms", "default": 50,   "divisor": 1},
    "water": {"label": "Water",       "cost_key": "water_cost", "rate_key": "water", "unit": "gal",    "default": 3000, "divisor": 1000},
}

# ─────────────────────────────────────────────
#   HELPERS
# ─────────────────────────────────────────────

def slow_print(text, delay=0.012):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def divider(char="─", width=72):
    print(char * width)

def get_providers_for_zip(zip_code):
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in UTILITY_DB:
            return UTILITY_DB[prefix]
    return UTILITY_DB["default"]

def get_monthly_cost(rate, usage, divisor=1):
    if rate is None:
        return None
    return rate * (usage / divisor)

# ─────────────────────────────────────────────
#   INPUT HELPERS
# ─────────────────────────────────────────────

def get_zip():
    while True:
        z = input("\n  Enter your ZIP code: ").strip()
        if z.isdigit() and len(z) == 5:
            return z
        print("  ⚠  Please enter a valid 5-digit ZIP code.")

def get_usage(filters):
    """Ask for usage only for the utilities the user cares about."""
    print()
    divider()
    slow_print("  Enter your average MONTHLY usage (press Enter for defaults):")
    divider()

    usage = {}
    for key in ["elec", "gas", "water"]:
        if key not in filters:
            usage[key] = UTILITY_CONFIG[key]["default"]
            continue
        cfg = UTILITY_CONFIG[key]
        prompt = f"  {cfg['label']} usage ({cfg['unit']}) [{cfg['default']} {cfg['unit']}]: "
        val = input(prompt).strip()
        if val == "":
            usage[key] = cfg["default"]
        else:
            try:
                v = float(val)
                if v < 0:
                    raise ValueError
                usage[key] = v
            except ValueError:
                print(f"  ⚠  Invalid — using default ({cfg['default']} {cfg['unit']}).")
                usage[key] = cfg["default"]
    return usage

# ─────────────────────────────────────────────
#   NEW: UTILITY FILTER PICKER  ← v1.1 feature
# ─────────────────────────────────────────────

def pick_utility_filter():
    """
    Let the user choose which utilities to compare:
      - All three (original behaviour)
      - Electricity only
      - Gas only
      - Water only
      - Any custom combination
    Returns a set of active keys, e.g. {"elec"} or {"elec","gas","water"}
    """
    print()
    divider()
    slow_print("  Which utilities do you want to compare?  (v1.1 Filter Mode)", delay=0.015)
    divider()
    print("  [1]  All utilities  (Electricity + Gas + Water)")
    print("  [2]  Electricity only  ⚡")
    print("  [3]  Natural Gas only  🔥")
    print("  [4]  Water only  💧")
    print("  [5]  Custom combination — pick your own mix")
    divider()

    while True:
        choice = input("  Your choice [1-5]: ").strip()
        if choice == "1":
            return {"elec", "gas", "water"}
        elif choice == "2":
            return {"elec"}
        elif choice == "3":
            return {"gas"}
        elif choice == "4":
            return {"water"}
        elif choice == "5":
            return pick_custom_filter()
        else:
            print("  ⚠  Please enter a number from 1 to 5.")

def pick_custom_filter():
    """Let the user toggle individual utilities on/off."""
    print()
    slow_print("  CUSTOM FILTER — type the number to toggle on/off, then press S to save.", delay=0.013)
    selected = {"elec": True, "gas": True, "water": True}
    options  = [("elec", "Electricity ⚡"), ("gas", "Natural Gas 🔥"), ("water", "Water 💧")]

    while True:
        print()
        divider()
        for i, (key, label) in enumerate(options, 1):
            status = "✅ ON " if selected[key] else "❌ OFF"
            print(f"  [{i}]  {label:<20}  {status}")
        divider()
        print("  [S]  Save and continue")

        raw = input("  Toggle [1/2/3] or Save [S]: ").strip().upper()
        if raw == "1":
            selected["elec"]  = not selected["elec"]
        elif raw == "2":
            selected["gas"]   = not selected["gas"]
        elif raw == "3":
            selected["water"] = not selected["water"]
        elif raw == "S":
            active = {k for k, v in selected.items() if v}
            if not active:
                print("  ⚠  You must keep at least one utility selected!")
            else:
                return active
        else:
            print("  ⚠  Invalid — press 1, 2, 3, or S.")

# ─────────────────────────────────────────────
#   RESULTS DISPLAY  (filter-aware)
# ─────────────────────────────────────────────

ICONS = {"elec": "⚡", "gas": "🔥", "water": "💧"}

def display_results(zip_code, providers, usage, filters):
    print()
    divider("═")

    # Build a readable label for the active filter
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec", "gas", "water"] if k in filters]
    filter_str    = " + ".join(filter_labels)
    slow_print(f"  📍  Results for ZIP Code: {zip_code}  |  Showing: {filter_str}", delay=0.013)
    divider("═")

    # Print usage line only for active utilities
    usage_parts = []
    for key in ["elec", "gas", "water"]:
        if key in filters:
            cfg = UTILITY_CONFIG[key]
            usage_parts.append(f"{usage[key]:.0f} {cfg['unit']} {cfg['label'].lower()}")
    print("  Usage: " + " | ".join(usage_parts))
    divider()

    # Build result rows
    results = []
    for p in providers:
        costs = {}
        for key in ["elec", "gas", "water"]:
            cfg = UTILITY_CONFIG[key]
            if key in filters:
                costs[cfg["cost_key"]] = get_monthly_cost(
                    p[cfg["rate_key"]], usage[key], cfg["divisor"]
                )
            else:
                costs[cfg["cost_key"]] = None   # hidden / not requested

        active_costs   = [costs[UTILITY_CONFIG[k]["cost_key"]] for k in filters]
        available      = [c for c in active_costs if c is not None]
        total          = sum(available)
        services_count = len(available)

        results.append({**p, **costs,
                        "total":    total,
                        "services": services_count})

    # Sort: most services first, then cheapest
    results.sort(key=lambda x: (-x["services"], x["total"]))

    # ── Header row ──
    col_w  = 34
    header = f"  {'PROVIDER':<{col_w}}"
    for key in ["elec", "gas", "water"]:
        if key in filters:
            label = UTILITY_CONFIG[key]["label"].upper()[:9]
            header += f"  {label+'/mo':>11}"
    if len(filters) > 1:
        header += f"  {'TOTAL/mo':>10}"
    header += "  PHONE"
    print(header)
    divider()

    for r in results:
        row = f"  {r['name']:<{col_w}}"
        has_any = False
        for key in ["elec", "gas", "water"]:
            if key not in filters:
                continue
            cost_key = UTILITY_CONFIG[key]["cost_key"]
            val = r[cost_key]
            if val is not None:
                row += f"  ${val:>9.2f}"
                has_any = True
            else:
                row += f"  {'N/A':>10}"

        if len(filters) > 1:
            if r["services"] > 0:
                row += f"  ${r['total']:>9.2f}"
            else:
                row += f"  {'N/A':>10}"

        row += f"  {r['phone']}"
        print(row)

    divider()

    # ── Winners ──
    print("\n  🏆  CHEAPEST BY UTILITY:")
    for key in ["elec", "gas", "water"]:
        if key not in filters:
            continue
        cfg      = UTILITY_CONFIG[key]
        cost_key = cfg["cost_key"]
        icon     = ICONS[key]
        candidates = [r for r in results if r[cost_key] is not None]
        if candidates:
            winner = min(candidates, key=lambda x: x[cost_key])
            print(f"     {icon} {cfg['label']:<14} →  {winner['name']}"
                  f"  (${winner[cost_key]:.2f}/mo)  📞 {winner['phone']}")
        else:
            print(f"     {icon} {cfg['label']:<14} →  No data for this region.")

    if len(filters) > 1:
        bundle = [r for r in results if r["services"] >= 2]
        if bundle:
            best = bundle[0]
            print(f"\n  💡  BEST BUNDLE ({best['services']} services):  {best['name']}")
            print(f"      Est. monthly total: ${best['total']:.2f}  📞 {best['phone']}")

    divider("═")

# ─────────────────────────────────────────────
#   COMPARE MODE
# ─────────────────────────────────────────────

def compare_mode(usage, filters):
    print()
    divider()
    slow_print("  COMPARISON MODE — Enter two ZIP codes to compare regions.")
    divider()
    zip1 = get_zip()
    zip2 = get_zip()
    for z in [zip1, zip2]:
        display_results(z, get_providers_for_zip(z), usage, filters)

# ─────────────────────────────────────────────
#   ABOUT SCREEN
# ─────────────────────────────────────────────

def about_screen():
    print()
    divider("═")
    slow_print("  ℹ️   ABOUT UTILITY FINDER  v1.1", delay=0.02)
    divider("═")
    print("""
  What's new in v1.1:
  ───────────────────
  • Filter Mode — search a single utility (Electricity, Gas, or
    Water) or any combination you choose.
  • Custom mix — toggle individual utilities on/off before searching.
  • Results table and winners adapt automatically to your filter.

  How rates are calculated:
  ─────────────────────────
  • Electricity  — dollars per kilowatt-hour (kWh)
  • Natural Gas  — dollars per therm (≈ 100,000 BTU)
  • Water        — dollars per 1,000 gallons

  Monthly cost = your usage × the provider's rate.

  Averages used if you skip custom usage input:
    • Electricity :  900 kWh/mo  (US household average)
    • Gas         :   50 therms/mo
    • Water       : 3,000 gal/mo

  Data note:
  ──────────
  Rates are representative estimates based on EIA data and publicly
  reported utility tariffs. Actual bills vary by plan, time-of-use
  pricing, taxes, fees, and season. Always confirm with the provider.
  Rates are updated manually in the source file — look for the
  comment "Last updated" near the top of the database section.
""")
    divider("═")
    input("  Press Enter to return to the menu...")

# ─────────────────────────────────────────────
#   MAIN MENU
# ─────────────────────────────────────────────

def main_menu(filters):
    """Show the menu; display the current filter next to option 1."""
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec", "gas", "water"] if k in filters]
    filter_str    = " + ".join(filter_labels)

    while True:
        print()
        divider()
        slow_print("  MAIN MENU", delay=0.02)
        divider()
        print(f"  [1]  Find cheapest utilities for my ZIP code")
        print(f"         ↳ Filter: {filter_str}")
        print(f"  [2]  Compare two ZIP codes side-by-side")
        print(f"  [3]  Change utility filter  ← NEW in v1.1")
        print(f"  [4]  Change usage amounts")
        print(f"  [5]  About / How rates work")
        print(f"  [Q]  Quit")
        divider()

        choice = input("  Your choice: ").strip().upper()
        if   choice == "1": return "single"
        elif choice == "2": return "compare"
        elif choice == "3": return "filter"
        elif choice == "4": return "usage"
        elif choice == "5": return "about"
        elif choice == "Q": return "quit"
        else:
            print("  ⚠  Invalid — please enter 1, 2, 3, 4, 5, or Q.")

# ─────────────────────────────────────────────
#   ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print(BANNER)
    time.sleep(0.3)
    slow_print("  Welcome to Utility Finder v1.1!", delay=0.018)
    slow_print("  Now with single-utility filter mode.", delay=0.016)

    # Step 1: pick utilities to compare
    filters = pick_utility_filter()

    # Step 2: get usage only for selected utilities
    usage = get_usage(filters)

    while True:
        choice = main_menu(filters)

        if choice == "single":
            zip_code  = get_zip()
            providers = get_providers_for_zip(zip_code)
            display_results(zip_code, providers, usage, filters)
            input("\n  Press Enter to return to the menu...")

        elif choice == "compare":
            compare_mode(usage, filters)
            input("\n  Press Enter to return to the menu...")

        elif choice == "filter":
            filters = pick_utility_filter()
            # Re-ask usage only for newly selected utilities
            usage = get_usage(filters)
            print("  ✅  Filter and usage updated!")

        elif choice == "usage":
            usage = get_usage(filters)
            print("  ✅  Usage updated!")

        elif choice == "about":
            about_screen()

        elif choice == "quit":
            print()
            slow_print("  Thanks for using Utility Finder. Goodbye! 👋", delay=0.018)
            print()
            break

if __name__ == "__main__":
    main()
