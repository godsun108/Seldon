"""SELDON Experiment 001: vintage-safe 12-month unemployment direction."""
import json
from pathlib import Path
from statistics import mean
from seldon.fred import vintage_as_known
SERIES={"unemployment":"UNRATE","cpi":"CPIAUCSL","fed_funds":"FEDFUNDS"}
CUTOFFS=[f"{y}-01-31" for y in range(2000,2025)]
def values(payload): return [(x["date"],float(x["value"])) for x in payload.get("observations",[]) if x.get("value") not in ("",".",None)]
def latest(payload):
    xs=values(payload)
    if not xs: raise ValueError("no usable observations")
    return xs[-1][1]
def pct_change_12m(payload):
    xs=values(payload)
    if len(xs)<13: raise ValueError("need 13 monthly observations")
    a,b=xs[-13][1],xs[-1][1]
    return b/a-1 if a else 0.0
def state(cutoff):
    raw={k:vintage_as_known(s,cutoff,observation_start="1998-01-01") for k,s in SERIES.items()}
    return {"cutoff":cutoff,"unemployment":latest(raw["unemployment"]),"cpi_yoy":pct_change_12m(raw["cpi"]),"fed_funds":latest(raw["fed_funds"])}
def probability(train,current,k=5):
    features=("unemployment","cpi_yoy","fed_funds"); scales={}
    for f in features:
        xs=[r[f] for r in train]+[current[f]]; mu=mean(xs); var=mean((x-mu)**2 for x in xs)
        scales[f]=(var**0.5) or 1.0
    ranked=[]
    for r in train:
        d=sum(((current[f]-r[f])/scales[f])**2 for f in features)**0.5
        ranked.append((d,r["outcome_higher"]))
    ranked.sort(key=lambda x:x[0]); chosen=ranked[:k]
    return sum(y for _,y in chosen)/len(chosen)
def main():
    states=[state(c) for c in CUTOFFS]
    for i,r in enumerate(states[:-1]): r["outcome_higher"]=int(states[i+1]["unemployment"]>r["unemployment"])
    records=[]
    for i in range(6,len(states)-1):
        train=states[:i]; current=states[i]; p=probability(train,current); y=current["outcome_higher"]
        baseline=sum(r["outcome_higher"] for r in train)/len(train)
        records.append({"cutoff":current["cutoff"],"p_higher":p,"actual_higher":y,"brier":(p-y)**2,"baseline_p":baseline,"baseline_brier":(baseline-y)**2})
    mb=mean(r["brier"] for r in records); bb=mean(r["baseline_brier"] for r in records)
    result={"schema":"seldon.experiment.001.v1","question":"Will US unemployment be higher 12 months ahead?","features":["UNRATE level","CPIAUCSL 12m change","FEDFUNDS level"],"vintage_safe":True,"n":len(records),"mean_brier":mb,"baseline_mean_brier":bb,"brier_skill_vs_baseline":1-mb/bb,"records":records}
    Path("artifacts").mkdir(exist_ok=True); Path("artifacts/experiment_001.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
if __name__=="__main__": main()
