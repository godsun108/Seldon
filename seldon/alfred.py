"""Parser for ALFRED/FRED-style vintage observations.

Expected CSV columns: observation_date, realtime_start, value.
The caller supplies a stable series id. No network credentials are required for
parsing downloaded/publicly obtained vintage exports.
"""
import csv,datetime as dt
from .vintage import VintagePoint

def _day(s): return (dt.date.fromisoformat(s)-dt.date(1900,1,1)).days

def parse_vintage_csv(path,series,source="ALFRED"):
    out=[]
    with open(path,newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            raw=(r.get("value") or "").strip()
            if raw in ("",".","NA","NaN"): continue
            out.append(VintagePoint(_day(r["observation_date"]),_day(r["realtime_start"]),float(raw),series,source,r["realtime_start"]))
    return out
