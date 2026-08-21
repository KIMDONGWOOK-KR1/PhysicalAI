import pandas as pd, numpy as np, glob, json, sys
SEGN=["하단직선","우측헤어핀","상단스위핑","좌상단코너","좌측복귀"]
def seg57(wp):
    i=wp*110/57
    for a,b,n in [(0,18,"하단직선"),(18,46,"우측헤어핀"),(46,76,"상단스위핑"),(76,94,"좌상단코너"),(94,111,"좌측복귀")]:
        if a<=i<b: return n
def analyze(d, label):
    d=d[d.episode_status!="prepare"].copy()
    d["seg"]=d.closest_waypoint.map(seg57)
    d["jump"]=d.groupby("episode").steer.diff().abs()
    d["tj"]=d.groupby("episode").throttle.diff().abs()
    eps=d.groupby("episode").agg(prog=("progress","max"),steps=("steps","max"),status=("episode_status","last"))
    laps=[f"{s/15:.2f}" for s,p in zip(eps.steps,eps.prog) if p>=99.9]
    print(f"\n===== {label} =====")
    print(f"완주 {sum(eps.prog>=99.9)}/{len(eps)} | 랩(steps/15): {laps} | 상태: {eps.status.value_counts().to_dict()}")
    print("조향: jump 평균 %.1f° | jump>20° %.0f%% | |steer| 평균 %.1f° | 풀조향 비율 %.0f%%" %
          (d.jump.mean(),(d.jump>20).mean()*100,d.steer.abs().mean(),(d.steer.abs()>=d.steer.abs().max()-1).mean()*100))
    print("속도: 평균 %.2f | 스텝간 변화 %.2f | 최대속도 비율 %.0f%% | 최소속도 비율 %.0f%%" %
          (d.throttle.mean(),d.tj.mean(),(d.throttle>=d.throttle.max()-0.1).mean()*100,(d.throttle<=d.throttle.min()+0.1).mean()*100))
    print(d.groupby("seg").agg(speed=("throttle","mean"),steer_abs=("steer",lambda s:s.abs().mean()),jump=("jump","mean")).loc[SEGN].round(2).to_string())
    off=d[d.episode_status=="off_track"]
    if len(off): print("탈선 위치(wp):", off.closest_waypoint.tolist())
for name in sys.argv[1:]:
    f=glob.glob(f"extracted/{name}/*/sim-trace/evaluation/*/evaluation-simtrace/*.csv")[0]
    analyze(pd.read_csv(f), name)
