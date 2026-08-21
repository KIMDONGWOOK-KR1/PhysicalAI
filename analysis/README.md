# 로그 분석 스크립트

DeepRacer 학습/평가 로그(tar.gz)를 `extracted/<폴더명>/` 아래에 풀어 놓고 실행한다.

| 스크립트 | 입력 | 출력 |
|---|---|---|
| `analyze_metrics.py` | `extracted/*-logs/*/metrics/training/*.json` | iteration별 완주율·보상·랩타임 추이 |
| `analyze_trace.py` | sim-trace CSV | 에피소드별 랩타임, 탈선 위치 |
| `analyze_trace2.py` | sim-trace CSV + `data/racing_line_110.csv` | 최적 라인 대비 이탈 거리, 조향/throttle 통계 |
| **`compare_eval.py <폴더>...`** | 평가 로그 폴더 여러 개 | 모델 간 비교표: 완주 수, 랩타임, **스텝당 조향 변화(jump)**, jump>20° 비율, 풀조향 비율, 구간별 평균 속도, action 사용 분포 |

## 핵심 지표

- **steer jump** (°/step): 직전 스텝 대비 조향 변화량 평균. 실물 서보 부담의 대리 지표. test1-1 16.6 → disc2 계열 8°대
- **풀조향 비율**: |steer| ≥ 24° 스텝 비율
- **구간별 속도**: waypoint를 5구간(하단직선 / 우측헤어핀 / 상단스위핑 / 좌상단코너 / 좌측복귀)으로 매핑. 헤어핀 < 직선이 정상 순서

## 예시

```bash
mkdir -p extracted/eval_disc2-v2 && tar -xzf logs/eval_disc2-v2.tar.gz -C extracted/eval_disc2-v2
python analysis/compare_eval.py eval_disc1-smooth eval_disc2-v2 eval_disc3-slots
```
