# ================================================================================
# lions_processing/event_processor.py
#   - "이벤트 처리(Event Processing / CEP)" 예제
#       원본 데이터를 대상으로 "이상 상황(조건을 만족하는 사건)"을
#       탐지하여 별도의 알림(alert) 테이블에 기록한다.
#
#   - 이벤트 규칙 2가지
#       1) PITCHER_ERA_FIP_GAP : ERA(결과)와 FIP(수비 무관 실력 지표)의 격차가 크면
#          "운이 좋았거나(피안타 불운) 나빴던(수비 도움 못 받은)" 투수로 판정
#       2) TEAM_WIN_PCT_SURPRISE : 실제 승률과 피타고리안 승률(득실점 기반 기대 승률)의
#          격차가 크면 "성과가 경기 내용과 어긋난(접전에 강하거나 약한)" 상대팀으로 판정
#
#   - 표본이 매우 작은 투수(몇 이닝만 던진 경우)는 ERA/FIP가 극단적으로 튀기 때문에
#     MIN_INNINGS_THIRDS 미만은 이벤트 탐지 대상에서 제외한다.
# ================================================================================
import argparse
from datetime import datetime

from config import ERA_FIP_GAP_THRESHOLD, MIN_INNINGS_THIRDS, WIN_PCT_GAP_THRESHOLD
from database import engine, check_required_tables, execute_sql


def init_alert_tables() -> None:
    """이벤트 알림을 저장할 테이블 2개를 준비(없으면 생성)"""
    execute_sql(
        engine,
        """
        CREATE TABLE IF NOT EXISTS event_pitcher_alerts (
            id BIGSERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            pitcher_name VARCHAR(50) NOT NULL,
            age SMALLINT NOT NULL,
            role VARCHAR(10),
            era NUMERIC(5, 2) NOT NULL,
            fip NUMERIC(5, 2) NOT NULL,
            gap_value NUMERIC(5, 2) NOT NULL,
            threshold_value NUMERIC(5, 2) NOT NULL,
            detected_at TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS event_team_alerts (
            id BIGSERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            opponent VARCHAR(10) NOT NULL,
            win_pct NUMERIC(4, 3) NOT NULL,
            pythag_win_pct NUMERIC(4, 3) NOT NULL,
            gap_value NUMERIC(5, 3) NOT NULL,
            threshold_value NUMERIC(5, 3) NOT NULL,
            detected_at TIMESTAMP NOT NULL
        );
        """
    )


def detect_pitcher_era_fip_gap(threshold: float, min_innings: float) -> None:
    """
    |ERA - FIP| 가 threshold를 초과하는 투수를 찾아 이벤트로 등록한다.
    (재실행해도 중복이 쌓이지 않도록 같은 event_type을 먼저 지운다 - 멱등성)
    """
    execute_sql(
        engine,
        """
        DELETE FROM event_pitcher_alerts
        WHERE event_type = 'PITCHER_ERA_FIP_GAP';
        """
    )
    execute_sql(
        engine,
        """
        INSERT INTO event_pitcher_alerts(
            event_type, pitcher_name, age, role, era, fip,
            gap_value, threshold_value, detected_at
        )
        SELECT
            'PITCHER_ERA_FIP_GAP', name, age, role, era, fip,
            ROUND(ABS(era - fip)::numeric, 2),
            :threshold,
            :detected_at
        FROM pitchers
        WHERE innings_thirds >= :min_innings
          AND ABS(era - fip) > :threshold;
        """,
        {"threshold": threshold, "min_innings": min_innings, "detected_at": datetime.now()}
    )
    print(f'[event] 투수 ERA-FIP 격차 이벤트 탐지 완료 threshold={threshold}, min_innings={min_innings}')


def detect_team_win_pct_surprise(threshold: float) -> None:
    """
    |실제승률 - 피타고리안승률| 이 threshold를 초과하는 상대팀을 찾아 이벤트로 등록한다.
    """
    execute_sql(
        engine,
        """
        DELETE FROM event_team_alerts
        WHERE event_type = 'TEAM_WIN_PCT_SURPRISE';
        """
    )
    execute_sql(
        engine,
        """
        INSERT INTO event_team_alerts(
            event_type, opponent, win_pct, pythag_win_pct,
            gap_value, threshold_value, detected_at
        )
        SELECT
            'TEAM_WIN_PCT_SURPRISE', opponent, win_pct, pythag_win_pct,
            ROUND(ABS(win_pct - pythag_win_pct)::numeric, 3),
            :threshold,
            :detected_at
        FROM team_matchups
        WHERE ABS(win_pct - pythag_win_pct) > :threshold;
        """,
        {"threshold": threshold, "detected_at": datetime.now()}
    )
    print(f'[event] 팀 승률-피타고리안 이변 이벤트 탐지 완료 threshold={threshold}')


def run_event_processing(
    era_fip_threshold: float = ERA_FIP_GAP_THRESHOLD,
    min_innings: float = MIN_INNINGS_THIRDS,
    win_pct_threshold: float = WIN_PCT_GAP_THRESHOLD,
) -> None:
    check_required_tables()
    init_alert_tables()
    detect_pitcher_era_fip_gap(era_fip_threshold, min_innings)
    detect_team_win_pct_surprise(win_pct_threshold)
    print('[event] 이벤트 처리 완료')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='라이온즈 스탯 이벤트 처리')
    parser.add_argument('--era-fip-threshold', type=float, default=ERA_FIP_GAP_THRESHOLD)
    parser.add_argument('--min-innings', type=float, default=MIN_INNINGS_THIRDS)
    parser.add_argument('--win-pct-threshold', type=float, default=WIN_PCT_GAP_THRESHOLD)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run_event_processing(
        era_fip_threshold=args.era_fip_threshold,
        min_innings=args.min_innings,
        win_pct_threshold=args.win_pct_threshold,
    )
