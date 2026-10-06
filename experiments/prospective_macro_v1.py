"""Prospective Seldon macro feature. Research-only; preserves Experiment-004 model family."""
from __future__ import annotations
import json, time
from datetime import date
from pathlib import Path
from statistics import mean
from seldon.fred import vintage_as_known
SERIES={"unemployment":"UNRATE","cpi":"CPIAUCSL","fed_funds":"FEDFUNDS"}; K=7

def vals(p): return [(x["date"],float(x["value"])) for x in p.get("observations",[]) if x.get("value") not in ("",".",None)]
def latest(p):
    x=vals(p)
    if not x: raise ValueError("no observations")
    return x[-1][1]
def yoy(p):
    x=vals(p)
    if len(x)<13: raise ValueError("need 13 observations")
    return x[-1][1]/x[-13][1]-1 if x[-13][1] else 0.0
def state(c):
    p={}
    for k,s in SERIES.items():
        p[k]=vintage_as_known(s,c,observation_start="1998-01-01"); time.sleep(.35)
    return {"cutoff":c,"unemployment":latest(p["unemployment"]),"cpi_yoy":yoy(p["cpi"]),"fed_funds":latest(p["fed_funds"])}
def p_analogue(train,cur,key):
    fs=("unemployment","cpi_yoy","fed_funds"); scales={}
    for f in fs:
        xs=[r[f] for r in train]+[cur[f]]; mu=mean(xs); scales[f]=(mean((x-mu)**2 for x in xs)**.5) or 1
    ranked=sorted((sum(((cur[f]-r[f])/scales[f])**2 for f in fs)**.5,r[key]) for r in train)
    return sum(y for _,y in ranked[:K])/K

def main():
    historical=[f"{y}-{m:02d}-{31 if m in (1,7,10) else 30:02d}" for y in range(2000,2026) for m in (1,4,7,10)]
    today=date.today().isoformat()
    cutoffs=[c for c in historical if c<today]
    if not cutoffs or cutoffs[-1]!=today: cutoffs.append(today)
    states=[state(c) for c in cutoffs]
    for i in range(len(states)-4): states[i]["outcome_12m"]=int(states[i+4]["unemployment"]>states[i]["unemployment"])
    cur=states[-1]; train=[r for r in states[:-1] if "outcome_12m" in r]
    if len(train)<K: raise ValueError("insufficient vintage-safe training history")
    probability=p_analogue(train,cur,"outcome_12m")
    baseline=sum(r["outcome_12m"] for r in train)/len(train)
    payload={"as_of":today,"source_experiment":"seldon-prospective-macro-v1","target":"UNRATE higher 12m",
      "horizon":"12m","probability":probability,"baseline_probability":baseline,
      "evidence":{"n_train":len(train),"k":K,"model_family":"Experiment-004 nearest historical analogues"},
      "vintage_safe":True,"status":"RESEARCH_FEATURE_ONLY"}
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/seldon_prospective_macro_12m.json").write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print(json.dumps(payload,sort_keys=True))
if __name__=="__main__": main()
