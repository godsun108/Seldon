"""SELDON Experiment 003: frozen temporal replication of Experiment 002.

Frozen before scoring:
- Replicate the Experiment 002 hypothesis without feature/model retuning.
- Target: US unemployment higher 12 months ahead.
- Features: UNRATE level, CPIAUCSL trailing 12m change, FEDFUNDS level.
- Cutoffs: Jan/Apr/Jul/Oct month-end, 2000-2024.
- k: 7 nearest historical analogues.
- Primary replication window: 2020-01-31 onward.
- Primary score: Brier skill versus expanding historical-frequency baseline.
"""
import json, time
from pathlib import Path
from statistics import mean
from seldon.fred import vintage_as_known

SERIES={"unemployment":"UNRATE","cpi":"CPIAUCSL","fed_funds":"FEDFUNDS"}
MONTHS=(1,4,7,10)
CUTOFFS=[f"{y}-{m:02d}-{31 if m in (1,7,10) else 30:02d}" for y in range(2000,2025) for m in MONTHS]
HORIZON_STEPS=4
K=7
REPLICATION_START="2020-01-31"

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
def p_analogue(train,cur):
    fs=("unemployment","cpi_yoy","fed_funds"); scales={}
    for f in fs:
        xs=[r[f] for r in train]+[cur[f]]; mu=mean(xs); scales[f]=(mean((x-mu)**2 for x in xs)**.5) or 1
    ranked=sorted((sum(((cur[f]-r[f])/scales[f])**2 for f in fs)**.5,r["outcome_higher"]) for r in train)
    chosen=ranked[:K]
    return sum(y for _,y in chosen)/len(chosen)
def summarize(rs):
    if not rs:return {"n":0}
    mb=mean(r["brier"] for r in rs); bb=mean(r["baseline_brier"] for r in rs)
    return {"n":len(rs),"mean_brier":mb,"baseline_mean_brier":bb,"brier_skill_vs_baseline":1-mb/bb}
def main():
    states=[state(c) for c in CUTOFFS]
    for i in range(len(states)-HORIZON_STEPS):
        states[i]["outcome_higher"]=int(states[i+HORIZON_STEPS]["unemployment"]>states[i]["unemployment"])
    records=[]
    for i in range(12,len(states)-HORIZON_STEPS):
        train=[r for r in states[:i] if "outcome_higher" in r]
        cur=states[i]; p=p_analogue(train,cur); y=cur["outcome_higher"]
        base=sum(r["outcome_higher"] for r in train)/len(train)
        records.append({"cutoff":cur["cutoff"],"p_higher":p,"actual_higher":y,"brier":(p-y)**2,"baseline_p":base,"baseline_brier":(base-y)**2})
    replication=[r for r in records if r["cutoff"]>=REPLICATION_START]
    result={"schema":"seldon.experiment.003.v1","status":"FROZEN_BEFORE_SCORING","predefined":{"replicates":"experiment_002","target":"UNRATE higher 12 months ahead","features":["UNRATE level","CPIAUCSL 12m change","FEDFUNDS level"],"cutoff_frequency":"quarterly","k":K,"replication_start":REPLICATION_START,"primary_metric":"Brier skill versus expanding historical-frequency baseline"},"vintage_safe":True,"replication":summarize(replication),"all_context":summarize(records),"records":replication}
    Path("artifacts").mkdir(exist_ok=True); Path("artifacts/experiment_003.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
if __name__=="__main__":main()
