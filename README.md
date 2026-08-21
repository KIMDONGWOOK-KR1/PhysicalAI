# AWS DeepRacer 자율주행 경진대회 — sim2real 강건성 중심의 모델 개발 기록

**경북대학교 × 전남대학교 Physical AI 경진대회 (2026-08-19 ~ 08-21, AWS DeepRacer 실물 차량 타임트라이얼)**

> **AWS DeepRacer**(1/18 스케일 자율주행 RC카 + 클라우드 강화학습 플랫폼)로 진행된 대회.
> 시뮬레이션에서 가장 빠른 모델이 아니라, **실제 차가 완주하는 모델**을 만드는 과정의 기록이다.
> 3일간 교육 → 보상함수 설계 → 로그 분석 → 연속/이산 행동공간 비교 → clone 기반 점진 개선 → 실물 검증을 거쳐
> **실물 트랙 9초대, throttle 68%로 대회 시점 1위 기록**을 낸 모델(`disc2-10act`)을 완성했다.

---

## 대회 개요

| 항목 | 내용 |
|---|---|
| 대회명 | 경북대학교 × 전남대학교 Physical AI 경진대회 |
| 플랫폼 | **AWS DeepRacer** — DeepRacer on AWS(클라우드 PPO 학습·가상 시뮬레이션) + DeepRacer 실물 차량 |
| 일정 | 2026-08-19(수) ~ 08-21(금), 2박 3일 합숙 |
| 트랙 | A to Z Speedway (내부명 `reInvent2019_wide`, 16.6 m, 폭 107 cm, 반시계) |
| 본선 형식 | **실물 차량 Time Trial** — 팀당 2회 주행, 최단 랩타임 채택. 탈선 시 이탈 지점 재시작 + **1초 페널티** |
| 팀 | 4명 |

### 3일 진행

| 일자 | 공식 프로그램 | 우리 팀이 한 일 |
|---|---|---|
| **8/19 (수)** | Physical AI·DeepRacer 기초 이론, 보상함수 구조, AWS 인프라 점검, 가상 시뮬레이터 학습 실습, 야간 1차 모델 학습 | 사전 계산한 최적 레이싱 라인·보상함수 3종 준비. 팀원이 baseline 모델(`test1-1`, `test1-2`) 학습 |
| **8/20 (목)** | 가상 레이싱 테스트, Advanced 보상함수(Waypoints·Steering angle), **Clone Training**으로 모델 고도화, 실물 차량 연동·트랙 주행 실습(물리 기기 테스트), 야간 최종 튜닝 | baseline 로그 분석 → **bang-bang 조향 발견** → 실물 실습에서 탈선으로 확인 → 이산 행동공간 + 평활화 보상으로 야간 3개 병렬 학습 → `disc2-10act` 실물 9초 |
| **8/21 (금)** | **본선** Time Trial, 랩타임 측정·순위 집계, 참가자 전략 리뷰, 시상식 | 도전자 2개(`disc2-v2`, `disc3-slots`) 새벽 평가·비교, 본선 throttle 전략 수립, 인터뷰 대본 준비 |

---

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 과제 | A to Z Speedway 실물 DeepRacer 차량 최단 랩타임 |
| 알고리즘 | PPO (AWS DeepRacer), 보상함수·행동공간 직접 설계 |
| 최종 모델 | `disc2-10act` — **이산 10행동**(조향 0/±10/±20°, 속도 1.6~3.0) + 조향 평활화 보상 |
| 핵심 지표 | 스텝당 조향 변화 **16.6° → 8°대** (시뮬 로그), 시뮬 5/5 완주 |
| 실물 결과 | **9초대 완주 (throttle 68%)**, 대회 당시 1위 |

---

## 문제: 시뮬에서 빠른 모델이 실물에서 계속 탈선했다

팀원이 먼저 학습시킨 모델(`test1-1`)은 시뮬에서 6.9초로 빨랐지만, 실물 트랙에서는 탈선이 잦았다.
평가 로그(`sim-trace`)를 분석하자 원인이 보였다.

- **Bang-bang 조향**: 매 스텝 조향이 ±30° 사이를 튐 (평균 16.6°/step), throttle도 1.1↔3.0 왕복
- 원인: 연속 행동공간 + `speed**2` 보상의 전형적 부작용. 시뮬에서는 문제없지만 **실물 서보/모터 지연에서는 치명적**
- 구간별 속도 차별화 없음 (직선에서도 평균 속도 2.0)

## 접근: "측정 가능한 지표로 결정한다"

1. **보상함수 재설계** ([`reward_functions/reward_clone1.py`](reward_functions/reward_clone1.py))
   - `progress/steps` — 랩타임과 직결되는 시간 압박 항 (없으면 "느리게 정확히" 가는 모델로 수렴)
   - 전방 6개 waypoint의 방향 변화로 **곡률 추정 → 목표 속도** (직선 3.0, 헤어핀 1.7)
   - **직전 스텝 대비 조향 변화량을 곱셈 배율로** 페널티 — 덧셈이면 다른 항만 챙기는 정책이 나오므로
   - 절대 좌표 미사용 (시뮬 좌표계가 사전 계산한 라인과 달랐던 경험 때문)
2. **행동공간을 연속 → 이산으로** — 지그재그를 구조적으로 차단
3. **한 번에 하나만 바꾸는 clone** — 매 단계 `compare_eval.py`로 조향 변화·풀조향 비율·구간 속도 수치 확인
4. **실물 주행 결과로 최종 결정** — 시뮬 랩타임이 0.7초 빠른 모델 대신 조향이 부드러운 모델 선택

## 결과: 모델 계보

| 모델 | 행동공간 | 보상 | 시뮬 (5회 평가) | 조향 변화/step | 실물 |
|---|---|---|---|---|---|
| test1-1 (팀원 원본) | 연속 ±30, 1.1~3.0 | `pace + speed²` | 3~5/5, 6.9~9.4 s | 16.6° | 탈선 잦음 |
| dev1 | 연속 ±25, 1.5~3.0 | `reward_D_segment` (좌표 미보정) | 5/5, 7.0~7.9 s | 11.1° | — |
| seg2-line | 연속 ±25, 1.5~3.0 | `reward_D2_segment` | 5/5, 7.7~10.1 s | 풀조향 58% | 제외 |
| disc1-smooth | 이산 12 | `reward_clone1` | 5/5, 7.9~8.5 s | 11.7° | 84% 완주, 느림 |
| **disc2-10act** ★ | **이산 10** (±30 제거) | `reward_clone1` | 5/5 | ~8° | **9초대 @68%** |
| disc2-v2 | 이산 10 | `reward_clone2` | 5/5, 7.6~8.4 s | 8.2° | — |
| disc3-slots | 이산 10 (+고속 슬롯) | `reward_clone1` | 5/5, 7.7~8.5 s | 8.5° | — |

## 배운 것

- **의도대로 학습되는지는 로그로 확인한다.** 좌표가 틀린 보상함수로 학습한 `dev1`이 오히려 완주했다. 파고들어 보니 라인 보상은 항상 0이었고 "트랙 위 = 양수 / 탈선 = 0.001" 구조가 생존 보상으로 작동한 것이었다.
- **시뮬 기록과 실물은 다르다.** 탈선 1회 = +1초 룰에서는 0.7초 빠른 것보다 완주 안정성이 먼저다.
- **속도 상한만 올리는 clone은 역효과.** 3.5 m/s 모델(`test1-2`)은 상한을 못 쓰고 더 느리게 수렴했다.
- **Clone은 출력층을 이어받아 이산 행동 개수를 바꿀 수 없다** → 중복 슬롯 값을 덮어써 우회.

---

## 저장소 구성

```
├── README.md                 ← 이 문서
├── docs/
│   ├── PROJECT_LOG.md        ← 3일간의 작업 일지 (분석·결정·실패 전부)
│   ├── ANALYSIS_test1.md     ← 팀원 원본 모델 로그 분석
│   ├── MANUAL_import_clone.md← DeepRacer on AWS Import/Clone 절차
│   ├── action_space_disc*.md ← 이산 행동공간 입력표
│   └── INTERVIEW_script.md   ← 수상 인터뷰 대본
├── reward_functions/         ← 보상함수 5종 (+ README)
├── analysis/                 ← 로그 분석 스크립트 (+ README)
├── data/                     ← 최적 레이싱 라인 CSV, 시뮬 waypoint
└── logs/                     ← 모델별 평가 로그 (sim-trace, 결과 재현용)
```

### 재현

```bash
pip install pandas numpy
mkdir -p extracted && for f in logs/*.tar.gz; do n=$(basename $f .tar.gz); mkdir -p extracted/$n && tar -xzf $f -C extracted/$n; done
python analysis/compare_eval.py eval_disc1-smooth eval_disc2-v2 eval_disc3-slots
```

## 환경

- **AWS DeepRacer**: DeepRacer on AWS (2025-12 콘솔 종료 후 계정 직접 배포 버전)에서 PPO 학습·가상 평가, 학습된 모델을 DeepRacer 실물 차량에 업로드해 주행
- 하이퍼파라미터: batch 128, lr 3e-4, entropy 0.01, discount 0.995, 25 episodes/iter, 10 epochs, Huber
- 분석: Python 3.10, pandas, numpy. 로그 수치 분석과 보상함수 검증에 Claude를 활용했고, 모델 선택과 변경 변수 결정은 실물 주행 결과를 보고 팀이 내렸다.

---

## English summary

Record of a 3-day **AWS DeepRacer** competition (Kyungpook National Univ. × Chonnam National Univ. Physical AI Challenge, Aug 19–21 2026): day 1 DeepRacer/RL training and first models, day 2 clone training and physical-car track practice, day 3 the final — a **physical-car** time trial on A to Z Speedway (16.6 m, CCW; best of 2 runs, +1 s per off-track).
A teammate's baseline was fast in simulation (6.9 s) but kept leaving the track on the real car. Log analysis showed **bang-bang steering** (16.6° change per step) caused by a continuous action space with a `speed²` reward.
We redesigned the reward (pace term, curvature-based target speed from forward waypoints, **multiplicative steering-smoothness penalty**, no absolute coordinates), switched to a **10-action discrete space**, and iterated by cloning with one variable changed at a time, measuring steering jump / full-steer ratio / per-segment speed from sim-trace logs after every step.
The final model `disc2-10act` cut steering change to ~8°/step, completed 5/5 evaluation laps, and ran **~9 s laps on the real track at 68% throttle — first place at the time of the run**.
