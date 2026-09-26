"""SELDON vintage-grade protocol scaffold.

Usage:
 python experiments/vintage_protocol.py SERIES=file.csv [SERIES=file.csv ...]

This validates that historical revisions are reconstructed as-of each cutoff.
It does not manufacture a forecast when required vintage files are absent.
"""
import sys
from seldon.alfred import parse_vintage_csv
from seldon.vintage import as_known,fingerprint

def main(args):
    if not args: raise SystemExit("Provide SERIES=path.csv vintage exports")
    points=[]
    for arg in args:
        series,path=arg.split("=",1); points.extend(parse_vintage_csv(path,series))
    releases=sorted(set(p.available_at for p in points))
    print("points",len(points),"releases",len(releases),"fingerprint",fingerprint(points))
    for cutoff in releases[-5:]:
        known=as_known(points,cutoff)
        print("cutoff",cutoff,"known_observations",len(known))

if __name__=="__main__": main(sys.argv[1:])
