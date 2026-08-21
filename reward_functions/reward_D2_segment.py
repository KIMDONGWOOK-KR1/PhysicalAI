# A to Z Speedway - racing line reward v2 (segment distance)
# 좌표계: 시뮬 원점 기준 (57-waypoint 환경 검증 완료)
# Continuous / steering +-25 / speed 1.5-3.0
import math

L = [[-1.27, -1.83, 2.88], [-0.51, -1.88, 3.00], [0.09, -1.87, 3.00],
     [0.85, -1.83, 3.00], [1.45, -1.77, 3.00], [2.21, -1.61, 2.51],
     [2.77, -1.30, 1.83], [2.94, -0.95, 1.70], [2.86, -0.49, 1.73],
     [2.57, -0.19, 1.98], [1.88, 0.02, 2.67], [1.28, 0.15, 3.00],
     [0.67, 0.41, 2.64], [0.14, 0.89, 3.00], [-0.29, 1.33, 3.00],
     [-0.90, 1.73, 2.44], [-1.50, 1.83, 2.94], [-2.25, 1.72, 2.38],
     [-2.70, 1.43, 1.87], [-2.93, 0.78, 2.47], [-2.92, 0.01, 3.00],
     [-2.78, -0.58, 3.00], [-2.43, -1.28, 2.38], [-2.01, -1.63, 2.21]]

LTOL = 0.40
STOL = 0.9
SCALE = 1.0
PREV = {"steer": 0.0}


def reward_function(p):
    if not p['all_wheels_on_track']:
        return 1e-3

    x = p['x']
    y = p['y']
    sp = p['speed']
    st = p['steering_angle']
    steps = p['steps']
    n = len(L)

    if steps <= 1:
        PREV["steer"] = st

    bd = 1e9
    bt = 0.0
    bi = 0
    for i in range(n):
        ax, ay = L[i][0], L[i][1]
        j = (i + 1) % n
        bx, by = L[j][0], L[j][1]
        ex = bx - ax
        ey = by - ay
        t = ((x - ax) * ex + (y - ay) * ey) / (ex * ex + ey * ey)
        t = min(max(t, 0.0), 1.0)
        dx = x - (ax + t * ex)
        dy = y - (ay + t * ey)
        d = dx * dx + dy * dy
        if d < bd:
            bd = d
            bt = t
            bi = i

    j = (bi + 1) % n
    tv = (L[bi][2] + (L[j][2] - L[bi][2]) * bt) * SCALE

    # 라인 거리 (선형, 허용폭 0.40)
    lr = max(1.0 - math.sqrt(bd) / LTOL, 0.0)

    # 목표속도 부합
    sr = max(1.0 - abs(sp - tv) / STOL, 0.0)
    if sp > tv and sr < 0.3:
        sr = 0.3

    # 진행 방향 정렬 (배율)
    ld = math.degrees(math.atan2(L[j][1] - L[bi][1], L[j][0] - L[bi][0]))
    df = (ld - p['heading'] + 180.0) % 360.0 - 180.0
    hm = max(1.0 - abs(df) / 30.0, 0.15)

    # 조향 평활화 (배율): 스텝간 급변 억제
    jump = abs(st - PREV["steer"])
    sm = 1.0 - min(jump, 25.0) / 25.0 * 0.5

    # 시간 압박 (매 스텝)
    pace = (p['progress'] / float(steps)) if steps > 0 else 0.0

    r = (lr * 2.0 + sr * 2.0 + pace * 1.5) * hm * sm

    if sp > 2.5 and abs(st) > 20:
        r *= 0.7
    if p['progress'] >= 100:
        r += 10.0

    PREV["steer"] = st
    return float(max(r, 1e-3))
