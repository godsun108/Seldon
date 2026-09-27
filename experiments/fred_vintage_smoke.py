"""Small CI smoke pull: proves FRED auth + vintage retrieval without leaking key."""
import json, os
from pathlib import Path
from seldon.fred import DEFAULT_SERIES, vintage_as_known

def main():
    cutoff=os.environ.get("SELDON_CUTOFF","2020-01-31")
    start=os.environ.get("SELDON_OBSERVATION_START","2019-01-01")
    summary={"schema":"seldon.fred.smoke.v1","cutoff":cutoff,"series":{}}
    for label,series_id in DEFAULT_SERIES.items():
        payload=vintage_as_known(series_id,cutoff,observation_start=start)
        obs=payload.get("observations",[])
        valid=[x for x in obs if x.get("value") not in (None,"",".")]
        summary["series"][label]={
            "series_id":series_id,
            "observation_count":len(valid),
            "first_observation":valid[0]["date"] if valid else None,
            "last_observation":valid[-1]["date"] if valid else None,
            "realtime_start":payload.get("realtime_start"),
            "realtime_end":payload.get("realtime_end"),
        }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/fred_smoke_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
