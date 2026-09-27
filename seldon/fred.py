"""Authenticated FRED/ALFRED data client for vintage-safe SELDON inputs.

The API key is read only from FRED_API_KEY. It is never logged or written to
artifacts. FRED's series/observations endpoint also exposes ALFRED realtime
vintages through realtime_start/realtime_end parameters.
"""
import json, os
from urllib.parse import urlencode
from urllib.request import urlopen

BASE="https://api.stlouisfed.org/fred"
DEFAULT_SERIES={
    "gdp":"GDP",
    "cpi":"CPIAUCSL",
    "unemployment":"UNRATE",
    "fed_funds":"FEDFUNDS",
}

def _key():
    key=os.environ.get("FRED_API_KEY","").strip()
    if not key:
        raise RuntimeError("Missing FRED_API_KEY. Add it as a GitHub Actions repository secret or local environment variable.")
    return key

def request(endpoint, **params):
    """Make one authenticated FRED request and return decoded JSON."""
    query={"api_key":_key(),"file_type":"json",**params}
    url=f"{BASE}/{endpoint}?{urlencode(query)}"
    with urlopen(url,timeout=30) as response:
        return json.load(response)

def series_observations(series_id, observation_start=None, observation_end=None,
                        realtime_start=None, realtime_end=None, limit=100000):
    """Fetch observations, optionally frozen to an ALFRED realtime window."""
    p={"series_id":series_id,"limit":limit}
    for k,v in {
        "observation_start":observation_start,
        "observation_end":observation_end,
        "realtime_start":realtime_start,
        "realtime_end":realtime_end,
    }.items():
        if v is not None:p[k]=v
    return request("series/observations",**p)

def vintage_as_known(series_id, cutoff, observation_start=None):
    """Return the series exactly as FRED/ALFRED reports it for cutoff date."""
    return series_observations(
        series_id,
        observation_start=observation_start,
        realtime_start=cutoff,
        realtime_end=cutoff,
    )
