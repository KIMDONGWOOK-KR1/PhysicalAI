# Import → Clone 매뉴얼 (test1-1 → test1-1-smooth)

## 0. 준비물
- 업로드 폴더: `C:\PhysicalAI\import_test1-1\` (tar.gz 압축 해제 + logs/metrics/sim-trace 제거본, ~280MB)
  - 필수 구성: `model/`(ckpt·pb·deepracer_checkpoints.json·model_metadata.json), `model_metadata.json`, `reward_function.py`, `ip/hyperparameters.json`
- 보상함수: `C:\PhysicalAI\reward_clone1.py`

## 1. S3 업로드
1. AWS 콘솔 → S3 → DeepRacer가 쓰는 버킷 열기
   (이름에 `deepracer` 포함. 모르면 DeepRacer 콘솔의 기존 모델 상세/Settings에서 버킷명 확인)
2. 폴더 생성: `imports/test1-1/`
3. 그 안에 `import_test1-1` 폴더의 **내용물**을 폴더 구조 그대로 업로드
   (드래그 시 `import_test1-1` 폴더 자체가 아니라 안의 `model/`, `ip/`, 파일들을 올릴 것)
4. 업로드 후 확인: `s3://<버킷>/imports/test1-1/model/45_Step-74327.ckpt.index` 가 보여야 함
   - tar.gz를 그대로 올리면 안 됨. **반드시 압축 해제된 폴더**
   - 숨김파일 `model/.coach_checkpoint`, `model/.ready`가 빠질 수 있음 → 탐색기에서 숨김파일 표시 켜고 확인. 빠졌으면 따로 업로드

## 2. Import model
1. DeepRacer 콘솔 → Your models → **Import model**
2. Model name: `test1-1-import`
3. S3 location: `s3://<버킷>/imports/test1-1/` (model/ 의 **상위** 폴더)
4. Import → 상태가 Ready 될 때까지 대기 (수 분)
5. 모델 상세에서 확인: Action space **continuous, speed 1.1~3, steer ±30** / Reward function이 `(progress/steps)*100 + speed**2` 형태
   → 다르면 잘못 올라간 것. 경로 재확인

## 3. Clone
1. `test1-1-import` 선택 → **Clone**
2. Model name: `test1-1-smooth`
3. Environment: A to Z Speedway, 방향 **Counterclockwise(Reverse OFF)**
4. Race type: Time trial
5. Training algorithm: PPO — 하이퍼파라미터 **확인만** (아래와 일치해야 함, 수정 금지)
   ```
   Batch size 128 / Entropy 0.01 / Discount 0.995 / Exploration categorical
   Loss huber / LR 0.0003 / Episodes per iteration 25 / Epochs 10
   ```
6. Action space: clone이라 수정 불가 또는 그대로 — **1.1~3.0, ±30 유지**
7. Reward function: 기존 내용 전부 삭제 → `reward_clone1.py` 내용 붙여넣기 → **Validate** 클릭 (통과해야 함)
8. Stop conditions: Maximum time **90분**
9. Evaluation(있으면): Min eval trials 5
10. **Create model**

## 4. 학습 중 모니터링
| 시점 | 정상 | 이상 → 조치 |
|---|---|---|
| 0~10분 | reward가 원본보다 낮게 시작 (배율 페널티 때문) | — |
| 30분 | completion 50%+ 유지, reward 상승 | completion 20% 이하 30분 지속 → Stop. 페널티 완화 버전으로 재clone |
| 60~90분 | completion 70%+, eval 4~5/5 | 상승 후 급락 → 직전 체크포인트 |

## 5. 완료 후
1. Evaluate 5회 → 기록: **완주 횟수** / 최단 랩 / 최장 랩
2. Download logs → `C:\PhysicalAI\`에 저장 → `analyze_trace2.py`로 bang-bang 감소 확인
3. 결과 좋으면 다음 clone에서 속도 3.5 (이번엔 금지)
4. 실물용 export: Download physical model (test1-1-smooth)

## 트러블슈팅
- Import 실패 "model_metadata not found" → S3 경로가 `model/` 상위인지 확인
- Import 실패 "checkpoint" 관련 → `.coach_checkpoint` 누락. 내용은 텍스트 한 줄 `46_Step-76655.ckpt` (또는 `45_Step-74327.ckpt`로 바꿔도 됨)
- Validate 실패 → 붙여넣기 시 들여쓰기 깨짐. 파일을 메모장으로 열어 전체선택 복사
- `Endpoint request timed out` → 주최 측 서버 문제. 5분 후 재시도, 반복되면 주최 측 문의
