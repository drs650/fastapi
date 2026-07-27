# ================================================================================
# lions_processing/batch_processor.py
#   - "배치 처리(Batch Processing)" 단계
#   - 저장시스템에 이미 적재되어 있는 원본 테이블(pitchers, batters) 전체를
#          한 번에 읽어서, 집계 결과 테이블을 새로 만든다.
# ================================================================================
from database import engine, check_required_tables, execute_sql


def create_pitcher_role_summary() -> None:
    """
    투수 원본 데이터를 "보직(role)" 기준으로 그룹핑하여
    보직별 투수 수 / 총 이닝 / 평균 ERA·FIP·rWAR·fWAR을 집계한다.

    COALESCE(role, '미분류') : 원본에서 '-'였던(=NULL) 값을 '미분류'라는 그룹으로 묶는다.
    SUM(innings_thirds) : 이닝의 야구식 표기(.1=1아웃)를 이미 보정해 둔 컬럼이므로
                          그냥 SUM해도 정확한 총 이닝이 나온다.
    """
    execute_sql(
        engine,
        '''
        DROP TABLE IF EXISTS batch_pitcher_role_summary;

        CREATE TABLE batch_pitcher_role_summary AS
        SELECT
            COALESCE(role, '미분류') AS role,
            COUNT(*) AS pitcher_count,
            ROUND(SUM(innings_thirds)::numeric, 1) AS total_innings,
            ROUND(AVG(era)::numeric, 2) AS avg_era,
            ROUND(AVG(fip)::numeric, 2) AS avg_fip,
            ROUND(AVG(rwar)::numeric, 2) AS avg_rwar,
            ROUND(AVG(fwar)::numeric, 2) AS avg_fwar
        FROM pitchers
        GROUP BY COALESCE(role, '미분류');

        CREATE INDEX idx_batch_pitcher_role_summary_innings
        ON batch_pitcher_role_summary(total_innings DESC);
        '''
    )
    print('[batch] 투수 보직별 집계 완료: batch_pitcher_role_summary')


def create_batter_position_summary() -> None:
    """
    타자 원본 데이터를 "포지션(position)" 기준으로 그룹핑하여
    포지션별 타자 수 / 평균 WAR·OPS·wRC+를 집계한다.
    """
    execute_sql(
        engine,
        '''
        DROP TABLE IF EXISTS batch_batter_position_summary;

        CREATE TABLE batch_batter_position_summary AS
        SELECT
            position,
            COUNT(*) AS batter_count,
            ROUND(AVG(war)::numeric, 2) AS avg_war,
            ROUND(AVG(ops)::numeric, 3) AS avg_ops,
            ROUND(AVG(wrc_plus)::numeric, 1) AS avg_wrc_plus
        FROM batters
        GROUP BY position;

        CREATE INDEX idx_batch_batter_position_summary_war
        ON batch_batter_position_summary(avg_war DESC);
        '''
    )
    print('[batch] 타자 포지션별 집계 완료: batch_batter_position_summary')


def run_batch_processing() -> None:
    print('[batch] 필수 입력 테이블 확인')
    check_required_tables()
    create_pitcher_role_summary()
    create_batter_position_summary()
    print('[batch] 배치 처리 완료')


if __name__ == '__main__':
    run_batch_processing()
