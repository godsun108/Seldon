"""Adapters for real public historical indicators.

SELDON uses the World Bank Indicators API because annual observations are public,
long-running and machine-readable. Network access is optional: callers can cache
raw JSON and pass it to parse_world_bank().
"""
import json
from urllib.request import urlopen

WORLD_BANK={
 "gdp_growth":"NY.GDP.MKTP.KD.ZG",
 "inflation":"FP.CPI.TOTL.ZG",
 "unemployment":"SL.UEM.TOTL.ZS",
 "population_growth":"SP.POP.GROW",
}

def fetch_world_bank(country,indicator,start=1960,end=2025):
    code=WORLD_BANK[indicator]
    url=f"https://api.worldbank.org/v2/country/{country}/indicator/{code}?date={start}:{end}&format=json&per_page=1000"
    with urlopen(url,timeout=30) as r:return json.load(r)

def parse_world_bank(payload):
    rows=payload[1] if isinstance(payload,list) and len(payload)>1 else []
    return {int(r["date"]):float(r["value"]) for r in rows if r.get("value") is not None}
