# disc1-smooth — Discrete action space 입력표

| # | Steering (°) | Speed (m/s) |
|---|---|---|
| 0 | -30 | 1.6 |
| 1 | -20 | 1.6 |
| 2 | -20 | 2.1 |
| 3 | -10 | 1.9 |
| 4 | -10 | 2.6 |
| 5 | 0 | 2.2 |
| 6 | 0 | 3.0 |
| 7 | 10 | 1.9 |
| 8 | 10 | 2.6 |
| 9 | 20 | 1.6 |
| 10 | 20 | 2.1 |
| 11 | 30 | 1.6 |

(12개. 표 순서는 무관 — 콘솔이 정렬함. DeepRacer는 왼쪽 조향이 +, 오른쪽이 −)

## 콘솔 입력
1. Action space type: **Discrete**
2. 자동 생성 옵션이 있으면: Maximum steering angle **30**, Steering granularity **7**, Maximum speed **3.0**, Speed granularity **2** → 14개 생성
3. **Advanced configuration / 개별 편집**에서 위 표대로 속도 수정, ±30°의 느린 쪽(또는 중복) 1개씩 삭제 → 12개
4. 개별 편집 불가 시 fallback: 자동 그리드 14개(속도 1.5 / 3.0) 그대로 진행

## 나머지 설정
- 모델명 `disc1-smooth`, A to Z Speedway **Counterclockwise**, Time trial
- 하이퍼파라미터: batch **128**, entropy 0.01, discount **0.995**, huber, lr 0.0003, episodes **25**, epochs 10 (굵은 것이 기본값과 다름)
- Reward: `reward_clone1.py` 그대로 → Validate
- Max time **120분**, Min eval trials 5
