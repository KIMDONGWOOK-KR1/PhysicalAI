# v2 (D2a): disc1 clone용. 평활화 강화 + 속도 항 8배
import math

PREV = {"steer": 0.0}


def reward_function(params):
    if not params["all_wheels_on_track"]:
        return 1e-3

    steps = params["steps"]
    progress = params["progress"]
    speed = params["speed"]
    steer = params["steering_angle"]
    heading = params["heading"]
    wps = params["waypoints"]
    nxt = params["closest_waypoints"][1]
    n = len(wps)

    if steps <= 1:
        PREV["steer"] = steer

    def ang(i, j):
        a, b = wps[i % n], wps[j % n]
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    # 1. 전방 곡률(도) -> 목표속도. 직선 3.0, 헤어핀 1.7
    curve = abs((ang(nxt + 3, nxt + 6) - ang(nxt, nxt + 3) + 180) % 360 - 180)
    target = max(1.7, min(3.0, 3.0 - 0.02 * curve))
    speed_score = max(0.0, 1.0 - abs(speed - target) / 1.2)

    # 2. 조향 평활화 (배율). v2: 급변 0.7, 직선 과조향 0.5로 강화
    jump = abs(steer - PREV["steer"])
    smooth = 1.0 - min(jump, 30.0) / 30.0 * 0.7
    if curve < 10:
        smooth *= 1.0 - min(abs(steer), 30.0) / 30.0 * 0.5

    # 3. 진행 방향 정렬 (배율)
    diff = abs((ang(nxt, nxt + 2) - heading + 180) % 360 - 180)
    align = max(0.2, 1.0 - diff / 45.0)

    # 4. 시간 압박 (기존 모델과 동일 골격)
    pace = (progress / float(steps)) * 100.0 if steps > 0 else 0.0

    reward = (pace + 8.0 * speed ** 2 * speed_score) * smooth * align
    if progress >= 100:
        reward += 100.0

    PREV["steer"] = steer
    return float(max(reward, 1e-3))
