# 삼성 라이온즈 2025 스탯 처리시스템

저장시스템(lions_stats)에서 만든 `pitchers`/`batters`/`team_matchups`를 입력으로,
배치 집계와 이벤트 탐지를 수행한다. Steam 프로젝트 처리시스템(09_processing_system)과 동일한 구조.

| 파일 | 설명 |
|---|---|
| `config.py` | DB 접속정보 + 이벤트 임계값 |
| `database.py` | engine 생성 + 공통 SQL 유틸(execute_sql, table_count, check_required_tables) |
| `batch_processor.py` | 투수 보직별 / 타자 포지션별 집계 |
| `event_processor.py` | ERA-FIP 격차 투수, 승률-피타고리안 이변 팀 탐지 |
| `pipeline.py` | 배치 -> 이벤트 통합 실행 |
| `verify_processing.py` | 결과 테이블 검증 |

---

## 전제 조건

저장시스템(lions_stats) 실습이 완료되어 있어야 한다.

| DB | 테이블 |
| --- | --- |
| `lionsdb` | `pitchers`, `batters`, `team_matchups` |

## 처리 로직

### 배치 처리
- `batch_pitcher_role_summary` — 투수를 **보직(role: 선발/스윙/셋업/미분류)** 기준으로 그룹핑해서 인원수·총 이닝(야구식 표기 보정된 `innings_thirds` 합)·평균 ERA/FIP/rWAR/fWAR 집계
- `batch_batter_position_summary` — 타자를 **포지션** 기준으로 그룹핑해서 인원수·평균 WAR/OPS/wRC+ 집계

### 이벤트 처리
- `event_pitcher_alerts` — **PITCHER_ERA_FIP_GAP**: `|ERA - FIP| > 1.00`인 투수 (표본이 너무 작은 투수는 `innings_thirds >= 10` 조건으로 제외). ERA(결과)가 FIP(수비 무관 실력)보다 한참 나쁘면 수비 도움을 못 받은 것이고, 한참 좋으면 운이 따른 것으로 해석할 수 있다.
- `event_team_alerts` — **TEAM_WIN_PCT_SURPRISE**: `|실제승률 - 피타고리안승률| > 0.03`인 상대팀. 득실점으로 예상되는 승률보다 실제 성적이 많이 벗어난 상대를 표시한다.

두 이벤트 모두 재실행 시 `DELETE FROM ... WHERE event_type=...` 후 재삽입하는 방식으로 멱등성을 보장한다.

## 실행

```bash
pip install sqlalchemy "psycopg[binary]"
python pipeline.py
python verify_processing.py
```

임계값을 바꿔서 재탐지하려면:

```bash
python event_processor.py --era-fip-threshold 1.5 --win-pct-threshold 0.05
```

## 확인 SQL

```sql
SELECT * FROM batch_pitcher_role_summary ORDER BY total_innings DESC;
SELECT * FROM batch_batter_position_summary ORDER BY avg_war DESC;
SELECT * FROM event_pitcher_alerts ORDER BY gap_value DESC;
SELECT * FROM event_team_alerts ORDER BY gap_value DESC;
```
