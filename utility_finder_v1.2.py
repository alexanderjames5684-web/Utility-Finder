import time
import os
import csv
from datetime import datetime

# ─────────────────────────────────────────────
#   ASCII BANNER
# ─────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗                 ║
║   ██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝                 ║
║   ██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝                  ║
║   ██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝                   ║
║   ╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║                    ║
║    ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                    ║
║                                                                      ║
║    ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗                      ║
║    ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗                     ║
║    █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝                     ║
║    ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗                     ║
║    ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║                     ║
║    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝                     ║
║                                                                      ║
║          >>> Compare Electricity, Gas & Water Rates <<<              ║
║                    by ZIP Code  |  v1.2                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#   UTILITY DATABASE
#   Last updated: 2025-04
#   To update a rate: find the provider name and
#   change the number. Units: $/kWh, $/therm, $/1000 gal
# ─────────────────────────────────────────────

UTILITY_DB = {
    "4": [
        {"name": "FirstEnergy / Ohio Edison",  "elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "AEP Ohio",                   "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",        "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Toledo Edison",               "elec": 0.1280, "gas": 1.11, "water": 5.10, "phone": "1-800-447-3333"},
        {"name": "Toledo City Water",           "elec": None,   "gas": None, "water": 4.60, "phone": "419-936-2020"},
    ],
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
    "3": [
        {"name": "Duke Energy Florida",         "elec": 0.1190, "gas": 1.05, "water": 4.30, "phone": "1-800-700-8744"},
        {"name": "Florida Power & Light (FPL)", "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "Georgia Power",               "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "TECO Peoples Gas",            "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "JEA (Jacksonville)",          "elec": 0.1155, "gas": 1.08, "water": 4.15, "phone": "1-904-665-6000"},
    ],
    "7": [
        {"name": "Oncor Electric",              "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "CenterPoint Energy",          "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",               "elec": 0.1080, "gas": 0.92, "water": None, "phone": "1-800-968-8243"},
        {"name": "Texas Gas Service",           "elec": None,   "gas": 0.90, "water": None, "phone": "1-800-700-2443"},
        {"name": "City of Houston Water",       "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],
    "9": [
        {"name": "Pacific Gas & Electric (PG&E)","elec": 0.3100,"gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Southern California Edison",  "elec": 0.2850, "gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                    "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Gas & Electric",    "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "East Bay MUD",                "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
    ],
    "97": [
        {"name": "Portland General Electric",  "elec": 0.1250, "gas": 1.20, "water": 5.50, "phone": "1-800-542-8818"},
        {"name": "NW Natural Gas",             "elec": None,   "gas": 1.15, "water": None, "phone": "1-800-422-4012"},
        {"name": "Pacific Power",              "elec": 0.1190, "gas": None, "water": None, "phone": "1-888-221-7070"},
    ],
    "default": [
        {"name": "Generic National Electric Co.", "elec": 0.1400, "gas": 1.20, "water": 5.50, "phone": "N/A"},
        {"name": "National Gas Services",          "elec": None,   "gas": 1.18, "water": None, "phone": "N/A"},
        {"name": "American Water Works",           "elec": None,   "gas": None, "water": 5.80, "phone": "1-800-684-3256"},
    ],
}

UTILITY_CONFIG = {
    "elec":  {"label": "Electricity", "cost_key": "elec_cost",  "rate_key": "elec",  "unit": "kWh",    "default": 900,  "divisor": 1},
    "gas":   {"label": "Natural Gas", "cost_key": "gas_cost",   "rate_key": "gas",   "unit": "therms", "default": 50,   "divisor": 1},
    "water": {"label": "Water",       "cost_key": "water_cost", "rate_key": "water", "unit": "gal",    "default": 3000, "divisor": 1000},
}

ICONS = {"elec": "⚡", "gas": "🔥", "water": "💧"}

# ─────────────────────────────────────────────
#   SESSION HISTORY  ← v1.2
#   Stores the last search so it can be re-run
#   or saved without re-entering details.
# ─────────────────────────────────────────────

last_search = {
    "zip_code":  None,
    "results":   None,
    "filters":   None,
    "usage":     None,
    "timestamp": None,
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
        val = input(f"  {cfg['label']} usage ({cfg['unit']}) [{cfg['default']} {cfg['unit']}]: ").strip()
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

def pick_utility_filter():
    print()
    divider()
    slow_print("  Which utilities do you want to compare?", delay=0.015)
    divider()
    print("  [1]  All utilities  (Electricity + Gas + Water)")
    print("  [2]  Electricity only  ⚡")
    print("  [3]  Natural Gas only  🔥")
    print("  [4]  Water only  💧")
    print("  [5]  Custom combination — pick your own mix")
    divider()
    while True:
        choice = input("  Your choice [1-5]: ").strip()
        if choice == "1": return {"elec", "gas", "water"}
        elif choice == "2": return {"elec"}
        elif choice == "3": return {"gas"}
        elif choice == "4": return {"water"}
        elif choice == "5": return pick_custom_filter()
        else: print("  ⚠  Please enter a number from 1 to 5.")

def pick_custom_filter():
    print()
    slow_print("  CUSTOM FILTER — toggle on/off, then press S to save.", delay=0.013)
    selected = {"elec": True, "gas": True, "water": True}
    options  = [("elec", "Electricity ⚡"), ("gas", "Natural Gas 🔥"), ("water", "Water 💧")]
    while True:
        print()
        divider()
        for i, (key, label) in enumerate(options, 1):
            print(f"  [{i}]  {label:<20}  {'✅ ON' if selected[key] else '❌ OFF'}")
        divider()
        print("  [S]  Save and continue")
        raw = input("  Toggle [1/2/3] or Save [S]: ").strip().upper()
        if raw == "1":   selected["elec"]  = not selected["elec"]
        elif raw == "2": selected["gas"]   = not selected["gas"]
        elif raw == "3": selected["water"] = not selected["water"]
        elif raw == "S":
            active = {k for k, v in selected.items() if v}
            if not active: print("  ⚠  Keep at least one utility selected!")
            else: return active
        else: print("  ⚠  Invalid — press 1, 2, 3, or S.")

# ─────────────────────────────────────────────
#   BUILD RESULTS  (shared by display + save)
# ─────────────────────────────────────────────

def build_results(providers, usage, filters):
    results = []
    for p in providers:
        costs = {}
        for key in ["elec", "gas", "water"]:
            cfg = UTILITY_CONFIG[key]
            costs[cfg["cost_key"]] = get_monthly_cost(
                p[cfg["rate_key"]], usage[key], cfg["divisor"]
            ) if key in filters else None

        available      = [costs[UTILITY_CONFIG[k]["cost_key"]] for k in filters
                          if costs[UTILITY_CONFIG[k]["cost_key"]] is not None]
        results.append({**p, **costs,
                        "total":    sum(available),
                        "services": len(available)})

    results.sort(key=lambda x: (-x["services"], x["total"]))
    return results

# ─────────────────────────────────────────────
#   RESULTS DISPLAY
# ─────────────────────────────────────────────

def display_results(zip_code, providers, usage, filters):
    results = build_results(providers, usage, filters)

    # Cache for re-run / save
    last_search["zip_code"]  = zip_code
    last_search["results"]   = results
    last_search["filters"]   = filters
    last_search["usage"]     = usage
    last_search["timestamp"] = datetime.now()

    _print_results(zip_code, results, usage, filters)
    return results

def _print_results(zip_code, results, usage, filters):
    print()
    divider("═")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    slow_print(f"  📍  Results for ZIP Code: {zip_code}  |  Showing: {' + '.join(filter_labels)}", delay=0.013)
    divider("═")

    usage_parts = [f"{usage[k]:.0f} {UTILITY_CONFIG[k]['unit']} {UTILITY_CONFIG[k]['label'].lower()}"
                   for k in ["elec","gas","water"] if k in filters]
    print("  Usage: " + " | ".join(usage_parts))
    divider()

    col_w  = 34
    header = f"  {'PROVIDER':<{col_w}}"
    for key in ["elec","gas","water"]:
        if key in filters:
            header += f"  {(UTILITY_CONFIG[key]['label'].upper()[:9]+'/mo'):>11}"
    if len(filters) > 1:
        header += f"  {'TOTAL/mo':>10}"
    header += "  PHONE"
    print(header)
    divider()

    for r in results:
        row = f"  {r['name']:<{col_w}}"
        for key in ["elec","gas","water"]:
            if key not in filters: continue
            val = r[UTILITY_CONFIG[key]["cost_key"]]
            row += f"  ${val:>9.2f}" if val is not None else f"  {'N/A':>10}"
        if len(filters) > 1:
            row += f"  ${r['total']:>9.2f}" if r["services"] > 0 else f"  {'N/A':>10}"
        row += f"  {r['phone']}"
        print(row)

    divider()
    print("\n  🏆  CHEAPEST BY UTILITY:")
    for key in ["elec","gas","water"]:
        if key not in filters: continue
        cfg  = UTILITY_CONFIG[key]
        ckey = cfg["cost_key"]
        candidates = [r for r in results if r[ckey] is not None]
        if candidates:
            w = min(candidates, key=lambda x: x[ckey])
            print(f"     {ICONS[key]} {cfg['label']:<14} →  {w['name']}  (${w[ckey]:.2f}/mo)  📞 {w['phone']}")
        else:
            print(f"     {ICONS[key]} {cfg['label']:<14} →  No data for this region.")

    if len(filters) > 1:
        bundle = [r for r in results if r["services"] >= 2]
        if bundle:
            best = bundle[0]
            print(f"\n  💡  BEST BUNDLE ({best['services']} services):  {best['name']}")
            print(f"      Est. monthly total: ${best['total']:.2f}  📞 {best['phone']}")
    divider("═")

# ─────────────────────────────────────────────
#   SAVE & EXPORT  ← v1.2
# ─────────────────────────────────────────────

def save_menu():
    """Offer save options after (or instead of) a fresh search."""
    if last_search["results"] is None:
        print("\n  ⚠  No search results yet — run a search first!")
        return

    zip_code = last_search["zip_code"]
    results  = last_search["results"]
    filters  = last_search["filters"]
    usage    = last_search["usage"]
    ts       = last_search["timestamp"].strftime("%Y-%m-%d %H:%M")

    print()
    divider()
    slow_print("  SAVE / EXPORT  ← v1.2", delay=0.015)
    divider()
    print(f"  Last search: ZIP {zip_code}  |  {ts}")
    print()
    print("  [1]  Save as .txt  (readable report)")
    print("  [2]  Export as .csv  (open in Excel / Sheets)")
    print("  [3]  Re-display last results on screen")
    print("  [B]  Back to main menu")
    divider()

    choice = input("  Your choice: ").strip().upper()

    if choice == "1":
        save_txt(zip_code, results, filters, usage, ts)
    elif choice == "2":
        save_csv(zip_code, results, filters, usage, ts)
    elif choice == "3":
        _print_results(zip_code, results, usage, filters)
        input("\n  Press Enter to continue...")
    elif choice == "B":
        return
    else:
        print("  ⚠  Invalid choice.")


def _make_filename(zip_code, ext):
    """Build a timestamped filename in the current directory."""
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"utility_results_{zip_code}_{ts}.{ext}"
    return os.path.join(os.getcwd(), name)


def save_txt(zip_code, results, filters, usage, ts):
    path = _make_filename(zip_code, "txt")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    lines = []

    lines.append("=" * 72)
    lines.append("  UTILITY FINDER — Search Results")
    lines.append(f"  Generated : {ts}")
    lines.append(f"  ZIP Code  : {zip_code}")
    lines.append(f"  Utilities : {' + '.join(filter_labels)}")

    usage_parts = [f"{usage[k]:.0f} {UTILITY_CONFIG[k]['unit']} {UTILITY_CONFIG[k]['label'].lower()}"
                   for k in ["elec","gas","water"] if k in filters]
    lines.append(f"  Usage     : {' | '.join(usage_parts)}")
    lines.append("=" * 72)
    lines.append("")

    col_w = 34
    header = f"  {'PROVIDER':<{col_w}}"
    for key in ["elec","gas","water"]:
        if key in filters:
            header += f"  {(UTILITY_CONFIG[key]['label'].upper()[:9]+'/mo'):>11}"
    if len(filters) > 1:
        header += f"  {'TOTAL/mo':>10}"
    header += "  PHONE"
    lines.append(header)
    lines.append("-" * 72)

    for r in results:
        row = f"  {r['name']:<{col_w}}"
        for key in ["elec","gas","water"]:
            if key not in filters: continue
            val = r[UTILITY_CONFIG[key]["cost_key"]]
            row += f"  ${val:>9.2f}" if val is not None else f"  {'N/A':>10}"
        if len(filters) > 1:
            row += f"  ${r['total']:>9.2f}" if r["services"] > 0 else f"  {'N/A':>10}"
        row += f"  {r['phone']}"
        lines.append(row)

    lines.append("-" * 72)
    lines.append("")
    lines.append("  CHEAPEST BY UTILITY:")
    for key in ["elec","gas","water"]:
        if key not in filters: continue
        cfg  = UTILITY_CONFIG[key]
        ckey = cfg["cost_key"]
        candidates = [r for r in results if r[ckey] is not None]
        if candidates:
            w = min(candidates, key=lambda x: x[ckey])
            lines.append(f"  {ICONS[key]} {cfg['label']:<14} -> {w['name']}  (${w[ckey]:.2f}/mo)  {w['phone']}")

    if len(filters) > 1:
        bundle = [r for r in results if r["services"] >= 2]
        if bundle:
            best = bundle[0]
            lines.append("")
            lines.append(f"  BEST BUNDLE ({best['services']} services): {best['name']}")
            lines.append(f"  Est. monthly total: ${best['total']:.2f}  {best['phone']}")

    lines.append("")
    lines.append("  Rates are estimates. Always confirm directly with the provider.")
    lines.append("=" * 72)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  ✅  Saved: {path}")
    except OSError as e:
        print(f"\n  ❌  Could not save file: {e}")

    input("  Press Enter to continue...")


def save_csv(zip_code, results, filters, usage, ts):
    path = _make_filename(zip_code, "csv")

    # Build column headers dynamically
    base_cols  = ["Provider", "Phone"]
    rate_cols  = []
    cost_cols  = []
    for key in ["elec","gas","water"]:
        if key not in filters: continue
        cfg = UTILITY_CONFIG[key]
        rate_cols.append(f"{cfg['label']} Rate")
        cost_cols.append(f"{cfg['label']} $/mo")
    extra_cols = (["Total $/mo"] if len(filters) > 1 else []) + ["Services Offered"]
    meta_cols  = ["ZIP Code", "Search Date"]
    all_cols   = base_cols + rate_cols + cost_cols + extra_cols + meta_cols

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            writer.writeheader()

            for r in results:
                row = {
                    "Provider": r["name"],
                    "Phone":    r["phone"],
                    "ZIP Code": zip_code,
                    "Search Date": ts,
                    "Services Offered": r["services"],
                }
                if len(filters) > 1:
                    row["Total $/mo"] = f"{r['total']:.2f}" if r["services"] > 0 else "N/A"

                for key in ["elec","gas","water"]:
                    if key not in filters: continue
                    cfg  = UTILITY_CONFIG[key]
                    ckey = cfg["cost_key"]
                    rate = r.get(cfg["rate_key"])
                    cost = r[ckey]
                    row[f"{cfg['label']} Rate"]  = f"{rate:.4f}" if rate is not None else "N/A"
                    row[f"{cfg['label']} $/mo"]  = f"{cost:.2f}" if cost is not None else "N/A"

                writer.writerow(row)

        print(f"\n  ✅  Exported: {path}")
        print("      Open in Excel or Google Sheets — columns are already labelled.")
    except OSError as e:
        print(f"\n  ❌  Could not export file: {e}")

    input("  Press Enter to continue...")

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
    # Show both; last_search will hold zip2's results
    for z in [zip1, zip2]:
        display_results(z, get_providers_for_zip(z), usage, filters)

# ─────────────────────────────────────────────
#   ABOUT SCREEN
# ─────────────────────────────────────────────

def about_screen():
    print()
    divider("═")
    slow_print("  ℹ️   ABOUT UTILITY FINDER  v1.2", delay=0.02)
    divider("═")
    print("""
  What's new in v1.2:
  ───────────────────
  • Save results as a .txt report  — readable, shareable
  • Export results as .csv         — open straight in Excel or Sheets
  • Re-display last search         — no need to re-enter your ZIP
  • Files are saved in the same folder you run the program from,
    with a timestamp in the filename so nothing gets overwritten.

  What's in v1.1:
  ───────────────
  • Filter Mode — search one utility or any combination
  • Custom mix — toggle each utility on/off individually

  How rates are calculated:
  ─────────────────────────
  • Electricity  — $/kWh
  • Natural Gas  — $/therm  (≈ 100,000 BTU)
  • Water        — $/1,000 gallons

  Monthly cost = your usage × the provider's rate.

  Default usage (US national averages):
    Electricity: 900 kWh/mo  |  Gas: 50 therms/mo  |  Water: 3,000 gal/mo

  Data note:
  ──────────
  Rates are estimates. Always confirm with the provider before switching.
""")
    divider("═")
    input("  Press Enter to return to the menu...")

# ─────────────────────────────────────────────
#   MAIN MENU
# ─────────────────────────────────────────────

def main_menu(filters):
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    filter_str    = " + ".join(filter_labels)
    has_results   = last_search["results"] is not None

    while True:
        print()
        divider()
        slow_print("  MAIN MENU", delay=0.02)
        divider()
        print(f"  [1]  Find cheapest utilities for my ZIP code")
        print(f"         ↳ Filter: {filter_str}")
        print(f"  [2]  Compare two ZIP codes side-by-side")
        print(f"  [3]  Change utility filter")
        print(f"  [4]  Change usage amounts")
        print(f"  [5]  Save / Export results  ← NEW in v1.2"
              + (f"  (last: ZIP {last_search['zip_code']})" if has_results else "  (no results yet)"))
        print(f"  [6]  About / How rates work")
        print(f"  [Q]  Quit")
        divider()

        choice = input("  Your choice: ").strip().upper()
        if   choice == "1": return "single"
        elif choice == "2": return "compare"
        elif choice == "3": return "filter"
        elif choice == "4": return "usage"
        elif choice == "5": return "save"
        elif choice == "6": return "about"
        elif choice == "Q": return "quit"
        else: print("  ⚠  Invalid — enter 1–6 or Q.")

# ─────────────────────────────────────────────
#   ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print(BANNER)
    time.sleep(0.3)
    slow_print("  Welcome to Utility Finder v1.2!", delay=0.018)
    slow_print("  Now with save & export — keep your results forever.", delay=0.016)

    filters = pick_utility_filter()
    usage   = get_usage(filters)

    while True:
        choice = main_menu(filters)

        if choice == "single":
            zip_code  = get_zip()
            display_results(zip_code, get_providers_for_zip(zip_code), usage, filters)
            print("\n  Tip: use option [5] to save or export these results.")
            input("  Press Enter to return to the menu...")

        elif choice == "compare":
            compare_mode(usage, filters)
            input("\n  Press Enter to return to the menu...")

        elif choice == "filter":
            filters = pick_utility_filter()
            usage   = get_usage(filters)
            print("  ✅  Filter and usage updated!")

        elif choice == "usage":
            usage = get_usage(filters)
            print("  ✅  Usage updated!")

        elif choice == "save":
            save_menu()

        elif choice == "about":
            about_screen()

        elif choice == "quit":
            print()
            slow_print("  Thanks for using Utility Finder. Goodbye! 👋", delay=0.018)
            print()
            break

if __name__ == "__main__":
    main()
