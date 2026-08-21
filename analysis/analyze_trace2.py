import pandas as pd, numpy as np, glob, os
line = pd.read_csv("racing_line_110.csv")
# estimate frame offset: compare bounding box centers of trace vs line (same track, different origin)
allf = sorted(glob.glob("extracted/*lh843*/*/sim-trace/training/*/training-simtrace/*.csv"))
big = pd.concat([pd.read_csv(f) for f in allf]); big=big[(big.episode_status!="prepare")&(big.all_wheels_on_track)]
off = np.array([ (big.X.min()+big.X.max())/2 - (line.x.min()+line.x.max())/2, (big.Y.min()+big.Y.max())/2 - (line.y.min()+line.y.max())/2 ])
print("frame offset (sim - ours):", off.round(3))
lx, ly = line.x.values+off[0], line.y.values+off[1]
# sim waypoint -> our idx mapping by nearest line point to waypoint centroid
wpc = big.groupby("closest_waypoint")[["X","Y"]].median()
def seg57(wp):
    # map 57-wp index to 110 scale
    i = wp*110/57
    for a,b,n in [(0,18,"하단직선"),(18,46,"우측헤어핀"),(46,76,"상단스위핑"),(76,94,"좌상단코너"),(94,111,"좌측복귀")]:
        if a<=i<b: return n
SEGN=["하단직선","우측헤어핀","상단스위핑","좌상단코너","좌측복귀"]
for run in sorted(glob.glob("extracted/*-logs/*/sim-trace/training/*/training-simtrace")):
    name = "test1-1 (max3.0)" if "lh843" in run else "test1-2 (max3.5)"
    files = sorted(glob.glob(run+"/*-iteration.csv"), key=lambda f:int(os.path.basename(f).split("-")[0]))
    df = pd.concat([pd.read_csv(f) for f in files[-10:]]); df=df[df.episode_status!="prepare"]
    df = df.assign(seg=df.closest_waypoint.map(seg57))
    print(f"\n===== {name}  (last 10 iters, {df.episode.nunique()} eps) =====")
    o = df[df.episode_status=="off_track"]
    print("탈선 구간 분포:", o.seg.value_counts().to_dict())
    print("탈선 wp(57기준) top8:", o.closest_waypoint.value_counts().head(8).to_dict())
    comp = df.groupby("episode").progress.max(); comp=comp[comp>=99.9].index
    c = df[df.episode.isin(comp)].copy()
    c["dline"]=np.hypot(lx[None,:]-c.X.values[:,None], ly[None,:]-c.Y.values[:,None]).min(1)
    c["steer_jump"]=c.groupby("episode").steer.diff().abs()
    line_seg = line.assign(seg=line.idx.map(lambda i: seg57(i*57/110))).groupby("seg").target_speed.mean()
    g=c.groupby("seg").agg(cmd_speed=("throttle","mean"), full_thr=("throttle",lambda s:(s>=2.9).mean()), min_thr=("throttle",lambda s:(s<=1.2).mean()),
                           steer_abs=("steer",lambda s:s.abs().mean()), steer_jump=("steer_jump","mean"), dist_line=("dline","mean"))
    g["opt_speed"]=line_seg
    print(f"완주 {len(comp)}개 에피소드 기준:")
    print(g.loc[SEGN].round(2).to_string())
    print("전체: 최적라인 거리 평균 %.2f m (90%% %.2f) | 스텝간 조향 변화 평균 %.1f° | throttle 최대치 비율 %.0f%%, 최소치 비율 %.0f%%" %
          (c.dline.mean(), c.dline.quantile(.9), c.steer_jump.mean(), (c.throttle>=2.9).mean()*100, (c.throttle<=1.2).mean()*100))
    lt=c.groupby("episode").steps.max()/15
    print("학습중 완주 랩타임: min %.2f mean %.2f max %.2f" % (lt.min(),lt.mean(),lt.max()))
