"""First real-data SELDON experiment: US macro state -> next-year GDP-growth direction.

This is an experiment, not a claim of predictive power. For strict vintage-grade
research, replace current World Bank historical series with archived release
vintages carrying true publication timestamps.
"""
from seldon.core import Observation
from seldon.datasets import fetch_world_bank,parse_world_bank
from seldon.walkforward import walk_forward,summary

FEATURES=("inflation","unemployment","population_growth")
TARGET="gdp_growth"

def build():
    series={x:parse_world_bank(fetch_world_bank("USA",x)) for x in (*FEATURES,TARGET)}
    years=sorted(set.intersection(*(set(v) for v in series.values())))
    # Conservative annual availability proxy: year y is admitted at y+1.
    # This is NOT a substitute for true vintage/release timestamps.
    return [Observation(y,y+1,{k:series[k][y] for k in series}) for y in years]

def main():
    h=build(); records=walk_forward(h,TARGET,FEATURES,horizon=1,k=7,min_cutoff=1975)
    print("SELDON WORLD-STATE EXPERIMENT v1")
    print("records",summary(records))
    if records:
        worst=max(records,key=lambda r:r.deviation)
        print("largest_deviation",worst)

if __name__=="__main__":main()
