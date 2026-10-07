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
║                    by ZIP Code  |  v1.3                             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#   REGION MAP  ← v1.3
#   Maps ZIP prefix → human-readable region name
#   Used in the region browser and result headers
# ─────────────────────────────────────────────

REGION_NAMES = {
    # ── 0xx ──────────────────────────────────
    "0":   "Northeast — CT, MA, RI, VT, NH, ME",
    # ── 1xx ──────────────────────────────────
    "1":   "New York & New Jersey",
    # ── 2xx ──────────────────────────────────
    "20":  "Washington D.C. & Northern Virginia",
    "21":  "Maryland",
    "22":  "Northern Virginia",
    "23":  "Virginia",
    "24":  "West Virginia & Southwest Virginia",
    "25":  "West Virginia",
    "26":  "West Virginia",
    "27":  "North Carolina",
    "28":  "North Carolina",
    "29":  "South Carolina",
    # ── 3xx ──────────────────────────────────
    "30":  "Georgia — Atlanta metro",
    "31":  "Georgia",
    "32":  "Florida — Central & North",
    "33":  "Florida — South & Miami",
    "34":  "Florida — West Coast",
    "35":  "Alabama",
    "36":  "Alabama",
    "37":  "Tennessee",
    "38":  "Tennessee & Mississippi",
    "39":  "Mississippi",
    # ── 4xx ──────────────────────────────────
    "40":  "Kentucky — Louisville",
    "41":  "Kentucky",
    "42":  "Kentucky",
    "43":  "Ohio — Columbus & Central",
    "44":  "Ohio — Cleveland & Northeast",
    "45":  "Ohio — Cincinnati",
    "46":  "Indiana — Indianapolis",
    "47":  "Indiana",
    "48":  "Michigan — Detroit & Southeast",
    "49":  "Michigan — West & Upper Peninsula",
    # ── 5xx ──────────────────────────────────
    "5":   "Midwest — IA, MN, WI, SD, ND, NE, KS",
    # ── 6xx ──────────────────────────────────
    "60":  "Illinois — Chicago metro",
    "61":  "Illinois — Central",
    "62":  "Illinois — Southern",
    "63":  "Missouri — St. Louis",
    "64":  "Missouri — Kansas City",
    "65":  "Missouri",
    "66":  "Kansas",
    "67":  "Kansas",
    "68":  "Nebraska",
    "69":  "Nebraska — Panhandle",
    # ── 7xx ──────────────────────────────────
    "70":  "Louisiana — New Orleans",
    "71":  "Louisiana — North",
    "72":  "Arkansas",
    "73":  "Oklahoma — Oklahoma City",
    "74":  "Oklahoma — Tulsa",
    "75":  "Texas — Dallas & North Texas",
    "76":  "Texas — Fort Worth",
    "77":  "Texas — Houston",
    "78":  "Texas — San Antonio & Central",
    "79":  "Texas — West Texas & El Paso",
    # ── 8xx ──────────────────────────────────
    "80":  "Colorado — Denver",
    "81":  "Colorado — Western",
    "82":  "Wyoming",
    "83":  "Idaho & Wyoming",
    "84":  "Utah",
    "85":  "Arizona — Phoenix",
    "86":  "Arizona — Northern",
    "87":  "New Mexico",
    "88":  "New Mexico & West Texas",
    "89":  "Nevada",
    # ── 9xx ──────────────────────────────────
    "90":  "California — Los Angeles",
    "91":  "California — Los Angeles & San Fernando Valley",
    "92":  "California — San Diego & Inland Empire",
    "93":  "California — Central Valley & Fresno",
    "94":  "California — San Francisco Bay Area",
    "95":  "California — Sacramento & Northern CA",
    "96":  "California — Far North & Hawaii",
    "97":  "Oregon",
    "98":  "Washington State",
    "99":  "Washington State — Eastern & Alaska",
}

# ─────────────────────────────────────────────
#   UTILITY DATABASE  ← v1.3: greatly expanded
#   Last updated: 2025-04
#   Units: elec=$/kWh  gas=$/therm  water=$/1000gal
# ─────────────────────────────────────────────

UTILITY_DB = {

    # ════════════════════════════════════════
    #   0xx — NORTHEAST (CT, MA, RI, VT, NH, ME)
    # ════════════════════════════════════════
    "0": [
        {"name": "Eversource Energy",        "elec": 0.2210, "gas": 1.45, "water": 7.80, "phone": "1-800-286-2000"},
        {"name": "National Grid",             "elec": 0.2050, "gas": 1.38, "water": 7.20, "phone": "1-800-642-4272"},
        {"name": "UI (United Illuminating)",  "elec": 0.2380, "gas": None, "water": None, "phone": "1-800-722-5584"},
        {"name": "Aquarion Water Company",    "elec": None,   "gas": None, "water": 8.10, "phone": "1-800-732-9678"},
        {"name": "Liberty Utilities (NH/ME)", "elec": 0.1980, "gas": 1.42, "water": 7.50, "phone": "1-800-375-7413"},
        {"name": "Green Mountain Power (VT)", "elec": 0.2010, "gas": None, "water": None, "phone": "1-888-835-4672"},
    ],

    # ════════════════════════════════════════
    #   1xx — NEW YORK & NEW JERSEY
    # ════════════════════════════════════════
    "1": [
        {"name": "Con Edison",               "elec": 0.2340, "gas": 1.52, "water": 9.10, "phone": "1-800-752-6633"},
        {"name": "Orange & Rockland",        "elec": 0.2100, "gas": 1.44, "water": 8.50, "phone": "1-877-434-4100"},
        {"name": "New York American Water",  "elec": None,   "gas": None, "water": 8.90, "phone": "1-877-426-6999"},
        {"name": "PSE&G (NJ)",               "elec": 0.1680, "gas": 1.30, "water": 6.70, "phone": "1-800-436-7734"},
        {"name": "JCP&L (NJ)",               "elec": 0.1590, "gas": None, "water": None, "phone": "1-800-662-3115"},
        {"name": "New Jersey American Water","elec": None,   "gas": None, "water": 7.10, "phone": "1-800-652-6987"},
        {"name": "NYSEG",                    "elec": 0.1870, "gas": 1.35, "water": None, "phone": "1-800-572-1111"},
        {"name": "Central Hudson (NY)",      "elec": 0.2010, "gas": 1.40, "water": None, "phone": "1-845-452-2700"},
    ],

    # ════════════════════════════════════════
    #   20x — DC & NORTHERN VIRGINIA
    # ════════════════════════════════════════
    "20": [
        {"name": "Pepco (DC/MD)",            "elec": 0.1420, "gas": None, "water": None, "phone": "1-202-833-7500"},
        {"name": "Washington Gas",           "elec": None,   "gas": 1.18, "water": None, "phone": "1-844-927-4427"},
        {"name": "DC Water",                 "elec": None,   "gas": None, "water": 8.20, "phone": "202-354-3600"},
        {"name": "Dominion Energy VA",       "elec": 0.1260, "gas": 1.12, "water": None, "phone": "1-866-366-4357"},
    ],

    # ════════════════════════════════════════
    #   21x — MARYLAND
    # ════════════════════════════════════════
    "21": [
        {"name": "BGE (Baltimore Gas & Elec)","elec": 0.1380,"gas": 1.15, "water": 6.40, "phone": "1-800-685-0123"},
        {"name": "Delmarva Power",           "elec": 0.1490, "gas": None, "water": None, "phone": "1-800-375-7117"},
        {"name": "Washington Suburban Sanitary","elec": None,"gas": None, "water": 7.30, "phone": "301-206-8000"},
        {"name": "Washington Gas",           "elec": None,   "gas": 1.18, "water": None, "phone": "1-844-927-4427"},
    ],

    # ════════════════════════════════════════
    #   23x/24x — VIRGINIA
    # ════════════════════════════════════════
    "23": [
        {"name": "Dominion Energy VA",       "elec": 0.1260, "gas": 1.12, "water": 5.80, "phone": "1-866-366-4357"},
        {"name": "Virginia Natural Gas",     "elec": None,   "gas": 1.08, "water": None, "phone": "1-866-229-1929"},
        {"name": "Hampton Roads Sanitation", "elec": None,   "gas": None, "water": 5.20, "phone": "757-460-7000"},
    ],
    "24": [
        {"name": "Appalachian Power (WV/VA)","elec": 0.1180, "gas": 1.05, "water": 4.90, "phone": "1-800-956-4237"},
        {"name": "Mountaineer Gas (WV)",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-858-3272"},
    ],

    # ════════════════════════════════════════
    #   27x/28x — NORTH CAROLINA
    # ════════════════════════════════════════
    "27": [
        {"name": "Duke Energy Carolinas",    "elec": 0.1210, "gas": 1.08, "water": 5.10, "phone": "1-800-777-9898"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "PSNC Energy",              "elec": None,   "gas": 1.07, "water": None, "phone": "1-877-776-2427"},
        {"name": "Raleigh Water",            "elec": None,   "gas": None, "water": 4.80, "phone": "919-996-3245"},
    ],
    "28": [
        {"name": "Duke Energy Progress",     "elec": 0.1230, "gas": None, "water": None, "phone": "1-800-452-2777"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "Charlotte Water",          "elec": None,   "gas": None, "water": 4.90, "phone": "704-336-7600"},
    ],

    # ════════════════════════════════════════
    #   29x — SOUTH CAROLINA
    # ════════════════════════════════════════
    "29": [
        {"name": "Dominion Energy SC",       "elec": 0.1350, "gas": 1.12, "water": None, "phone": "1-800-251-7234"},
        {"name": "Duke Energy Carolinas",    "elec": 0.1210, "gas": None, "water": None, "phone": "1-800-777-9898"},
        {"name": "Columbia Water (SC)",      "elec": None,   "gas": None, "water": 4.70, "phone": "803-545-3300"},
    ],

    # ════════════════════════════════════════
    #   30x/31x — GEORGIA
    # ════════════════════════════════════════
    "30": [
        {"name": "Georgia Power",            "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "Atlanta Gas Light",        "elec": None,   "gas": 1.08, "water": None, "phone": "1-770-994-1946"},
        {"name": "City of Atlanta Watershed","elec": None,   "gas": None, "water": 5.30, "phone": "404-546-0311"},
    ],
    "31": [
        {"name": "Georgia Power",            "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "Atlanta Gas Light",        "elec": None,   "gas": 1.08, "water": None, "phone": "1-770-994-1946"},
    ],

    # ════════════════════════════════════════
    #   32x/34x — FLORIDA CENTRAL & WEST COAST
    # ════════════════════════════════════════
    "32": [
        {"name": "Duke Energy Florida",      "elec": 0.1190, "gas": 1.05, "water": 4.30, "phone": "1-800-700-8744"},
        {"name": "Florida Public Utilities", "elec": None,   "gas": 1.03, "water": None, "phone": "1-800-427-7712"},
        {"name": "JEA (Jacksonville)",       "elec": 0.1155, "gas": 1.08, "water": 4.15, "phone": "1-904-665-6000"},
    ],
    "33": [
        {"name": "Florida Power & Light",    "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "TECO Peoples Gas",         "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "Miami-Dade Water & Sewer", "elec": None,   "gas": None, "water": 5.60, "phone": "305-665-7477"},
    ],
    "34": [
        {"name": "Florida Power & Light",    "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "TECO Peoples Gas",         "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "Sarasota County Utilities","elec": None,   "gas": None, "water": 4.50, "phone": "941-861-6790"},
    ],

    # ════════════════════════════════════════
    #   35x/36x — ALABAMA
    # ════════════════════════════════════════
    "35": [
        {"name": "Alabama Power",            "elec": 0.1310, "gas": 1.09, "water": 4.80, "phone": "1-800-245-2244"},
        {"name": "Alagasco (Spire Alabama)", "elec": None,   "gas": 1.06, "water": None, "phone": "1-800-292-4008"},
        {"name": "Birmingham Water Works",   "elec": None,   "gas": None, "water": 4.40, "phone": "205-244-4000"},
    ],
    "36": [
        {"name": "Alabama Power",            "elec": 0.1310, "gas": 1.09, "water": 4.80, "phone": "1-800-245-2244"},
        {"name": "Alagasco (Spire Alabama)", "elec": None,   "gas": 1.06, "water": None, "phone": "1-800-292-4008"},
    ],

    # ════════════════════════════════════════
    #   37x/38x — TENNESSEE
    # ════════════════════════════════════════
    "37": [
        {"name": "Nashville Electric Service","elec": 0.1080,"gas": None, "water": None, "phone": "615-736-6900"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "Metro Water Services (Nashville)","elec":None,"gas":None,"water":4.35, "phone": "615-862-4600"},
        {"name": "Memphis Light Gas & Water","elec": 0.1020, "gas": 1.01, "water": 4.10, "phone": "901-544-6549"},
    ],
    "38": [
        {"name": "Memphis Light Gas & Water","elec": 0.1020, "gas": 1.01, "water": 4.10, "phone": "901-544-6549"},
        {"name": "Entergy Mississippi",      "elec": 0.1120, "gas": None, "water": None, "phone": "1-800-368-3749"},
    ],

    # ════════════════════════════════════════
    #   40x-42x — KENTUCKY
    # ════════════════════════════════════════
    "40": [
        {"name": "LG&E (Louisville Gas & Elec)","elec":0.1150,"gas":1.05,"water":4.60, "phone": "502-589-1444"},
        {"name": "Louisville Water Company", "elec": None,   "gas": None, "water": 4.20, "phone": "502-583-6610"},
    ],
    "41": [
        {"name": "Kentucky Power (AEP)",     "elec": 0.1220, "gas": 1.08, "water": 4.70, "phone": "1-800-572-1113"},
        {"name": "Columbia Gas of Kentucky", "elec": None,   "gas": 1.04, "water": None, "phone": "1-800-432-9515"},
    ],

    # ════════════════════════════════════════
    #   43x-45x — OHIO (expanded from v1.x)
    # ════════════════════════════════════════
    "43": [
        {"name": "AEP Ohio",                 "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Columbus Division of Water","elec":None,   "gas": None, "water": 4.80, "phone": "614-645-7788"},
    ],
    "44": [
        {"name": "FirstEnergy / Ohio Edison","elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "Dominion Energy Ohio (gas)","elec":None,   "gas": 1.06, "water": None, "phone": "1-800-362-7557"},
        {"name": "Cleveland Water",          "elec": None,   "gas": None, "water": 4.95, "phone": "216-664-3060"},
    ],
    "45": [
        {"name": "Duke Energy Ohio",         "elec": 0.1210, "gas": 1.09, "water": 5.00, "phone": "1-800-544-6900"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Greater Cincinnati Water", "elec": None,   "gas": None, "water": 4.75, "phone": "513-591-7700"},
    ],
    # Keep old "4" prefix as broader Midwest fallback for
    # 46x/47x/48x/49x that don't have their own entry yet
    "4": [
        {"name": "FirstEnergy / Ohio Edison","elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "AEP Ohio",                 "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Indiana Michigan Power",   "elec": 0.1230, "gas": 1.10, "water": 5.00, "phone": "1-800-311-4634"},
        {"name": "Consumers Energy (MI)",    "elec": 0.1680, "gas": 1.14, "water": None, "phone": "1-800-477-5050"},
        {"name": "DTE Energy (MI)",          "elec": 0.1790, "gas": 1.18, "water": None, "phone": "1-800-477-4747"},
    ],

    # ════════════════════════════════════════
    #   5xx — UPPER MIDWEST (MN, WI, IA, ND, SD, NE, KS)
    # ════════════════════════════════════════
    "5": [
        {"name": "Xcel Energy (MN/ND/SD)",   "elec": 0.1320, "gas": 1.10, "water": 5.30, "phone": "1-800-895-4999"},
        {"name": "MidAmerican Energy (IA)",  "elec": 0.1050, "gas": 0.98, "water": None, "phone": "1-888-427-5632"},
        {"name": "We Energies (WI)",         "elec": 0.1850, "gas": 1.20, "water": 6.10, "phone": "1-800-242-9137"},
        {"name": "Alliant Energy (IA/WI)",   "elec": 0.1280, "gas": 1.05, "water": None, "phone": "1-800-255-4268"},
        {"name": "Black Hills Energy (KS/NE)","elec":0.1150, "gas": 0.97, "water": None, "phone": "1-888-890-5554"},
        {"name": "Minneapolis Water",        "elec": None,   "gas": None, "water": 5.60, "phone": "612-673-3000"},
    ],

    # ════════════════════════════════════════
    #   60x-62x — ILLINOIS
    # ════════════════════════════════════════
    "60": [
        {"name": "ComEd (Chicago)",          "elec": 0.1620, "gas": None, "water": None, "phone": "1-800-334-7661"},
        {"name": "Peoples Gas (Chicago)",    "elec": None,   "gas": 1.28, "water": None, "phone": "1-866-556-6004"},
        {"name": "City of Chicago Water",    "elec": None,   "gas": None, "water": 6.50, "phone": "312-744-7038"},
        {"name": "North Shore Gas",          "elec": None,   "gas": 1.25, "water": None, "phone": "1-866-556-6004"},
    ],
    "61": [
        {"name": "Ameren Illinois",          "elec": 0.1490, "gas": 1.20, "water": 5.80, "phone": "1-800-755-5000"},
    ],
    "62": [
        {"name": "Ameren Illinois",          "elec": 0.1490, "gas": 1.20, "water": 5.80, "phone": "1-800-755-5000"},
    ],
    "6": [
        {"name": "Ameren Illinois",          "elec": 0.1490, "gas": 1.20, "water": 5.80, "phone": "1-800-755-5000"},
        {"name": "Spire Missouri",           "elec": None,   "gas": 1.16, "water": None, "phone": "1-800-582-1234"},
        {"name": "Evergy (KS/MO)",           "elec": 0.1380, "gas": 1.08, "water": None, "phone": "1-888-471-5275"},
    ],

    # ════════════════════════════════════════
    #   70x-79x — SOUTH & TEXAS (expanded from v1.x)
    # ════════════════════════════════════════
    "70": [
        {"name": "Entergy Louisiana",        "elec": 0.1050, "gas": 0.94, "water": 3.90, "phone": "1-800-368-3749"},
        {"name": "Atmos Energy (LA)",        "elec": None,   "gas": 0.92, "water": None, "phone": "1-888-286-6700"},
        {"name": "Sewerage & Water Board NO","elec": None,   "gas": None, "water": 3.70, "phone": "504-529-2837"},
    ],
    "72": [
        {"name": "Entergy Arkansas",         "elec": 0.1020, "gas": 0.93, "water": 3.80, "phone": "1-800-368-3749"},
        {"name": "Arkansas Oklahoma Gas",    "elec": None,   "gas": 0.91, "water": None, "phone": "1-800-880-9267"},
        {"name": "Central Arkansas Water",   "elec": None,   "gas": None, "water": 3.50, "phone": "501-372-5161"},
    ],
    "73": [
        {"name": "OG&E (Oklahoma City)",     "elec": 0.1140, "gas": 0.96, "water": 4.10, "phone": "405-272-9741"},
        {"name": "Oklahoma Natural Gas",     "elec": None,   "gas": 0.94, "water": None, "phone": "1-800-664-5463"},
        {"name": "Oklahoma City Water",      "elec": None,   "gas": None, "water": 3.80, "phone": "405-297-2833"},
    ],
    "75": [
        {"name": "Oncor Electric (DFW)",     "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "Atmos Energy (TX)",        "elec": None,   "gas": 0.90, "water": None, "phone": "1-888-286-6700"},
        {"name": "Dallas Water Utilities",   "elec": None,   "gas": None, "water": 3.90, "phone": "214-651-1441"},
    ],
    "77": [
        {"name": "CenterPoint Energy",       "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",            "elec": 0.1080, "gas": None, "water": None, "phone": "1-800-968-8243"},
        {"name": "City of Houston Water",    "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],
    "78": [
        {"name": "CPS Energy (San Antonio)", "elec": 0.1010, "gas": 0.93, "water": 3.70, "phone": "210-353-2222"},
        {"name": "San Antonio Water System", "elec": None,   "gas": None, "water": 3.50, "phone": "210-704-7297"},
    ],
    "7": [
        {"name": "Oncor Electric",           "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "CenterPoint Energy",       "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",            "elec": 0.1080, "gas": 0.92, "water": None, "phone": "1-800-968-8243"},
        {"name": "Texas Gas Service",        "elec": None,   "gas": 0.90, "water": None, "phone": "1-800-700-2443"},
        {"name": "City of Houston Water",    "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],

    # ════════════════════════════════════════
    #   80x-89x — MOUNTAIN WEST
    # ════════════════════════════════════════
    "80": [
        {"name": "Xcel Energy (CO)",         "elec": 0.1410, "gas": 1.08, "water": 5.40, "phone": "1-800-895-4999"},
        {"name": "Black Hills Energy (CO)",  "elec": 0.1320, "gas": 1.02, "water": None, "phone": "1-888-890-5554"},
        {"name": "Denver Water",             "elec": None,   "gas": None, "water": 5.10, "phone": "720-944-3751"},
    ],
    "81": [
        {"name": "Xcel Energy (CO)",         "elec": 0.1410, "gas": 1.08, "water": 5.40, "phone": "1-800-895-4999"},
        {"name": "Atmos Energy (CO)",        "elec": None,   "gas": 1.05, "water": None, "phone": "1-888-286-6700"},
    ],
    "84": [
        {"name": "Rocky Mountain Power (UT)","elec": 0.1180, "gas": 1.06, "water": 5.20, "phone": "1-888-221-7070"},
        {"name": "Questar Gas (Dominion UT)","elec": None,   "gas": 1.03, "water": None, "phone": "1-800-323-5517"},
        {"name": "Salt Lake City Public Utils","elec":None,  "gas": None, "water": 4.90, "phone": "801-483-6900"},
    ],
    "85": [
        {"name": "Arizona Public Service",   "elec": 0.1420, "gas": None, "water": None, "phone": "1-602-371-7171"},
        {"name": "Salt River Project (AZ)",  "elec": 0.1280, "gas": None, "water": None, "phone": "602-236-8888"},
        {"name": "Southwest Gas (AZ)",       "elec": None,   "gas": 1.14, "water": None, "phone": "1-877-860-6020"},
        {"name": "City of Phoenix Water",    "elec": None,   "gas": None, "water": 4.30, "phone": "602-262-6251"},
    ],
    "87": [
        {"name": "PNM (New Mexico)",         "elec": 0.1350, "gas": 1.11, "water": 5.00, "phone": "1-888-342-5766"},
        {"name": "New Mexico Gas Company",   "elec": None,   "gas": 1.09, "water": None, "phone": "1-888-664-2726"},
        {"name": "Albuquerque Bernalillo Water","elec":None, "gas": None, "water": 4.70, "phone": "505-842-9287"},
    ],
    "89": [
        {"name": "NV Energy (Nevada)",       "elec": 0.1390, "gas": 1.20, "water": 6.20, "phone": "1-702-402-5555"},
        {"name": "Southwest Gas (NV)",       "elec": None,   "gas": 1.18, "water": None, "phone": "1-877-860-6020"},
        {"name": "Las Vegas Valley Water Dist","elec":None,  "gas": None, "water": 5.90, "phone": "702-870-4194"},
    ],
    "8": [
        {"name": "Xcel Energy",              "elec": 0.1410, "gas": 1.08, "water": 5.40, "phone": "1-800-895-4999"},
        {"name": "Black Hills Energy",       "elec": 0.1320, "gas": 1.02, "water": None, "phone": "1-888-890-5554"},
        {"name": "Southwest Gas",            "elec": None,   "gas": 1.14, "water": None, "phone": "1-877-860-6020"},
    ],

    # ════════════════════════════════════════
    #   90x-96x — CALIFORNIA (expanded from v1.x)
    # ════════════════════════════════════════
    "90": [
        {"name": "Southern California Edison","elec": 0.2850,"gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                 "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "LA Dept of Water & Power", "elec": 0.2340, "gas": None, "water": 9.20, "phone": "1-800-342-5397"},
    ],
    "92": [
        {"name": "San Diego Gas & Electric", "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "SoCalGas",                 "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Water",          "elec": None,   "gas": None, "water": 9.80, "phone": "619-515-3500"},
    ],
    "94": [
        {"name": "Pacific Gas & Electric",   "elec": 0.3100, "gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "East Bay MUD",             "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
        {"name": "San Jose Water",           "elec": None,   "gas": None, "water": 9.10, "phone": "408-279-7900"},
    ],
    "95": [
        {"name": "Pacific Gas & Electric",   "elec": 0.3100, "gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Sacramento Municipal Util (SMUD)","elec":0.1890,"gas":None,"water":None,"phone":"1-888-742-7683"},
        {"name": "Sacramento Dept of Utilities","elec":None, "gas": None, "water": 8.60, "phone": "916-808-5454"},
    ],
    "9": [
        {"name": "Pacific Gas & Electric",   "elec": 0.3100, "gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Southern California Edison","elec": 0.2850,"gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                 "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Gas & Electric", "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "East Bay MUD",             "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
    ],

    # ════════════════════════════════════════
    #   97x — OREGON
    # ════════════════════════════════════════
    "97": [
        {"name": "Portland General Electric","elec": 0.1250, "gas": 1.20, "water": 5.50, "phone": "1-800-542-8818"},
        {"name": "NW Natural Gas",           "elec": None,   "gas": 1.15, "water": None, "phone": "1-800-422-4012"},
        {"name": "Pacific Power",            "elec": 0.1190, "gas": None, "water": None, "phone": "1-888-221-7070"},
        {"name": "Portland Water Bureau",    "elec": None,   "gas": None, "water": 5.20, "phone": "503-823-7770"},
    ],

    # ════════════════════════════════════════
    #   98x — WASHINGTON STATE
    # ════════════════════════════════════════
    "98": [
        {"name": "Puget Sound Energy",       "elec": 0.1390, "gas": 1.25, "water": 5.80, "phone": "1-888-225-5773"},
        {"name": "Seattle City Light",       "elec": 0.1120, "gas": None, "water": None, "phone": "206-684-3000"},
        {"name": "Cascade Natural Gas",      "elec": None,   "gas": 1.22, "water": None, "phone": "1-888-522-1130"},
        {"name": "Seattle Public Utilities", "elec": None,   "gas": None, "water": 6.10, "phone": "206-684-3000"},
        {"name": "Tacoma Power",             "elec": 0.1050, "gas": None, "water": None, "phone": "253-502-8600"},
    ],

    # ════════════════════════════════════════
    #   National fallback
    # ════════════════════════════════════════
    "default": [
        {"name": "National avg — Electricity","elec": 0.1400,"gas": None, "water": None, "phone": "eia.gov"},
        {"name": "National avg — Gas",        "elec": None,  "gas": 1.18, "water": None, "phone": "eia.gov"},
        {"name": "American Water Works",      "elec": None,  "gas": None, "water": 5.80, "phone": "1-800-684-3256"},
    ],
}

UTILITY_CONFIG = {
    "elec":  {"label": "Electricity", "cost_key": "elec_cost",  "rate_key": "elec",  "unit": "kWh",    "default": 900,  "divisor": 1},
    "gas":   {"label": "Natural Gas", "cost_key": "gas_cost",   "rate_key": "gas",   "unit": "therms", "default": 50,   "divisor": 1},
    "water": {"label": "Water",       "cost_key": "water_cost", "rate_key": "water", "unit": "gal",    "default": 3000, "divisor": 1000},
}

ICONS = {"elec": "⚡", "gas": "🔥", "water": "💧"}

# ─────────────────────────────────────────────
#   SESSION HISTORY
# ─────────────────────────────────────────────

last_search = {
    "zip_code": None, "results": None,
    "filters": None,  "usage": None, "timestamp": None,
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
    """Longest-prefix match, 3 → 2 → 1 → default."""
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in UTILITY_DB:
            return UTILITY_DB[prefix], REGION_NAMES.get(prefix, f"Region {prefix}xx")
    return UTILITY_DB["default"], "National (no region data)"

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
                if v < 0: raise ValueError
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
        c = input("  Your choice [1-5]: ").strip()
        if c == "1":   return {"elec", "gas", "water"}
        elif c == "2": return {"elec"}
        elif c == "3": return {"gas"}
        elif c == "4": return {"water"}
        elif c == "5": return pick_custom_filter()
        else:          print("  ⚠  Enter 1–5.")

def pick_custom_filter():
    print()
    slow_print("  CUSTOM FILTER — toggle on/off, then S to save.", delay=0.013)
    sel     = {"elec": True, "gas": True, "water": True}
    options = [("elec","Electricity ⚡"),("gas","Natural Gas 🔥"),("water","Water 💧")]
    while True:
        print(); divider()
        for i,(k,lbl) in enumerate(options,1):
            print(f"  [{i}]  {lbl:<20}  {'✅ ON' if sel[k] else '❌ OFF'}")
        divider(); print("  [S]  Save and continue")
        r = input("  Toggle [1/2/3] or Save [S]: ").strip().upper()
        if r=="1":   sel["elec"]  = not sel["elec"]
        elif r=="2": sel["gas"]   = not sel["gas"]
        elif r=="3": sel["water"] = not sel["water"]
        elif r=="S":
            active = {k for k,v in sel.items() if v}
            if not active: print("  ⚠  Keep at least one!")
            else:          return active
        else: print("  ⚠  Invalid.")

# ─────────────────────────────────────────────
#   REGION BROWSER  ← v1.3
# ─────────────────────────────────────────────

def region_browser():
    """Show all covered regions grouped by first digit, with provider counts."""
    print()
    divider("═")
    slow_print("  🗺️   REGION COVERAGE BROWSER  ← v1.3", delay=0.015)
    divider("═")
    print("  All ZIP code regions currently in the database.\n")

    # Group by first digit of prefix
    groups = {}
    for prefix, providers in UTILITY_DB.items():
        if prefix == "default":
            continue
        first = prefix[0]
        groups.setdefault(first, []).append((prefix, providers))

    zone_labels = {
        "0": "0xx — Northeast",
        "1": "1xx — New York & New Jersey",
        "2": "2xx — Mid-Atlantic",
        "3": "3xx — Southeast",
        "4": "4xx — Midwest (OH / IN / MI / KY)",
        "5": "5xx — Upper Midwest",
        "6": "6xx — IL / MO / KS",
        "7": "7xx — South & Texas",
        "8": "8xx — Mountain West",
        "9": "9xx — California, Pacific NW, AK/HI",
    }

    for digit in sorted(groups.keys()):
        entries = sorted(groups[digit], key=lambda x: x[0])
        print(f"  {zone_labels.get(digit, digit+'xx')}")
        for prefix, providers in entries:
            name     = REGION_NAMES.get(prefix, f"ZIP {prefix}xxx")
            count    = len(providers)
            coverage = []
            if any(p["elec"]  is not None for p in providers): coverage.append("⚡")
            if any(p["gas"]   is not None for p in providers): coverage.append("🔥")
            if any(p["water"] is not None for p in providers): coverage.append("💧")
            print(f"     {prefix}xxx  {name:<42}  {count} providers  {''.join(coverage)}")
        print()

    total_prefixes  = len(UTILITY_DB) - 1   # exclude "default"
    total_providers = sum(len(v) for k,v in UTILITY_DB.items() if k != "default")
    divider()
    print(f"  Total: {total_prefixes} regions  |  {total_providers} provider entries")
    print("  Missing your area? Open an issue on GitHub to request it!")
    divider("═")
    input("\n  Press Enter to return to the menu...")

# ─────────────────────────────────────────────
#   BUILD & DISPLAY RESULTS
# ─────────────────────────────────────────────

def build_results(providers, usage, filters):
    results = []
    for p in providers:
        costs = {}
        for key in ["elec","gas","water"]:
            cfg = UTILITY_CONFIG[key]
            costs[cfg["cost_key"]] = (
                get_monthly_cost(p[cfg["rate_key"]], usage[key], cfg["divisor"])
                if key in filters else None
            )
        avail = [costs[UTILITY_CONFIG[k]["cost_key"]] for k in filters
                 if costs[UTILITY_CONFIG[k]["cost_key"]] is not None]
        results.append({**p, **costs, "total": sum(avail), "services": len(avail)})
    results.sort(key=lambda x: (-x["services"], x["total"]))
    return results

def display_results(zip_code, providers, region_name, usage, filters):
    results = build_results(providers, usage, filters)
    last_search.update(zip_code=zip_code, results=results,
                       filters=filters, usage=usage,
                       timestamp=datetime.now())
    _print_results(zip_code, region_name, results, usage, filters)
    return results

def _print_results(zip_code, region_name, results, usage, filters):
    print()
    divider("═")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    slow_print(f"  📍  ZIP: {zip_code}  |  {region_name}", delay=0.013)
    slow_print(f"      Showing: {' + '.join(filter_labels)}", delay=0.010)
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
        cands = [r for r in results if r[ckey] is not None]
        if cands:
            w = min(cands, key=lambda x: x[ckey])
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
#   SAVE & EXPORT  (carried from v1.2)
# ─────────────────────────────────────────────

def save_menu():
    if last_search["results"] is None:
        print("\n  ⚠  No search results yet — run a search first!")
        return
    zip_code = last_search["zip_code"]
    results  = last_search["results"]
    filters  = last_search["filters"]
    usage    = last_search["usage"]
    ts       = last_search["timestamp"].strftime("%Y-%m-%d %H:%M")
    print(); divider()
    slow_print("  SAVE / EXPORT", delay=0.015)
    divider()
    print(f"  Last search: ZIP {zip_code}  |  {ts}\n")
    print("  [1]  Save as .txt  (readable report)")
    print("  [2]  Export as .csv  (open in Excel / Sheets)")
    print("  [3]  Re-display last results on screen")
    print("  [B]  Back")
    divider()
    choice = input("  Your choice: ").strip().upper()
    if   choice == "1": save_txt(zip_code, results, filters, usage, ts)
    elif choice == "2": save_csv(zip_code, results, filters, usage, ts)
    elif choice == "3":
        _print_results(zip_code, REGION_NAMES.get(zip_code[:2], zip_code[:1]+"xx"),
                       results, usage, filters)
        input("\n  Press Enter to continue...")
    elif choice == "B": return
    else: print("  ⚠  Invalid choice.")

def _make_filename(zip_code, ext):
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(os.getcwd(), f"utility_results_{zip_code}_{ts}.{ext}")

def save_txt(zip_code, results, filters, usage, ts):
    path          = _make_filename(zip_code, "txt")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    region_name   = REGION_NAMES.get(zip_code[:2], REGION_NAMES.get(zip_code[:1], "Unknown region"))
    lines = [
        "=" * 72,
        "  UTILITY FINDER — Search Results",
        f"  Generated : {ts}",
        f"  ZIP Code  : {zip_code}",
        f"  Region    : {region_name}",
        f"  Utilities : {' + '.join(filter_labels)}",
        "  Usage     : " + " | ".join(
            f"{usage[k]:.0f} {UTILITY_CONFIG[k]['unit']} {UTILITY_CONFIG[k]['label'].lower()}"
            for k in ["elec","gas","water"] if k in filters),
        "=" * 72, "",
    ]
    col_w  = 34
    header = f"  {'PROVIDER':<{col_w}}"
    for key in ["elec","gas","water"]:
        if key in filters:
            header += f"  {(UTILITY_CONFIG[key]['label'].upper()[:9]+'/mo'):>11}"
    if len(filters) > 1: header += f"  {'TOTAL/mo':>10}"
    header += "  PHONE"
    lines += [header, "-" * 72]
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
    lines += ["-" * 72, "", "  CHEAPEST BY UTILITY:"]
    for key in ["elec","gas","water"]:
        if key not in filters: continue
        cfg   = UTILITY_CONFIG[key]
        ckey  = cfg["cost_key"]
        cands = [r for r in results if r[ckey] is not None]
        if cands:
            w = min(cands, key=lambda x: x[ckey])
            lines.append(f"  {ICONS[key]} {cfg['label']:<14} -> {w['name']}  (${w[ckey]:.2f}/mo)  {w['phone']}")
    lines += ["", "  Rates are estimates. Confirm directly with the provider.", "=" * 72]
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  ✅  Saved: {path}")
    except OSError as e:
        print(f"\n  ❌  Could not save: {e}")
    input("  Press Enter to continue...")

def save_csv(zip_code, results, filters, usage, ts):
    path      = _make_filename(zip_code, "csv")
    base_cols = ["Provider","Phone"]
    rate_cols = [f"{UTILITY_CONFIG[k]['label']} Rate" for k in ["elec","gas","water"] if k in filters]
    cost_cols = [f"{UTILITY_CONFIG[k]['label']} $/mo"  for k in ["elec","gas","water"] if k in filters]
    extra     = (["Total $/mo"] if len(filters)>1 else []) + ["Services Offered"]
    all_cols  = base_cols + rate_cols + cost_cols + extra + ["Region","ZIP Code","Search Date"]
    region    = REGION_NAMES.get(zip_code[:2], REGION_NAMES.get(zip_code[:1],"Unknown"))
    try:
        with open(path,"w",newline="",encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=all_cols)
            w.writeheader()
            for r in results:
                row = {"Provider":r["name"],"Phone":r["phone"],
                       "ZIP Code":zip_code,"Search Date":ts,
                       "Region":region,"Services Offered":r["services"]}
                if len(filters)>1:
                    row["Total $/mo"] = f"{r['total']:.2f}" if r["services"]>0 else "N/A"
                for key in ["elec","gas","water"]:
                    if key not in filters: continue
                    cfg  = UTILITY_CONFIG[key]
                    rate = r.get(cfg["rate_key"])
                    cost = r[cfg["cost_key"]]
                    row[f"{cfg['label']} Rate"] = f"{rate:.4f}" if rate else "N/A"
                    row[f"{cfg['label']} $/mo"] = f"{cost:.2f}" if cost else "N/A"
                w.writerow(row)
        print(f"\n  ✅  Exported: {path}")
    except OSError as e:
        print(f"\n  ❌  Export failed: {e}")
    input("  Press Enter to continue...")

# ─────────────────────────────────────────────
#   COMPARE MODE
# ─────────────────────────────────────────────

def compare_mode(usage, filters):
    print(); divider()
    slow_print("  COMPARISON MODE — Enter two ZIP codes to compare.")
    divider()
    zip1 = get_zip()
    zip2 = get_zip()
    for z in [zip1, zip2]:
        providers, region = get_providers_for_zip(z)
        display_results(z, providers, region, usage, filters)

# ─────────────────────────────────────────────
#   ABOUT SCREEN
# ─────────────────────────────────────────────

def about_screen():
    print(); divider("═")
    slow_print("  ℹ️   ABOUT UTILITY FINDER  v1.3", delay=0.02)
    divider("═")
    total_p = sum(len(v) for k,v in UTILITY_DB.items() if k!="default")
    total_r = len(UTILITY_DB) - 1
    print(f"""
  What's new in v1.3:
  ───────────────────
  • Massively expanded region coverage
      {total_r} ZIP regions  |  {total_p} provider entries  (was 7 / 26)
  • Region name shown in every result header
  • Region Coverage Browser — see all covered areas at a glance
  • Finer ZIP matching (3-digit → 2-digit → 1-digit → national)

  What's in v1.2:
  ───────────────
  • Save results as .txt  |  Export as .csv

  What's in v1.1:
  ───────────────
  • Filter by utility type  |  Custom mix

  How rates are calculated:
  ─────────────────────────
  Electricity: $/kWh  |  Gas: $/therm  |  Water: $/1,000 gal
  Monthly cost = your usage × the provider's rate.

  Default usage (US averages):
    Electricity: 900 kWh/mo  |  Gas: 50 therms/mo  |  Water: 3,000 gal/mo

  Data: EIA published tariffs, last updated April 2025.
  Always confirm rates directly with the provider.
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
        print(); divider()
        slow_print("  MAIN MENU", delay=0.02)
        divider()
        print(f"  [1]  Find cheapest utilities for my ZIP code")
        print(f"         ↳ Filter: {filter_str}")
        print(f"  [2]  Compare two ZIP codes side-by-side")
        print(f"  [3]  Change utility filter")
        print(f"  [4]  Change usage amounts")
        print(f"  [5]  Save / Export results"
              + (f"  (last: ZIP {last_search['zip_code']})" if has_results else "  (no results yet)"))
        print(f"  [6]  Browse region coverage  ← NEW in v1.3")
        print(f"  [7]  About / How rates work")
        print(f"  [Q]  Quit")
        divider()
        c = input("  Your choice: ").strip().upper()
        if   c=="1": return "single"
        elif c=="2": return "compare"
        elif c=="3": return "filter"
        elif c=="4": return "usage"
        elif c=="5": return "save"
        elif c=="6": return "browse"
        elif c=="7": return "about"
        elif c=="Q": return "quit"
        else: print("  ⚠  Invalid — enter 1–7 or Q.")

# ─────────────────────────────────────────────
#   ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print(BANNER)
    time.sleep(0.3)
    slow_print("  Welcome to Utility Finder v1.3!", delay=0.018)
    slow_print("  Now covering most of the US — use [6] to browse regions.", delay=0.016)

    filters = pick_utility_filter()
    usage   = get_usage(filters)

    while True:
        choice = main_menu(filters)

        if choice == "single":
            zip_code           = get_zip()
            providers, region  = get_providers_for_zip(zip_code)
            display_results(zip_code, providers, region, usage, filters)
            print("\n  Tip: use [5] from the menu to save or export these results.")
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

        elif choice == "browse":
            region_browser()

        elif choice == "about":
            about_screen()

        elif choice == "quit":
            print()
            slow_print("  Thanks for using Utility Finder. Goodbye! 👋", delay=0.018)
            print()
            break

if __name__ == "__main__":
    main()
