import time
import random

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
║                    by ZIP Code  |  v1.0                             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#   SIMULATED UTILITY DATABASE
#   (Structured by ZIP code prefix / region)
#   Rates are realistic estimates for illustration.
#   In a real app you'd pull from a live API.
# ─────────────────────────────────────────────

# Each provider entry:
#   name, electricity ($/kWh), gas ($/therm), water ($/1000 gal), phone

UTILITY_DB = {
    # ── Midwest (OH, MI, IN) ─────────────────
    "4": [
        {"name": "FirstEnergy / Ohio Edison",  "elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "AEP Ohio",                   "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",        "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Toledo Edison",               "elec": 0.1280, "gas": 1.11, "water": 5.10, "phone": "1-800-447-3333"},
        {"name": "Toledo City Water",           "elec": None,   "gas": None, "water": 4.60, "phone": "419-936-2020"},
    ],
    # ── Northeast (NY, NJ, CT, MA) ───────────
    "0": [
        {"name": "Eversource Energy",           "elec": 0.2210, "gas": 1.45, "water": 7.80, "phone": "1-800-286-2000"},
        {"name": "National Grid",               "elec": 0.2050, "gas": 1.38, "water": 7.20, "phone": "1-800-642-4272"},
        {"name": "UI (United Illuminating)",    "elec": 0.2380, "gas": None, "water": None, "phone": "1-800-722-5584"},
        {"name": "Aquarion Water Company",      "elec": None,   "gas": None, "water": 8.10, "phone": "1-800-732-9678"},
    ],
    "1": [
        {"name": "Con Edison",                  "elec": 0.2340, "gas": 1.52, "water": 9.10, "phone": "1-800-752-6633"},
        {"name": "Orange & Rockland",           "elec": 0.2100, "gas": 1.44, "water": 8.50, "phone": "1-877-434-4100"},
        {"name": "New York American Water",     "elec": None,   "gas": None, "water": 8.90, "phone": "1-877-426-6999"},
        {"name": "PSE&G (NJ)",                  "elec": 0.1680, "gas": 1.30, "water": 6.70, "phone": "1-800-436-7734"},
    ],
    # ── Southeast (FL, GA, SC, NC) ───────────
    "3": [
        {"name": "Duke Energy Florida",         "elec": 0.1190, "gas": 1.05, "water": 4.30, "phone": "1-800-700-8744"},
        {"name": "Florida Power & Light (FPL)", "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "Georgia Power",               "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "TECO Peoples Gas",            "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "JEA (Jacksonville)",          "elec": 0.1155, "gas": 1.08, "water": 4.15, "phone": "1-904-665-6000"},
    ],
    # ── South / TX ───────────────────────────
    "7": [
        {"name": "Oncor Electric",              "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "CenterPoint Energy",          "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",               "elec": 0.1080, "gas": 0.92, "water": None, "phone": "1-800-968-8243"},
        {"name": "Texas Gas Service",           "elec": None,   "gas": 0.90, "water": None, "phone": "1-800-700-2443"},
        {"name": "City of Houston Water",       "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],
    # ── West / CA ────────────────────────────
    "9": [
        {"name": "Pacific Gas & Electric (PG&E)","elec": 0.3100,"gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Southern California Edison",  "elec": 0.2850, "gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                    "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Gas & Electric",    "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "East Bay MUD",                "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
    ],
    # ── Pacific NW ───────────────────────────
    "97": [
        {"name": "Portland General Electric",  "elec": 0.1250, "gas": 1.20, "water": 5.50, "phone": "1-800-542-8818"},
        {"name": "NW Natural Gas",             "elec": None,   "gas": 1.15, "water": None, "phone": "1-800-422-4012"},
        {"name": "Pacific Power",              "elec": 0.1190, "gas": None, "water": None, "phone": "1-888-221-7070"},
    ],
    # ── Default fallback ─────────────────────
    "default": [
        {"name": "Generic National Electric Co.", "elec": 0.1400, "gas": 1.20, "water": 5.50, "phone": "N/A"},
        {"name": "National Gas Services",          "elec": None,   "gas": 1.18, "water": None, "phone": "N/A"},
        {"name": "American Water Works",           "elec": None,   "gas": None, "water": 5.80, "phone": "1-800-684-3256"},
    ],
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
    """Return provider list matched to ZIP prefix (longest match wins)."""
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in UTILITY_DB:
            return UTILITY_DB[prefix]
    return UTILITY_DB["default"]

def get_monthly_estimate(rate_per_unit, units):
    """Return monthly cost or None if rate unavailable."""
    if rate_per_unit is None:
        return None
    return rate_per_unit * units

def rate_str(value, unit):
    if value is None:
        return "  N/A          "
    return f"  ${value:.4f}/{unit}"

def cost_str(value):
    if value is None:
        return "    N/A   "
    return f"  ${value:>7.2f}"

# ─────────────────────────────────────────────
#   INPUT COLLECTION
# ─────────────────────────────────────────────

def get_zip():
    while True:
        z = input("\n  Enter your ZIP code: ").strip()
        if z.isdigit() and len(z) == 5:
            return z
        print("  ⚠  Please enter a valid 5-digit ZIP code.")

def get_usage():
    print()
    divider()
    slow_print("  Enter your average MONTHLY usage (press Enter to use defaults):")
    divider()

    def ask_usage(label, default, unit):
        val = input(f"  {label} [{default} {unit}]: ").strip()
        if val == "":
            return default
        try:
            v = float(val)
            if v < 0:
                raise ValueError
            return v
        except ValueError:
            print(f"  ⚠  Invalid — using default ({default} {unit}).")
            return default

    elec_kwh  = ask_usage("Electricity usage (kWh)", 900,   "kWh")
    gas_therm = ask_usage("Natural gas usage (therms)", 50, "therms")
    water_gal = ask_usage("Water usage (gallons)",  3000,   "gal")

    return elec_kwh, gas_therm, water_gal

# ─────────────────────────────────────────────
#   RESULTS DISPLAY
# ─────────────────────────────────────────────

def display_results(zip_code, providers, elec_kwh, gas_therm, water_gal):
    print()
    divider("═")
    slow_print(f"  📍  Results for ZIP Code: {zip_code}", delay=0.015)
    divider("═")
    print(f"  Usage assumed: {elec_kwh:.0f} kWh electricity | "
          f"{gas_therm:.0f} therms gas | {water_gal:.0f} gal water")
    divider()

    results = []
    for p in providers:
        elec_cost  = get_monthly_estimate(p["elec"],  elec_kwh)
        gas_cost   = get_monthly_estimate(p["gas"],   gas_therm)
        water_cost = get_monthly_estimate(p["water"], water_gal / 1000)  # per 1k gal

        # Total only counts services the provider offers
        total = sum(c for c in [elec_cost, gas_cost, water_cost] if c is not None)
        services = sum(1 for c in [elec_cost, gas_cost, water_cost] if c is not None)

        results.append({**p,
                        "elec_cost":  elec_cost,
                        "gas_cost":   gas_cost,
                        "water_cost": water_cost,
                        "total":      total,
                        "services":   services})

    # Sort: providers with more services first, then by total cost
    results.sort(key=lambda x: (-x["services"], x["total"]))

    col_w = 34
    print(f"\n  {'PROVIDER':<{col_w}} {'ELEC/mo':>10}  {'GAS/mo':>10}  {'WATER/mo':>10}  {'TOTAL':>10}  PHONE")
    divider()

    best_by = {"elec": None, "gas": None, "water": None}

    for r in results:
        flag = ""
        print(f"  {r['name']:<{col_w}} "
              f"{'N/A':>10}" if r['elec_cost'] is None else "", end="")
        # Rebuild cleanly
        ec  = f"${r['elec_cost']:>8.2f}"  if r['elec_cost']  is not None else "       N/A"
        gc  = f"${r['gas_cost']:>8.2f}"   if r['gas_cost']   is not None else "       N/A"
        wc  = f"${r['water_cost']:>8.2f}" if r['water_cost'] is not None else "       N/A"
        tot = f"${r['total']:>8.2f}"

        print(f"\r  {r['name']:<{col_w}} {ec:>10}  {gc:>10}  {wc:>10}  {tot:>10}  {r['phone']}")

    divider()

    # ── Winners per category ──
    def cheapest(key):
        candidates = [r for r in results if r[key] is not None]
        if not candidates:
            return None
        return min(candidates, key=lambda x: x[key])

    print("\n  🏆  CHEAPEST BY CATEGORY:")
    for label, key in [("Electricity", "elec_cost"), ("Gas", "gas_cost"), ("Water", "water_cost")]:
        winner = cheapest(key)
        if winner:
            print(f"     {label:12s} →  {winner['name']}  "
                  f"(${winner[key]:.2f}/mo)  📞 {winner['phone']}")
        else:
            print(f"     {label:12s} →  No data available for this region.")

    # ── Overall best bundle ──
    bundle_candidates = [r for r in results if r["services"] >= 2]
    if bundle_candidates:
        best = bundle_candidates[0]
        print(f"\n  💡  BEST BUNDLE ({best['services']} services):  {best['name']}")
        print(f"      Estimated monthly total: ${best['total']:.2f}  📞 {best['phone']}")

    divider("═")

# ─────────────────────────────────────────────
#   COMPARE MODE (two ZIPs)
# ─────────────────────────────────────────────

def compare_mode(elec_kwh, gas_therm, water_gal):
    print()
    divider()
    slow_print("  COMPARISON MODE — Enter two ZIP codes to compare regions.")
    divider()
    zip1 = get_zip()
    zip2 = get_zip()

    for z in [zip1, zip2]:
        providers = get_providers_for_zip(z)
        display_results(z, providers, elec_kwh, gas_therm, water_gal)

# ─────────────────────────────────────────────
#   MAIN MENU
# ─────────────────────────────────────────────

def main_menu():
    while True:
        print()
        divider()
        slow_print("  MAIN MENU", delay=0.02)
        divider()
        print("  [1]  Find cheapest utilities for my ZIP code")
        print("  [2]  Compare two ZIP codes side-by-side")
        print("  [3]  Change usage amounts")
        print("  [4]  About / How rates work")
        print("  [Q]  Quit")
        divider()

        choice = input("  Your choice: ").strip().upper()

        if choice == "1":
            return "single"
        elif choice == "2":
            return "compare"
        elif choice == "3":
            return "usage"
        elif choice == "4":
            return "about"
        elif choice == "Q":
            return "quit"
        else:
            print("  ⚠  Invalid choice — please enter 1, 2, 3, 4, or Q.")

def about_screen():
    print()
    divider("═")
    slow_print("  ℹ️   ABOUT UTILITY FINDER", delay=0.02)
    divider("═")
    print("""
  How rates are calculated:
  ─────────────────────────
  • Electricity  — cents per kilowatt-hour (kWh)
  • Natural Gas  — dollars per therm (≈ 100,000 BTU)
  • Water        — dollars per 1,000 gallons

  Monthly cost = your usage × the provider's rate.

  Averages used if you skip custom usage input:
    • Electricity : 900 kWh   (US household avg ~900 kWh/mo)
    • Gas         :  50 therms (US avg ~50 therms/mo)
    • Water       : 3,000 gal  (US avg ~3,000 gal/mo)

  Data note:
  ──────────
  Rates shown are representative estimates based on publicly
  reported utility tariffs and EIA data. Actual bills will
  vary based on your specific plan, time-of-use pricing,
  taxes, fees, and seasonal adjustments. Always confirm
  rates directly with the provider before switching.

  Contact the provider via the phone numbers shown for
  an exact quote or to start service.
""")
    divider("═")
    input("  Press Enter to return to the menu...")

# ─────────────────────────────────────────────
#   ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print(BANNER)
    time.sleep(0.3)
    slow_print("  Welcome! Let's find the cheapest utilities in your area.", delay=0.018)

    # Initial usage setup
    elec_kwh, gas_therm, water_gal = get_usage()

    while True:
        choice = main_menu()

        if choice == "single":
            zip_code  = get_zip()
            providers = get_providers_for_zip(zip_code)
            display_results(zip_code, providers, elec_kwh, gas_therm, water_gal)
            input("\n  Press Enter to return to the menu...")

        elif choice == "compare":
            compare_mode(elec_kwh, gas_therm, water_gal)
            input("\n  Press Enter to return to the menu...")

        elif choice == "usage":
            elec_kwh, gas_therm, water_gal = get_usage()
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
