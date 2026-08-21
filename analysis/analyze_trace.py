import pandas as pd, numpy as np, glob, os
line = pd.read_csv("racing_line_110.csv")
SEG = [(0,18,"하단직선"),(18,46,"우측헤어핀"),(46,76,"상단스위핑"),(76,94,"좌상단코너"),(94,111,"좌측복귀")]
def seg(wp):
    for a,b,n in SEG:
        if a<=wp<b: return n
    return "?"
for run in sorted(glob.glob("extracted/*-logs/*/sim-trace/training/*/training-simtrace")):
    name = "test1-1 (max3.0)" if "lh843" in run else "test1-2 (max3.5)"
    files = sorted(glob.glob(run+"/*-iteration.csv"), key=lambda f:int(os.path.basename(f).split("-")[0]))
    last = files[-10:]  # last 10 iterations
    df = pd.concat([pd.read_csv(f) for f in last])
    df = df[df.episode_status!="prepare"]
    print(f"\n===== {name}  (last 10 iterations, {df.episode.nunique()} episodes) =====")
    # off-track locations
    off = df[df.episode_status=="off_track"]
    print("탈선 위치 분포 (closest_waypoint, 구간별):")
    print(off.closest_waypoint.map(seg).value_counts().to_string())
    print("탈선 waypoint top10:", off.closest_waypoint.value_counts().head(10).to_dict())
    # speed profile per segment (completed laps only)
    comp_eps = df.groupby("episode").progress.max(); comp_eps = comp_eps[comp_eps>=99.9].index
    c = df[df.episode.isin(comp_eps)]
    print(f"완주 에피소드 {len(comp_eps)}개 기준 구간별 평균 throttle(명령속도) vs 최적라인 목표속도:")
    c = c.assign(seg=c.closest_waypoint.map(seg))
    line_seg = line.assign(seg=line.idx.map(seg)).groupby("seg").target_speed.mean()
    act = c.groupby("seg").agg(throttle=("throttle","mean"), steer_abs=("steer", lambda s: s.abs().mean()))
    print(pd.concat([act, line_seg.rename("opt_speed")],axis=1).loc[[s[2] for s in SEG]].round(2).to_string())
    # lateral deviation from racing line
    lx, ly = line.x.values, line.y.values
    def dist(r):
        d = np.hypot(lx-r.X, ly-r.Y); return d.min()
    c = c.assign(dline=c.apply(dist,axis=1))
    print("최적라인으로부터 거리(m): 평균 %.3f / 90%% %.3f / 최대 %.3f" % (c.dline.mean(), c.dline.quantile(.9), c.dline.max()))
    print(c.groupby("seg").dline.mean().loc[[s[2] for s in SEG]].round(3).to_string())
    # lap time of completed episodes (steps*1/15)
    lt = c.groupby("episode").steps.max()/15
    print("완주 랩타임(학습중): min %.2f  mean %.2f  max %.2f" % (lt.min(), lt.mean(), lt.max()))
