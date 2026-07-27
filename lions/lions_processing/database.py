# ===============================================================================
# lions_processing/database.py
#   - DB 연결(Engine) 생성과 여러 모듈에서 공통으로 사용하는 DB 유틸리티 함수를 정의
# ===============================================================================
from sqlalchemy import create_engine, text

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)


def table_count(engine, table_name: str) -> int:
    """주어진 테이블의 전체 행(row) 개수를 반환"""
    with engine.connect() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar_one()


def check_required_tables() -> None:
    """
    배치/이벤트 처리 시작 전에, 저장시스템(lions_stats)에서 만든 원본 테이블이
    실제로 존재하고 데이터가 들어있는지 점검한다. (Fail Fast)
    """
    checks = [
        (engine, 'pitchers', '저장시스템(lions_stats) 실습 결과가 필요합니다.'),
        (engine, 'batters', '저장시스템(lions_stats) 실습 결과가 필요합니다.'),
        (engine, 'team_matchups', '저장시스템(lions_stats) 실습 결과가 필요합니다.'),
    ]
    for eng, table_name, hint in checks:
        try:
            count = table_count(eng, table_name)
        except Exception as exc:
            raise RuntimeError(f'{table_name} 테이블을 확인할 수 없습니다. {hint} 원인: {exc}') from exc
        if count == 0:
            raise RuntimeError(f'{table_name} 테이블은 존재하지만 데이터가 없습니다. 저장시스템 적재를 먼저 확인하세요.')


def execute_sql(engine, sql: str, params: dict | None = None) -> None:
    """
    여러 문장으로 이루어진 SQL 스크립트(세미콜론으로 구분)를 한번에 실행한다.
    engine.begin() 트랜잭션 안에서 실행되어, 정상 종료 시 자동 COMMIT, 예외 시 자동 ROLLBACK.
    """
    with engine.begin() as conn:
        statements = [statement.strip() for statement in sql.split(';') if statement.strip()]
        for statement in statements:
            conn.execute(text(statement), params or {})
