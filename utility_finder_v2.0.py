import time
import os
import csv
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

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
║       >>> Live Rates via EIA API + Local Provider Data <<<          ║
║                    by ZIP Code  |  v2.0                             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#   EIA API CONFIG  ← v2.0
#   Get your free key at: eia.gov/opendata/register.php
#   Paste it below between the quotes, or leave as ""
#   and the program will ask you at startup.
# ─────────────────────────────────────────────

EIA_API_KEY   = ""                     # ← paste your key here if you want
CACHE_FILE    = "eia_cache.json"       # saved in the same folder as this script
CACHE_HOURS   = 24                     # how long before rates are re-fetched

# EIA endpoint URLs
EIA_BASE      = "https://api.eia.gov/v2"
EIA_ELEC_URL  = (
    EIA_BASE
    + "/electricity/retail-sales/data/"
    + "?data[]=price&facets[sectorName][]=residential"
    + "&sort[0][column]=period&sort[0][direction]=desc"
    + "&length=60"                     # last 60 state readings ≈ all states 1 month
)
EIA_GAS_URL   = (
    EIA_BASE
    + "/natural-gas/pri/sum/data/"
    + "?data[]=value&facets[process][]=PRS"   # PRS = residential retail
    + "&sort[0][column]=period&sort[0][direction]=desc"
    + "&length=60"
)

# ─────────────────────────────────────────────
#   ZIP → STATE MAP  (used to look up live rates)
# ─────────────────────────────────────────────

ZIP_PREFIX_TO_STATE = {
    "0":  "CT", "06": "CT", "05": "VT", "03": "NH", "04": "ME", "02": "MA", "028": "RI",
    "1":  "NY", "07": "NJ", "08": "NJ",
    "20": "DC", "21": "MD", "22": "VA", "23": "VA", "24": "WV", "25": "WV", "26": "WV",
    "27": "NC", "28": "NC", "29": "SC",
    "30": "GA", "31": "GA", "32": "FL", "33": "FL", "34": "FL",
    "35": "AL", "36": "AL", "37": "TN", "38": "TN", "39": "MS",
    "40": "KY", "41": "KY", "42": "KY",
    "43": "OH", "44": "OH", "45": "OH",
    "46": "IN", "47": "IN",
    "48": "MI", "49": "MI",
    "5":  "MN", "50": "IA", "51": "IA", "52": "IA", "53": "WI", "54": "WI",
    "55": "MN", "56": "MN", "57": "SD", "58": "ND", "59": "MT",
    "60": "IL", "61": "IL", "62": "IL",
    "63": "MO", "64": "MO", "65": "MO",
    "66": "KS", "67": "KS", "68": "NE", "69": "NE",
    "70": "LA", "71": "LA", "72": "AR",
    "73": "OK", "74": "OK",
    "75": "TX", "76": "TX", "77": "TX", "78": "TX", "79": "TX",
    "7":  "TX",
    "80": "CO", "81": "CO", "82": "WY", "83": "ID", "84": "UT",
    "85": "AZ", "86": "AZ", "87": "NM", "88": "NM", "89": "NV",
    "90": "CA", "91": "CA", "92": "CA", "93": "CA", "94": "CA",
    "95": "CA", "96": "CA",
    "97": "OR", "98": "WA", "99": "WA",
    "9":  "CA",
}

# ─────────────────────────────────────────────
#   REGION NAMES  (for display)
# ─────────────────────────────────────────────

REGION_NAMES = {
    "0": "Northeast — CT, MA, RI, VT, NH, ME",
    "1": "New York & New Jersey",
    "20": "Washington D.C. & Northern Virginia",
    "21": "Maryland", "22": "Northern Virginia", "23": "Virginia",
    "24": "West Virginia & SW Virginia", "25": "West Virginia", "26": "West Virginia",
    "27": "North Carolina", "28": "North Carolina", "29": "South Carolina",
    "30": "Georgia — Atlanta", "31": "Georgia",
    "32": "Florida — Central & North", "33": "Florida — South & Miami",
    "34": "Florida — West Coast",
    "35": "Alabama", "36": "Alabama",
    "37": "Tennessee", "38": "Tennessee & Mississippi", "39": "Mississippi",
    "40": "Kentucky — Louisville", "41": "Kentucky", "42": "Kentucky",
    "43": "Ohio — Columbus", "44": "Ohio — Cleveland", "45": "Ohio — Cincinnati",
    "46": "Indiana — Indianapolis", "47": "Indiana",
    "48": "Michigan — Detroit", "49": "Michigan — West",
    "5": "Midwest — IA, MN, WI, SD, ND, NE, KS",
    "60": "Illinois — Chicago", "61": "Illinois — Central", "62": "Illinois — Southern",
    "63": "Missouri — St. Louis", "64": "Missouri — Kansas City", "65": "Missouri",
    "66": "Kansas", "67": "Kansas", "68": "Nebraska", "69": "Nebraska",
    "70": "Louisiana — New Orleans", "71": "Louisiana — North", "72": "Arkansas",
    "73": "Oklahoma — OKC", "74": "Oklahoma — Tulsa",
    "75": "Texas — Dallas", "76": "Texas — Fort Worth",
    "77": "Texas — Houston", "78": "Texas — San Antonio", "79": "Texas — West",
    "80": "Colorado — Denver", "81": "Colorado — Western",
    "82": "Wyoming", "83": "Idaho", "84": "Utah",
    "85": "Arizona — Phoenix", "86": "Arizona — Northern",
    "87": "New Mexico", "88": "New Mexico", "89": "Nevada",
    "90": "California — Los Angeles", "91": "California — LA Valley",
    "92": "California — San Diego", "93": "California — Central Valley",
    "94": "California — Bay Area", "95": "California — Sacramento",
    "96": "California — Far North", "97": "Oregon",
    "98": "Washington State", "99": "Washington State — Eastern & Alaska",
}

# ─────────────────────────────────────────────
#   PROVIDER DATABASE  (from v1.3)
#   Rates here are FALLBACK only in v2.0 —
#   live EIA state averages override elec + gas
#   when the API call succeeds.
# ─────────────────────────────────────────────

UTILITY_DB = {
    "0":  [
        {"name": "Eversource Energy",        "elec": 0.2210, "gas": 1.45, "water": 7.80, "phone": "1-800-286-2000"},
        {"name": "National Grid",             "elec": 0.2050, "gas": 1.38, "water": 7.20, "phone": "1-800-642-4272"},
        {"name": "UI (United Illuminating)",  "elec": 0.2380, "gas": None, "water": None, "phone": "1-800-722-5584"},
        {"name": "Aquarion Water Company",    "elec": None,   "gas": None, "water": 8.10, "phone": "1-800-732-9678"},
        {"name": "Liberty Utilities",         "elec": 0.1980, "gas": 1.42, "water": 7.50, "phone": "1-800-375-7413"},
        {"name": "Green Mountain Power (VT)", "elec": 0.2010, "gas": None, "water": None, "phone": "1-888-835-4672"},
    ],
    "1":  [
        {"name": "Con Edison",               "elec": 0.2340, "gas": 1.52, "water": 9.10, "phone": "1-800-752-6633"},
        {"name": "Orange & Rockland",        "elec": 0.2100, "gas": 1.44, "water": 8.50, "phone": "1-877-434-4100"},
        {"name": "New York American Water",  "elec": None,   "gas": None, "water": 8.90, "phone": "1-877-426-6999"},
        {"name": "PSE&G (NJ)",               "elec": 0.1680, "gas": 1.30, "water": 6.70, "phone": "1-800-436-7734"},
        {"name": "JCP&L (NJ)",               "elec": 0.1590, "gas": None, "water": None, "phone": "1-800-662-3115"},
        {"name": "NJ American Water",        "elec": None,   "gas": None, "water": 7.10, "phone": "1-800-652-6987"},
    ],
    "20": [
        {"name": "Pepco (DC/MD)",            "elec": 0.1420, "gas": None, "water": None, "phone": "1-202-833-7500"},
        {"name": "Washington Gas",           "elec": None,   "gas": 1.18, "water": None, "phone": "1-844-927-4427"},
        {"name": "DC Water",                 "elec": None,   "gas": None, "water": 8.20, "phone": "202-354-3600"},
        {"name": "Dominion Energy VA",       "elec": 0.1260, "gas": 1.12, "water": None, "phone": "1-866-366-4357"},
    ],
    "21": [
        {"name": "BGE (Baltimore Gas & Elec)","elec":0.1380, "gas": 1.15, "water": 6.40, "phone": "1-800-685-0123"},
        {"name": "Delmarva Power",           "elec": 0.1490, "gas": None, "water": None, "phone": "1-800-375-7117"},
        {"name": "Washington Gas",           "elec": None,   "gas": 1.18, "water": None, "phone": "1-844-927-4427"},
        {"name": "WS Sanitary Commission",   "elec": None,   "gas": None, "water": 7.30, "phone": "301-206-8000"},
    ],
    "27": [
        {"name": "Duke Energy Carolinas",    "elec": 0.1210, "gas": 1.08, "water": 5.10, "phone": "1-800-777-9898"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "Raleigh Water",            "elec": None,   "gas": None, "water": 4.80, "phone": "919-996-3245"},
    ],
    "28": [
        {"name": "Duke Energy Progress",     "elec": 0.1230, "gas": None, "water": None, "phone": "1-800-452-2777"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "Charlotte Water",          "elec": None,   "gas": None, "water": 4.90, "phone": "704-336-7600"},
    ],
    "29": [
        {"name": "Dominion Energy SC",       "elec": 0.1350, "gas": 1.12, "water": None, "phone": "1-800-251-7234"},
        {"name": "Duke Energy Carolinas",    "elec": 0.1210, "gas": None, "water": None, "phone": "1-800-777-9898"},
        {"name": "Columbia Water (SC)",      "elec": None,   "gas": None, "water": 4.70, "phone": "803-545-3300"},
    ],
    "30": [
        {"name": "Georgia Power",            "elec": 0.1250, "gas": 1.10, "water": 4.60, "phone": "1-888-660-5890"},
        {"name": "Atlanta Gas Light",        "elec": None,   "gas": 1.08, "water": None, "phone": "1-770-994-1946"},
        {"name": "Atlanta Watershed",        "elec": None,   "gas": None, "water": 5.30, "phone": "404-546-0311"},
    ],
    "32": [
        {"name": "Duke Energy Florida",      "elec": 0.1190, "gas": 1.05, "water": 4.30, "phone": "1-800-700-8744"},
        {"name": "JEA (Jacksonville)",       "elec": 0.1155, "gas": 1.08, "water": 4.15, "phone": "1-904-665-6000"},
    ],
    "33": [
        {"name": "Florida Power & Light",    "elec": 0.1088, "gas": None, "water": None, "phone": "1-800-375-2434"},
        {"name": "TECO Peoples Gas",         "elec": None,   "gas": 1.01, "water": None, "phone": "1-877-832-6747"},
        {"name": "Miami-Dade Water & Sewer", "elec": None,   "gas": None, "water": 5.60, "phone": "305-665-7477"},
    ],
    "35": [
        {"name": "Alabama Power",            "elec": 0.1310, "gas": 1.09, "water": 4.80, "phone": "1-800-245-2244"},
        {"name": "Alagasco (Spire Alabama)", "elec": None,   "gas": 1.06, "water": None, "phone": "1-800-292-4008"},
        {"name": "Birmingham Water Works",   "elec": None,   "gas": None, "water": 4.40, "phone": "205-244-4000"},
    ],
    "37": [
        {"name": "Nashville Electric",       "elec": 0.1080, "gas": None, "water": None, "phone": "615-736-6900"},
        {"name": "Piedmont Natural Gas",     "elec": None,   "gas": 1.05, "water": None, "phone": "1-800-752-7504"},
        {"name": "Metro Water (Nashville)",  "elec": None,   "gas": None, "water": 4.35, "phone": "615-862-4600"},
        {"name": "Memphis LG&W",             "elec": 0.1020, "gas": 1.01, "water": 4.10, "phone": "901-544-6549"},
    ],
    "40": [
        {"name": "LG&E Louisville",          "elec": 0.1150, "gas": 1.05, "water": 4.60, "phone": "502-589-1444"},
        {"name": "Louisville Water Company", "elec": None,   "gas": None, "water": 4.20, "phone": "502-583-6610"},
    ],
    "43": [
        {"name": "AEP Ohio",                 "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Columbus Division of Water","elec":None,   "gas": None, "water": 4.80, "phone": "614-645-7788"},
    ],
    "44": [
        {"name": "FirstEnergy / Ohio Edison","elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "Dominion Energy Ohio",     "elec": None,   "gas": 1.06, "water": None, "phone": "1-800-362-7557"},
        {"name": "Cleveland Water",          "elec": None,   "gas": None, "water": 4.95, "phone": "216-664-3060"},
    ],
    "45": [
        {"name": "Duke Energy Ohio",         "elec": 0.1210, "gas": 1.09, "water": 5.00, "phone": "1-800-544-6900"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Greater Cincinnati Water", "elec": None,   "gas": None, "water": 4.75, "phone": "513-591-7700"},
    ],
    "4":  [
        {"name": "FirstEnergy / Ohio Edison","elec": 0.1312, "gas": 1.08, "water": 5.20, "phone": "1-800-633-4766"},
        {"name": "AEP Ohio",                 "elec": 0.1195, "gas": 1.15, "water": 4.95, "phone": "1-800-672-2231"},
        {"name": "Columbia Gas of Ohio",     "elec": None,   "gas": 1.02, "water": None, "phone": "1-800-344-4077"},
        {"name": "Indiana Michigan Power",   "elec": 0.1230, "gas": 1.10, "water": 5.00, "phone": "1-800-311-4634"},
        {"name": "Consumers Energy (MI)",    "elec": 0.1680, "gas": 1.14, "water": None, "phone": "1-800-477-5050"},
        {"name": "DTE Energy (MI)",          "elec": 0.1790, "gas": 1.18, "water": None, "phone": "1-800-477-4747"},
    ],
    "5":  [
        {"name": "Xcel Energy (MN/ND/SD)",   "elec": 0.1320, "gas": 1.10, "water": 5.30, "phone": "1-800-895-4999"},
        {"name": "MidAmerican Energy (IA)",  "elec": 0.1050, "gas": 0.98, "water": None, "phone": "1-888-427-5632"},
        {"name": "We Energies (WI)",         "elec": 0.1850, "gas": 1.20, "water": 6.10, "phone": "1-800-242-9137"},
        {"name": "Alliant Energy (IA/WI)",   "elec": 0.1280, "gas": 1.05, "water": None, "phone": "1-800-255-4268"},
        {"name": "Black Hills Energy",       "elec": 0.1150, "gas": 0.97, "water": None, "phone": "1-888-890-5554"},
        {"name": "Minneapolis Water",        "elec": None,   "gas": None, "water": 5.60, "phone": "612-673-3000"},
    ],
    "60": [
        {"name": "ComEd (Chicago)",          "elec": 0.1620, "gas": None, "water": None, "phone": "1-800-334-7661"},
        {"name": "Peoples Gas (Chicago)",    "elec": None,   "gas": 1.28, "water": None, "phone": "1-866-556-6004"},
        {"name": "City of Chicago Water",    "elec": None,   "gas": None, "water": 6.50, "phone": "312-744-7038"},
    ],
    "6":  [
        {"name": "Ameren Illinois",          "elec": 0.1490, "gas": 1.20, "water": 5.80, "phone": "1-800-755-5000"},
        {"name": "Spire Missouri",           "elec": None,   "gas": 1.16, "water": None, "phone": "1-800-582-1234"},
        {"name": "Evergy (KS/MO)",           "elec": 0.1380, "gas": 1.08, "water": None, "phone": "1-888-471-5275"},
    ],
    "70": [
        {"name": "Entergy Louisiana",        "elec": 0.1050, "gas": 0.94, "water": 3.90, "phone": "1-800-368-3749"},
        {"name": "Atmos Energy (LA)",        "elec": None,   "gas": 0.92, "water": None, "phone": "1-888-286-6700"},
        {"name": "Sewerage & Water Board",   "elec": None,   "gas": None, "water": 3.70, "phone": "504-529-2837"},
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
        {"name": "SA Water System (SAWS)",   "elec": None,   "gas": None, "water": 3.50, "phone": "210-704-7297"},
    ],
    "7":  [
        {"name": "Oncor Electric",           "elec": 0.1020, "gas": 0.95, "water": 4.00, "phone": "1-888-313-4747"},
        {"name": "CenterPoint Energy",       "elec": 0.1150, "gas": 0.98, "water": 3.80, "phone": "1-800-752-8036"},
        {"name": "Entergy Texas",            "elec": 0.1080, "gas": 0.92, "water": None, "phone": "1-800-968-8243"},
        {"name": "Texas Gas Service",        "elec": None,   "gas": 0.90, "water": None, "phone": "1-800-700-2443"},
        {"name": "City of Houston Water",    "elec": None,   "gas": None, "water": 3.60, "phone": "713-371-1400"},
    ],
    "80": [
        {"name": "Xcel Energy (CO)",         "elec": 0.1410, "gas": 1.08, "water": 5.40, "phone": "1-800-895-4999"},
        {"name": "Black Hills Energy (CO)",  "elec": 0.1320, "gas": 1.02, "water": None, "phone": "1-888-890-5554"},
        {"name": "Denver Water",             "elec": None,   "gas": None, "water": 5.10, "phone": "720-944-3751"},
    ],
    "84": [
        {"name": "Rocky Mountain Power (UT)","elec": 0.1180, "gas": 1.06, "water": 5.20, "phone": "1-888-221-7070"},
        {"name": "Questar Gas / Dominion",   "elec": None,   "gas": 1.03, "water": None, "phone": "1-800-323-5517"},
        {"name": "SLC Public Utilities",     "elec": None,   "gas": None, "water": 4.90, "phone": "801-483-6900"},
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
        {"name": "Albuquerque Water",        "elec": None,   "gas": None, "water": 4.70, "phone": "505-842-9287"},
    ],
    "89": [
        {"name": "NV Energy",                "elec": 0.1390, "gas": 1.20, "water": 6.20, "phone": "1-702-402-5555"},
        {"name": "Southwest Gas (NV)",       "elec": None,   "gas": 1.18, "water": None, "phone": "1-877-860-6020"},
        {"name": "Las Vegas Valley Water",   "elec": None,   "gas": None, "water": 5.90, "phone": "702-870-4194"},
    ],
    "8":  [
        {"name": "Xcel Energy",              "elec": 0.1410, "gas": 1.08, "water": 5.40, "phone": "1-800-895-4999"},
        {"name": "Black Hills Energy",       "elec": 0.1320, "gas": 1.02, "water": None, "phone": "1-888-890-5554"},
        {"name": "Southwest Gas",            "elec": None,   "gas": 1.14, "water": None, "phone": "1-877-860-6020"},
    ],
    "90": [
        {"name": "LA Dept of Water & Power", "elec": 0.2340, "gas": None, "water": 9.20, "phone": "1-800-342-5397"},
        {"name": "Southern California Edison","elec": 0.2850,"gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                 "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
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
        {"name": "SMUD (Sacramento)",        "elec": 0.1890, "gas": None, "water": None, "phone": "1-888-742-7683"},
        {"name": "Sacramento Utilities",     "elec": None,   "gas": None, "water": 8.60, "phone": "916-808-5454"},
    ],
    "9":  [
        {"name": "Pacific Gas & Electric",   "elec": 0.3100, "gas": 2.10, "water": 9.50, "phone": "1-800-743-5000"},
        {"name": "Southern California Edison","elec": 0.2850,"gas": None, "water": None, "phone": "1-800-655-4555"},
        {"name": "SoCalGas",                 "elec": None,   "gas": 1.98, "water": None, "phone": "1-800-427-2200"},
        {"name": "San Diego Gas & Electric", "elec": 0.3350, "gas": 2.05, "water": 10.20,"phone": "1-800-411-7343"},
        {"name": "East Bay MUD",             "elec": None,   "gas": None, "water": 8.80, "phone": "1-866-403-2683"},
    ],
    "97": [
        {"name": "Portland General Electric","elec": 0.1250, "gas": 1.20, "water": 5.50, "phone": "1-800-542-8818"},
        {"name": "NW Natural Gas",           "elec": None,   "gas": 1.15, "water": None, "phone": "1-800-422-4012"},
        {"name": "Pacific Power",            "elec": 0.1190, "gas": None, "water": None, "phone": "1-888-221-7070"},
        {"name": "Portland Water Bureau",    "elec": None,   "gas": None, "water": 5.20, "phone": "503-823-7770"},
    ],
    "98": [
        {"name": "Puget Sound Energy",       "elec": 0.1390, "gas": 1.25, "water": 5.80, "phone": "1-888-225-5773"},
        {"name": "Seattle City Light",       "elec": 0.1120, "gas": None, "water": None, "phone": "206-684-3000"},
        {"name": "Cascade Natural Gas",      "elec": None,   "gas": 1.22, "water": None, "phone": "1-888-522-1130"},
        {"name": "Seattle Public Utilities", "elec": None,   "gas": None, "water": 6.10, "phone": "206-684-3000"},
        {"name": "Tacoma Power",             "elec": 0.1050, "gas": None, "water": None, "phone": "253-502-8600"},
    ],
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
#   SESSION STATE
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
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in UTILITY_DB:
            region = REGION_NAMES.get(prefix, f"Region {prefix}xx")
            return list(UTILITY_DB[prefix]), region, prefix
    return list(UTILITY_DB["default"]), "National (no region data)", None

def get_state_for_zip(zip_code):
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in ZIP_PREFIX_TO_STATE:
            return ZIP_PREFIX_TO_STATE[prefix]
    return None

def get_monthly_cost(rate, usage, divisor=1):
    if rate is None:
        return None
    return rate * (usage / divisor)

# ─────────────────────────────────────────────
#   EIA API — CACHE  ← v2.0
# ─────────────────────────────────────────────

def _load_cache():
    """Load the local cache file. Returns {} if missing or corrupt."""
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_cache(data):
    """Write data to the local cache file."""
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass   # silent — cache is best-effort

def _cache_is_fresh(cache, key):
    """Return True if a cache entry exists and is younger than CACHE_HOURS."""
    if key not in cache:
        return False
    try:
        saved = datetime.fromisoformat(cache[key]["fetched_at"])
        return datetime.now() - saved < timedelta(hours=CACHE_HOURS)
    except (KeyError, ValueError):
        return False

# ─────────────────────────────────────────────
#   EIA API — FETCH  ← v2.0
# ─────────────────────────────────────────────

def _eia_get(url, api_key, timeout=10):
    """
    Make one GET request to the EIA API.
    Returns the parsed JSON dict, or None on any error.
    """
    full_url = url + f"&api_key={api_key}"
    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "UtilityFinder/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("\n  ❌  API key rejected (403). Double-check your key and try again.")
        else:
            print(f"\n  ⚠  EIA API HTTP error {e.code} — using cached / fallback rates.")
        return None
    except urllib.error.URLError:
        print("\n  ⚠  No internet connection — using cached / fallback rates.")
        return None
    except Exception:
        print("\n  ⚠  Unexpected API error — using cached / fallback rates.")
        return None

def fetch_live_rates(api_key, state_code):
    """
    Fetch the most recent residential electricity ($/kWh) and
    natural gas ($/therm) state averages from EIA.
    Returns: (elec_rate_or_None, gas_rate_or_None, period_str, source_label)
    """
    cache     = _load_cache()
    cache_key = f"rates_{state_code}"

    if _cache_is_fresh(cache, cache_key):
        entry = cache[cache_key]
        age   = datetime.now() - datetime.fromisoformat(entry["fetched_at"])
        hours = int(age.total_seconds() / 3600)
        source = f"EIA live ({entry['period']}) — cached {hours}h ago"
        return entry.get("elec"), entry.get("gas"), entry.get("period", "?"), source

    # ── Electricity ──
    elec_rate = None
    period    = "?"
    elec_data = _eia_get(EIA_ELEC_URL + f"&facets[stateid][]={state_code}", api_key)
    if elec_data:
        rows = elec_data.get("response", {}).get("data", [])
        if rows:
            price_cents = rows[0].get("price")
            period      = rows[0].get("period", "?")
            if price_cents is not None:
                elec_rate = round(float(price_cents) / 100, 4)   # cents → $/kWh

    # ── Natural gas ──
    gas_rate = None
    gas_data = _eia_get(EIA_GAS_URL + f"&facets[duoarea][]=S{state_code}", api_key)
    if gas_data:
        rows = gas_data.get("response", {}).get("data", [])
        if rows:
            val = rows[0].get("value")
            if val is not None:
                gas_rate = round(float(val), 4)   # already $/thousand cubic feet
                # Convert Mcf → therms: 1 Mcf ≈ 10.37 therms
                gas_rate = round(gas_rate / 10.37, 4)

    # ── Cache result ──
    if elec_rate is not None or gas_rate is not None:
        cache[cache_key] = {
            "elec":       elec_rate,
            "gas":        gas_rate,
            "period":     period,
            "fetched_at": datetime.now().isoformat(),
        }
        _save_cache(cache)
        source = f"EIA live data — period {period}"
    else:
        source = "fallback (API returned no data for this state)"

    return elec_rate, gas_rate, period, source

def apply_live_rates(providers, elec_live, gas_live):
    """
    Clone providers and substitute live EIA state-average rates for
    elec and gas wherever a provider originally had a rate (not None).
    Water is always kept from the local database — no public API for it.
    """
    updated = []
    for p in providers:
        p2 = dict(p)
        if elec_live is not None and p["elec"] is not None:
            p2["elec"] = elec_live
        if gas_live is not None and p["gas"] is not None:
            p2["gas"] = gas_live
        updated.append(p2)
    return updated

# ─────────────────────────────────────────────
#   API KEY MANAGEMENT  ← v2.0
# ─────────────────────────────────────────────

def load_or_prompt_api_key():
    """
    Priority: 1) hardcoded EIA_API_KEY  2) saved in cache  3) ask user
    Saves the key to cache so they only need to enter it once.
    """
    if EIA_API_KEY.strip():
        return EIA_API_KEY.strip()

    cache = _load_cache()
    if cache.get("api_key"):
        return cache["api_key"]

    print()
    divider()
    slow_print("  🔑  EIA API KEY SETUP  ← v2.0", delay=0.015)
    divider()
    print("""
  To get live rates you need a FREE EIA API key.
  It takes about 2 minutes:

  1. Go to:  https://www.eia.gov/opendata/register.php
  2. Fill in your name + email — no payment info needed
  3. Check your email for the key (arrives in seconds)
  4. Paste it below

  Or press Enter to skip and use saved rates instead (offline mode).
""")
    key = input("  Paste your EIA API key: ").strip()
    if key:
        cache["api_key"] = key
        _save_cache(cache)
        print("  ✅  Key saved — you won't need to enter it again.")
    else:
        print("  ℹ️   Running in offline mode — using saved fallback rates.")
    return key if key else None

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
    print("  [5]  Custom combination")
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
    sel     = {"elec": True, "gas": True, "water": True}
    options = [("elec","Electricity ⚡"), ("gas","Natural Gas 🔥"), ("water","Water 💧")]
    while True:
        print(); divider()
        for i, (k, lbl) in enumerate(options, 1):
            print(f"  [{i}]  {lbl:<20}  {'✅ ON' if sel[k] else '❌ OFF'}")
        divider(); print("  [S]  Save and continue")
        r = input("  Toggle [1/2/3] or Save [S]: ").strip().upper()
        if r == "1":   sel["elec"]  = not sel["elec"]
        elif r == "2": sel["gas"]   = not sel["gas"]
        elif r == "3": sel["water"] = not sel["water"]
        elif r == "S":
            active = {k for k, v in sel.items() if v}
            if not active: print("  ⚠  Keep at least one!")
            else:          return active
        else: print("  ⚠  Invalid.")

# ─────────────────────────────────────────────
#   BUILD & DISPLAY RESULTS
# ─────────────────────────────────────────────

def build_results(providers, usage, filters):
    results = []
    for p in providers:
        costs = {}
        for key in ["elec", "gas", "water"]:
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

def display_results(zip_code, providers, region_name, usage, filters,
                    rate_source="local database", period="—"):
    results = build_results(providers, usage, filters)
    last_search.update(zip_code=zip_code, results=results,
                       filters=filters, usage=usage,
                       timestamp=datetime.now())
    _print_results(zip_code, region_name, results, usage, filters, rate_source, period)
    return results

def _print_results(zip_code, region_name, results, usage, filters,
                   rate_source="local database", period="—"):
    print()
    divider("═")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    slow_print(f"  📍  ZIP: {zip_code}  |  {region_name}", delay=0.013)
    slow_print(f"      Showing: {' + '.join(filter_labels)}", delay=0.010)

    # Rate source banner — key new feature of v2.0
    if "EIA live" in rate_source:
        slow_print(f"  📡  Elec + Gas: {rate_source}", delay=0.008)
    else:
        slow_print(f"  📁  Rates: {rate_source}", delay=0.008)
    slow_print(f"      Water: always from local database (no public API)", delay=0.008)
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
        cfg   = UTILITY_CONFIG[key]
        ckey  = cfg["cost_key"]
        cands = [r for r in results if r[ckey] is not None]
        if cands:
            w = min(cands, key=lambda x: x[ckey])
            print(f"     {ICONS[key]} {cfg['label']:<14} →  {w['name']}  "
                  f"(${w[ckey]:.2f}/mo)  📞 {w['phone']}")
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
#   CORE SEARCH  ← v2.0 main flow
# ─────────────────────────────────────────────

def run_search(zip_code, usage, filters, api_key):
    """
    Full search: get providers, attempt live EIA rates,
    apply them if available, display results.
    """
    providers_raw, region_name, prefix = get_providers_for_zip(zip_code)
    state = get_state_for_zip(zip_code)

    elec_live = gas_live = None
    rate_source = "local database (offline mode)"
    period      = "—"

    if api_key and state:
        print(f"\n  📡  Fetching live EIA rates for {state}...", end="", flush=True)
        elec_live, gas_live, period, rate_source = fetch_live_rates(api_key, state)
        print(" done." if ("EIA live" in rate_source or "cached" in rate_source) else "")

    if elec_live is not None or gas_live is not None:
        providers = apply_live_rates(providers_raw, elec_live, gas_live)
    else:
        providers = providers_raw
        if api_key and state:
            rate_source = "local database (API returned no data for this state)"

    display_results(zip_code, providers, region_name, usage, filters, rate_source, period)

# ─────────────────────────────────────────────
#   COMPARE MODE
# ─────────────────────────────────────────────

def compare_mode(usage, filters, api_key):
    print(); divider()
    slow_print("  COMPARISON MODE — Enter two ZIP codes to compare.")
    divider()
    zip1 = get_zip()
    zip2 = get_zip()
    for z in [zip1, zip2]:
        run_search(z, usage, filters, api_key)

# ─────────────────────────────────────────────
#   SAVE & EXPORT  (carried from v1.2 / v1.3)
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
    print("  [1]  Save as .txt")
    print("  [2]  Export as .csv  (Excel / Sheets)")
    print("  [3]  Re-display last results")
    print("  [B]  Back")
    divider()
    choice = input("  Your choice: ").strip().upper()
    if   choice == "1": save_txt(zip_code, results, filters, usage, ts)
    elif choice == "2": save_csv(zip_code, results, filters, usage, ts)
    elif choice == "3":
        region = REGION_NAMES.get(zip_code[:2], REGION_NAMES.get(zip_code[:1], zip_code[:1]+"xx"))
        _print_results(zip_code, region, results, usage, filters)
        input("\n  Press Enter to continue...")
    elif choice == "B": return
    else: print("  ⚠  Invalid choice.")

def _make_filename(zip_code, ext):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(os.getcwd(), f"utility_results_{zip_code}_{ts}.{ext}")

def save_txt(zip_code, results, filters, usage, ts):
    path          = _make_filename(zip_code, "txt")
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    region        = REGION_NAMES.get(zip_code[:2], REGION_NAMES.get(zip_code[:1], "Unknown"))
    lines = [
        "=" * 72, "  UTILITY FINDER v2.0 — Search Results",
        f"  Generated : {ts}",
        f"  ZIP Code  : {zip_code}",
        f"  Region    : {region}",
        f"  Utilities : {' + '.join(filter_labels)}",
        "  Usage     : " + " | ".join(
            f"{usage[k]:.0f} {UTILITY_CONFIG[k]['unit']} {UTILITY_CONFIG[k]['label'].lower()}"
            for k in ["elec","gas","water"] if k in filters),
        "  Elec/Gas  : EIA live rates where available; water from local DB",
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
    lines += ["", "  EIA data: eia.gov | Always confirm rates with providers.", "=" * 72]
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
    extra     = (["Total $/mo"] if len(filters) > 1 else []) + ["Services Offered"]
    all_cols  = base_cols + rate_cols + cost_cols + extra + ["Region","ZIP Code","Search Date","Rate Source"]
    region    = REGION_NAMES.get(zip_code[:2], REGION_NAMES.get(zip_code[:1], "Unknown"))
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            writer.writeheader()
            for r in results:
                row = {"Provider": r["name"], "Phone": r["phone"],
                       "ZIP Code": zip_code, "Search Date": ts,
                       "Region": region, "Services Offered": r["services"],
                       "Rate Source": "EIA live + local DB"}
                if len(filters) > 1:
                    row["Total $/mo"] = f"{r['total']:.2f}" if r["services"] > 0 else "N/A"
                for key in ["elec","gas","water"]:
                    if key not in filters: continue
                    cfg  = UTILITY_CONFIG[key]
                    rate = r.get(cfg["rate_key"])
                    cost = r[cfg["cost_key"]]
                    row[f"{cfg['label']} Rate"] = f"{rate:.4f}" if rate else "N/A"
                    row[f"{cfg['label']} $/mo"] = f"{cost:.2f}" if cost else "N/A"
                writer.writerow(row)
        print(f"\n  ✅  Exported: {path}")
    except OSError as e:
        print(f"\n  ❌  Export failed: {e}")
    input("  Press Enter to continue...")

# ─────────────────────────────────────────────
#   CACHE STATUS  ← v2.0
# ─────────────────────────────────────────────

def cache_status():
    print(); divider("═")
    slow_print("  📡  LIVE RATE CACHE STATUS  ← v2.0", delay=0.015)
    divider("═")
    cache = _load_cache()
    entries = {k: v for k, v in cache.items() if k.startswith("rates_")}
    if not entries:
        print("  No live rates cached yet. Run a search to fetch them.")
    else:
        print(f"  {'STATE':<8}  {'ELEC ($/kWh)':<14}  {'GAS ($/therm)':<15}  {'PERIOD':<10}  AGE")
        divider()
        for key, entry in sorted(entries.items()):
            state  = key.replace("rates_", "")
            elec   = f"${entry['elec']:.4f}" if entry.get("elec") else "   N/A"
            gas    = f"${entry['gas']:.4f}"  if entry.get("gas")  else "   N/A"
            period = entry.get("period", "?")
            try:
                saved = datetime.fromisoformat(entry["fetched_at"])
                age   = datetime.now() - saved
                age_s = f"{int(age.total_seconds()//3600)}h ago"
                fresh = "✅" if age < timedelta(hours=CACHE_HOURS) else "⚠ stale"
            except (KeyError, ValueError):
                age_s, fresh = "?", "?"
            print(f"  {state:<8}  {elec:<14}  {gas:<15}  {period:<10}  {age_s}  {fresh}")
    divider()
    print(f"  Cache file: {CACHE_FILE}  |  Refreshes after {CACHE_HOURS} hours")
    print("  [C] Clear cache  [B] Back")
    divider()
    choice = input("  Choice: ").strip().upper()
    if choice == "C":
        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)
        rates_only = {k: v for k, v in cache.items() if not k.startswith("rates_")}
        _save_cache(rates_only)
        print("  ✅  Rate cache cleared. Next search will fetch fresh data.")
        input("  Press Enter to continue...")

# ─────────────────────────────────────────────
#   ABOUT SCREEN
# ─────────────────────────────────────────────

def about_screen():
    print(); divider("═")
    slow_print("  ℹ️   ABOUT UTILITY FINDER  v2.0", delay=0.02)
    divider("═")
    print(f"""
  What's new in v2.0:
  ───────────────────
  • Live EIA API rates for electricity + gas — auto-updates monthly
  • Rates cached locally for {CACHE_HOURS} hours so you're not hammering the API
  • Graceful offline mode — falls back to saved rates if no internet
  • Cache status screen — see what data you have and when it was fetched
  • API key saved locally — enter it once, never again

  How live rates work:
  ────────────────────
  Electricity + Gas: pulled from eia.gov as residential state averages.
  These are real, current rates — updated each month by the EIA.
  All local providers in your region are then priced against the same
  state average, so relative ranking between companies still applies.

  Water: no public API exists — always from the local database.

  Data note:
  ──────────
  EIA rates are state averages, not company-specific tariffs.
  Your actual bill will vary by plan, time-of-use pricing, and fees.
  Always confirm with the provider before switching.

  Get a free EIA key: eia.gov/opendata/register.php
""")
    divider("═")
    input("  Press Enter to return to the menu...")

# ─────────────────────────────────────────────
#   MAIN MENU
# ─────────────────────────────────────────────

def main_menu(filters, api_key):
    filter_labels = [UTILITY_CONFIG[k]["label"] for k in ["elec","gas","water"] if k in filters]
    filter_str    = " + ".join(filter_labels)
    has_results   = last_search["results"] is not None
    api_status    = "🟢 live" if api_key else "🔴 offline"

    while True:
        print(); divider()
        slow_print("  MAIN MENU", delay=0.02)
        divider()
        print(f"  [1]  Find cheapest utilities for my ZIP code")
        print(f"         ↳ Filter: {filter_str}  |  Rates: {api_status}")
        print(f"  [2]  Compare two ZIP codes side-by-side")
        print(f"  [3]  Change utility filter")
        print(f"  [4]  Change usage amounts")
        print(f"  [5]  Save / Export results"
              + (f"  (last: ZIP {last_search['zip_code']})" if has_results else "  (no results yet)"))
        print(f"  [6]  Live rate cache status  ← NEW in v2.0")
        print(f"  [7]  About / How rates work")
        print(f"  [Q]  Quit")
        divider()
        c = input("  Your choice: ").strip().upper()
        if   c == "1": return "single"
        elif c == "2": return "compare"
        elif c == "3": return "filter"
        elif c == "4": return "usage"
        elif c == "5": return "save"
        elif c == "6": return "cache"
        elif c == "7": return "about"
        elif c == "Q": return "quit"
        else: print("  ⚠  Invalid — enter 1–7 or Q.")

# ─────────────────────────────────────────────
#   ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print(BANNER)
    time.sleep(0.3)
    slow_print("  Welcome to Utility Finder v2.0!", delay=0.018)
    slow_print("  Now with live EIA API rates — electricity & gas auto-update monthly.", delay=0.014)

    # Get or prompt for API key
    api_key = load_or_prompt_api_key()

    # Pick filter and usage
    filters = pick_utility_filter()
    usage   = get_usage(filters)

    while True:
        choice = main_menu(filters, api_key)

        if choice == "single":
            zip_code = get_zip()
            run_search(zip_code, usage, filters, api_key)
            print("\n  Tip: use [5] to save or export these results.")
            input("  Press Enter to return to the menu...")

        elif choice == "compare":
            compare_mode(usage, filters, api_key)
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

        elif choice == "cache":
            cache_status()

        elif choice == "about":
            about_screen()

        elif choice == "quit":
            print()
            slow_print("  Thanks for using Utility Finder. Goodbye! 👋", delay=0.018)
            print()
            break

if __name__ == "__main__":
    main()
