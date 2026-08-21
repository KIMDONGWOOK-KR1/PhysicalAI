# A to Z Speedway - racing line reward (segment distance)
# 좌표계: 시뮬 원점 기준으로 보정 (원본 - (3.834, 2.758)), 57-waypoint 환경 검증 완료
# Continuous / steering +-25 / speed 1.5-3.0 / PPO default
import math

L = [[-1.27, -1.83, 2.88], [-0.51, -1.88, 3.00], [0.09, -1.87, 3.00],
     [0.85, -1.83, 3.00], [1.45, -1.77, 3.00], [2.21, -1.61, 2.51],
     [2.77, -1.30, 1.83], [2.94, -0.95, 1.70], [2.86, -0.49, 1.73],
     [2.57, -0.19, 1.98], [1.88, 0.02, 2.67], [1.28, 0.15, 3.00],
     [0.67, 0.41, 2.64], [0.14, 0.89, 3.00], [-0.29, 1.33, 3.00],
     [-0.90, 1.73, 2.44], [-1.50, 1.83, 2.94], [-2.25, 1.72, 2.38],
     [-2.70, 1.43, 1.87], [-2.93, 0.78, 2.47], [-2.92, 0.01, 3.00],
     [-2.78, -0.58, 3.00], [-2.43, -1.28, 2.38], [-2.01, -1.63, 2.21]]

LTOL = 0.28
STOL = 0.9
SCALE = 1.0


def reward_function(p):
    if not p['all_wheels_on_track']:
        return 1e-3

    x = p['x']
    y = p['y']
    sp = p['speed']
    n = len(L)

    # 각 선분까지의 수직 거리를 구해 가장 가까운 선분 선택
    bd = 1e9
    bt = 0.0
    bi = 0
    for i in range(n):
        ax, ay = L[i][0], L[i][1]
        j = (i + 1) % n
        bx, by = L[j][0], L[j][1]
        ex = bx - ax
        ey = by - ay
        ll = ex * ex + ey * ey
        t = ((x - ax) * ex + (y - ay) * ey) / ll
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        px = ax + t * ex
        py = ay + t * ey
        dx = x - px
        dy = y - py
        d = dx * dx + dy * dy
        if d < bd:
            bd = d
            bt = t
            bi = i

    j = (bi + 1) % n

    # 선분 위 위치에 맞춰 목표 속도를 선형 보간
    tv = (L[bi][2] + (L[j][2] - L[bi][2]) * bt) * SCALE

    lr = max(1.0 - math.sqrt(bd) / LTOL, 0.0) ** 2

    sr = max(1.0 - abs(sp - tv) / STOL, 0.0)
    if sp > tv and sr < 0.3:
        sr = 0.3

    ld = math.degrees(math.atan2(L[j][1] - L[bi][1], L[j][0] - L[bi][0]))
    df = (ld - p['heading'] + 180.0) % 360.0 - 180.0
    hm = max(1.0 - abs(df) / 30.0, 0.15)

    r = (lr * 2.0 + sr * 2.0) * hm

    if sp > 2.5 and abs(p['steering_angle']) > 20:
        r *= 0.7

    if p['steps'] > 0 and p['steps'] % 10 == 0:
        r += (p['progress'] / p['steps']) * 2.0

    return float(max(r, 1e-3))
