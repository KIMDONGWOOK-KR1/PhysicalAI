import json, glob, sys
from collections import defaultdict
for d in sorted(glob.glob("extracted/*-logs/*/metrics/training/*.json")):
    name = d.replace("\\","/").split("/")[1]
    m = json.load(open(d))["metrics"]
    tr = [x for x in m if x["phase"]=="training"]
    ev = [x for x in m if x["phase"]=="evaluation"]
    print(f"\n===== {name} =====")
    print(f"training episodes: {len(tr)}, eval episodes: {len(ev)}, iterations: {max(x.get('trial',0) for x in tr) if tr else 0}")
    # training completion by chunk of 25 eps
    print("-- training: per-iteration avg completion% / avg reward (25 eps each)")
    for i in range(0, len(tr), 25):
        chunk = tr[i:i+25]
        comp = sum(x["completion_percentage"] for x in chunk)/len(chunk)
        rew = sum(x["reward_score"] for x in chunk)/len(chunk)
        full = sum(1 for x in chunk if x["completion_percentage"]>=100)
        print(f"iter {i//25:3d}: comp {comp:5.1f}%  full {full:2d}/{len(chunk)}  reward {rew:8.1f}")
    print("-- evaluation (grouped by trial)")
    byt = defaultdict(list)
    for x in ev: byt[x["trial"]].append(x)
    for t in sorted(byt):
        eps = byt[t]
        laps = [x["elapsed_time_in_milliseconds"]/1000 for x in eps if x["completion_percentage"]>=100]
        offs = [x.get("off_track_count",0) for x in eps]
        print(f"  eval@iter{t:3d}: {len(laps)}/{len(eps)} complete | laps {[round(l,2) for l in laps]} | offtrack {offs}")
