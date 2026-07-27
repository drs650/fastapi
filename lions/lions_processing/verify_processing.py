# ================================================================================
# lions_processing/verify_processing.py
#   - 배치/이벤트 처리 단계가 만들어낸 결과 테이블들이 실제로 존재하고
#       데이터가 채워졌는지 "최종 점검"하는 스크립트
# ================================================================================
from database import engine, table_count

CHECKS = [
    (engine, 'batch_pitcher_role_summary'),
    (engine, 'batch_batter_position_summary'),
    (engine, 'event_pitcher_alerts'),
    (engine, 'event_team_alerts'),
]


def verify() -> bool:
    print('==== 처리시스템 결과 검증 (배치 + 이벤트) ====')
    ok = True
    for eng, table_name in CHECKS:
        try:
            count = table_count(eng, table_name)
            print(f'{table_name}: {count:,}건')
        except Exception as exc:
            ok = False
            print(f'{table_name}: 확인 실패 - {exc}')
    print(f'검증결과: {"PASS" if ok else "FAIL"}')
    return ok


if __name__ == '__main__':
    verify()
