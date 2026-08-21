# disc2-10act — Discrete action space 10개 (disc1에서 ±30°/1.6 제거)

| # | Steering (°) | Speed (m/s) |
|---|---|---|
| 0 | -20 | 1.6 |
| 1 | -20 | 2.1 |
| 2 | -10 | 1.9 |
| 3 | -10 | 2.6 |
| 4 | 0 | 2.2 |
| 5 | 0 | 3.0 |
| 6 | 10 | 1.9 |
| 7 | 10 | 2.6 |
| 8 | 20 | 1.6 |
| 9 | 20 | 2.1 |

콘솔: Discrete → Advanced configuration ON → 기본 10행을 위 표대로 덮어쓰기 (행 추가/삭제 불필요). 상단 granularity/max speed는 건드리지 않음.
나머지: A to Z Speedway CCW, Time trial, 하이퍼 128/0.01/0.995/huber/0.0003/25/10, Reward `reward_clone1.py`, 120분, eval 5.
