# A to Z Speedway - racing line reward (segment distance)
# Continuous / steering +-25 / speed 1.5-3.0 / PPO default
import math

L = [[2.56, 0.93, 2.88], [3.32, 0.88, 3.00], [3.92, 0.89, 3.00],
     [4.68, 0.93, 3.00], [5.28, 0.99, 3.00], [6.04, 1.15, 2.51],
     [6.60, 1.46, 1.83], [6.77, 1.81, 1.70], [6.69, 2.27, 1.73],
     [6.40, 2.57, 1.98], [5.71, 2.78, 2.67], [5.11, 2.91, 3.00],
     [4.50, 3.17, 2.64], [3.97, 3.65, 3.00], [3.54, 4.09, 3.00],
     [2.93, 4.49, 2.44], [2.33, 4.59, 2.94], [1.58, 4.48, 2.38],
     [1.13, 4.19, 1.87], [0.90, 3.54, 2.47], [0.91, 2.77, 3.00],
     [1.05, 2.18, 3.00], [1.40, 1.48, 2.38], [1.82, 1.13, 2.21]]

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
