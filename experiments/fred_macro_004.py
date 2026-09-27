"""SELDON Experiment 004: adversarial multi-horizon battery.

Frozen before scoring.
Model family is inherited unchanged from Experiments 002/003.
Primary purpose: try to falsify/generalize the observed unemployment signal.

Predefined:
- Target: whether UNRATE is higher at 6, 12, and 18 months.
- Features: UNRATE level, CPIAUCSL trailing 12m change, FEDFUNDS level.
- Quarterly vintage-safe cutoffs, 2000-2024.
- k=7 nearest historical analogues; no tuning by horizon.
- Evaluation window: 2015 onward.
- Baselines: expanding historical event frequency and persistence (p=0.5).
- Metrics: Brier score, Brier skill, calibration MAE.
- No parameter changes after results are observed.
"""
import json, time
from pathlib import Path
from statistics import mean
from seldon.fred import vintage_as_known

SERIES={"unemployment":"UNRATE","cpi":"CPIAUCSL","fed_funds":"FEDFUNDS"}
MONTHS=(1,4,7,10)
CUTOFFS=[f"{y}-{m:02d}-{31 if m in (1,7,10) else 30:02d}" for y in range(2000,2025) for m in MONTHS]
HORIZONS={"6m":2,"12m":4,"18m":6}
K=7
EVAL_START="2015-01-31"

def vals(p): return [(x["date"],float(x["value"])) for x in p.get("observations",[]) if x.get("value") not in ("",".",None)]
def latest(p):
    x=vals(p)
    if not x: raise ValueError("no observations")
    return x[-1][1]
def yoy(p):
    x=vals(p)
    if len(x)<13: raise ValueError("need 13 observations")
    a,b=x[-13][1],x[-1][1]
    return b/a-1 if a else 0.0
def state(c):
    p={}
    for k,s in SERIES.items():
        p[k]=vintage_as_known(s,c,observation_start="1998-01-01")
        time.sleep(0.35)
    return {"cutoff":c,"unemployment":latest(p["unemployment"]),"cpi_yoy":yoy(p["cpi"]),"fed_funds":latest(p["fed_funds"])}
def p_analogue(train,cur,outcome_key):
    fs=("unemployment","cpi_yoy","fed_funds"); scales={}
    for f in fs:
        xs=[r[f] for r in train]+[cur[f]]; mu=mean(xs); scales[f]=(mean((x-mu)**2 for x in xs)**.5) or 1
    ranked=sorted((sum(((cur[f]-r[f])/scales[f])**2 for f in fs)**.5,r[outcome_key]) for r in train)
    return sum(y for _,y in ranked[:K])/K
def calibration_mae(rs):
    if not rs:return None
    bins={}
    for r in rs: bins.setdefault(round(r["p_higher"],1),[]).append(r)
    return sum(len(v)*abs(mean(x["p_higher"] for x in v)-mean(x["actual_higher"] for x in v)) for v in bins.values())/len(rs)
def summarize(rs):
    if not rs:return {"n":0}
    mb=mean(r["brier"] for r in rs); hb=mean(r["historical_brier"] for r in rs); pb=mean(r["persistence_brier"] for r in rs)
    return {"n":len(rs),"mean_brier":mb,"historical_frequency_brier":hb,"skill_vs_historical_frequency":1-mb/hb,"persistence_brier":pb,"skill_vs_persistence":1-mb/pb,"calibration_mae":calibration_mae(rs)}
def main():
    states=[state(c) for c in CUTOFFS]
    results={}
    for label,steps in HORIZONS.items():
        key="outcome_"+label
        for i in range(len(states)-steps):
            states[i][key]=int(states[i+steps]["unemployment"]>states[i]["unemployment"])
        records=[]
        for i in range(12,len(states)-steps):
            train=[r for r in states[:i] if key in r]
            cur=states[i]; y=cur[key]; p=p_analogue(train,cur,key)
            hist=sum(r[key] for r in train)/len(train)
            records.append({"cutoff":cur["cutoff"],"p_higher":p,"actual_higher":y,"brier":(p-y)**2,"historical_p":hist,"historical_brier":(hist-y)**2,"persistence_p":0.5,"persistence_brier":0.25})
        ev=[r for r in records if r["cutoff"]>=EVAL_START]
        results[label]={"evaluation":summarize(ev),"records":ev}
    result={"schema":"seldon.experiment.004.v1","status":"FROZEN_BEFORE_SCORING","predefined":{"target":"UNRATE higher at each horizon","horizons":HORIZONS,"features":["UNRATE level","CPIAUCSL 12m change","FEDFUNDS level"],"cutoff_frequency":"quarterly","k":K,"evaluation_start":EVAL_START,"baselines":["expanding historical frequency","p=0.5 persistence/null"],"metrics":["Brier score","Brier skill","calibration MAE"]},"vintage_safe":True,"results":results}
    Path("artifacts").mkdir(exist_ok=True); Path("artifacts/experiment_004.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"schema":result["schema"],"status":result["status"],"predefined":result["predefined"],"vintage_safe":True,"scores":{k:v["evaluation"] for k,v in results.items()}},indent=2))
if __name__=="__main__":main()
