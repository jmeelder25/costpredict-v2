import os
import requests
import pandas as pd
from datetime import datetime

EIA_API_KEY = os.environ.get("EIA_API_KEY")
BLS_API_KEY = os.environ.get("BLS_API_KEY")  # optional, raises rate limit
USDA_AMS_API_KEY = os.environ.get("USDA_AMS_API_KEY")


# ---------------------------------------------------------------------------
# EIA — Diesel fuel (real, working)
# ---------------------------------------------------------------------------
def fetch_eia_diesel_midwest(start="2023-01-01"):
    """
    EIA Weekly U.S. No 2 Diesel Retail Prices, Midwest (PADD 2).
    Series ID verified against EIA's open data browser as of this writing —
    re-confirm at https://www.eia.gov/opendata/browser/petroleum/pri/gnd
    if this returns an empty frame, series IDs occasionally get revised.
    """
    url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[series][]": "EMD_EPD2D_PTE_R20_DPG",  # Midwest No.2 diesel retail
        "start": start,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    rows = r.json()["response"]["data"]
    df = pd.DataFrame(rows)[["period", "value"]]
    df.columns = ["date", "price_usd_per_gal"]
    df["item"] = "diesel_midwest"
    df["source"] = "EIA"
    return df


# ---------------------------------------------------------------------------
# BLS — Producer Price Index (real, working)
# ---------------------------------------------------------------------------
def fetch_bls_ppi(series_id, start_year, end_year):
    """
    BLS PPI series, e.g.:
      PCU3221--3221--  = corrugated & solid fiber box manufacturing
      WPU012202        = wheat flour milling
    Look up exact series IDs at https://data.bls.gov/PDQWebAPI/registrationEndpoint
    or the public series search at https://beta.bls.gov/dataViewer/
    """
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API error: {data.get('message')}")
    rows = data["Results"]["series"][0]["data"]
    df = pd.DataFrame(rows)[["year", "period", "periodName", "value"]]
    df["date"] = pd.to_datetime(df["year"] + df["periodName"], format="%Y%B", errors="coerce")
    df = df.rename(columns={"value": "index_value"})
    df["series_id"] = series_id
    df["source"] = "BLS PPI"
    return df[["date", "index_value", "series_id", "source"]]


# ---------------------------------------------------------------------------
# USDA AMS — STUB, unverified
# ---------------------------------------------------------------------------
def fetch_usda_ams_dairy(commodity="butter"):
    """
    STUB. USDA AMS publishes via MyMarketNews (mymarketnews.ams.usda.gov) and
    also via ams.usda.gov/mnreports for legacy report text/CSV. Neither has
    a single simple "get me butter price" endpoint — you look up a specific
    report slug/ID per commodity/region first. I have not been able to
    verify a working request from my sandbox. Do this before relying on it:
      1. Find the report at https://mymarketnews.ams.usda.gov/public_data
      2. Confirm the report ID and required API key header
      3. Replace this stub with the real request
    """
    raise NotImplementedError(
        "Confirm the MyMarketNews report ID and request shape before using this."
    )


# ---------------------------------------------------------------------------
# World Bank Pink Sheet — STUB, unverified
# ---------------------------------------------------------------------------
def fetch_world_bank_pink_sheet():
    """
    STUB. World Bank publishes a monthly commodity price workbook (the
    "Pink Sheet") as a public XLSX with no API key required, historically at
    a URL under worldbank.org/en/research/commodity-markets. The exact URL
    changes when they refresh the file, so confirm the current link
    yourself, then something like:

        df = pd.read_excel(CURRENT_URL, sheet_name="Monthly Prices", skiprows=4)

    will get you cocoa, coffee, wheat, and soybean oil series. I have not
    verified today's exact URL or sheet layout from my sandbox.
    """
    raise NotImplementedError("Confirm the current Pink Sheet download URL before using this.")


# ---------------------------------------------------------------------------
# MVP item registry — what's real vs. what you still need to wire up
# ---------------------------------------------------------------------------
MVP_ITEMS = {
    "diesel_midwest":   {"fetch": fetch_eia_diesel_midwest, "status": "real"},
    "corrugated_boxes": {"fetch": lambda: fetch_bls_ppi("PCU3221--3221--", 2020, datetime.now().year), "status": "real"},
    "flour":            {"fetch": lambda: fetch_bls_ppi("WPU012202", 2020, datetime.now().year), "status": "real"},
    "butter":           {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "eggs":             {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "milk":             {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "cheese":           {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "beef":             {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "chicken":          {"fetch": fetch_usda_ams_dairy, "status": "stub"},
    "vegetable_oil":    {"fetch": fetch_world_bank_pink_sheet, "status": "stub"},
    "cocoa":            {"fetch": fetch_world_bank_pink_sheet, "status": "stub"},
    "coffee":           {"fetch": fetch_world_bank_pink_sheet, "status": "stub"},
}


def run_all(output_dir="data/national_series"):
    os.makedirs(output_dir, exist_ok=True)
    for item, meta in MVP_ITEMS.items():
        if meta["status"] != "real":
            print(f"SKIP  {item}: still a stub, see docstring")
            continue
        try:
            df = meta["fetch"]()
            path = os.path.join(output_dir, f"{item}.csv")
            df.to_csv(path, index=False)
            print(f"OK    {item}: {len(df)} rows -> {path}")
        except Exception as e:
            print(f"ERROR {item}: {e}")


if __name__ == "__main__":
    run_all()
