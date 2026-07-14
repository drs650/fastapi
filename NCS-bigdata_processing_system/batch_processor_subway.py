# ================================================================================
# NCS-bigdata_processing_system/batch_processor_subway.py
#   - "배치 처리(Batch Processing)" 단계 예제 실습
# ================================================================================
from database import bus_engine, subway_engine, check_required_tables, execute_sql

def create_subway_data() -> None:
    execute_sql(
        subway_engine,
        '''
        DROP TABLE IF EXISTS subway_summary;

        CREATE TABLE subway_summary AS
        SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'subway_raw';
        SELECT COUNT(*) AS total_rows FROM subway_raw;
        SELECT COUNT(DISTINCT "역번호") AS station_count FROM subway_raw;
        SELECT DISTINCT "승하차" AS ride_types FROM subway_raw;
        SELECT "승하차", COUNT(*) AS row_count FROM subway_raw GROUP BY "승하차";
        SELECT * FROM subway_raw ORDER BY "인원수" DESC LIMIT 10;
        SELECT MIN("날짜") AS min_date, MAX("날짜") AS max_date FROM subway_raw;
        SELECT COUNT(*) AS null_count FROM subway_raw WHERE "인원수" IS NULL;
        CREATE INDEX idx_subway_summary_req 
        ON subway_summary(requirement_no);
        '''
    )
    print('[batch] 지하철 집계 완료: subway_data')

def run_batch_processing() -> None:

    print('[batch] 필수 입력 테이블 확인')
    check_required_tables()
    create_subway_data()
    print('[batch] 배치 처리 완료')

if __name__ == '__main__':
    run_batch_processing() # 엔트리포인트 함수 호출
