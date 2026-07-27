# ==================================================================
# lions_stats/verify.py
#
#   적재 검증
#     - 원본 대비 완전성 (원본 행수 = DB 행수)
#     - NOT NULL 필수 컬럼 결측 여부
#     - 이상치 (승률/AVG 등 비율 범위, 이닝수 음수 등)
#     - pitchers (name, age) / batters (name) 중복 여부
# ==================================================================

import os
import pandas as pd
from sqlalchemy import text
from database import engine

BASE_DIR = os.getcwd()
INPUT_DIR = os.path.join(BASE_DIR, 'input')


def _raw_count(filename: str) -> int:
    return len(pd.read_csv(os.path.join(INPUT_DIR, filename), encoding='utf-8-sig'))


def verify():
    raw_counts = {
        'pitchers': _raw_count('pitchers.csv'),
        'batters': _raw_count('batters.csv'),
        'team_matchups': _raw_count('team_matchups.csv'),
    }

    with engine.connect() as conn:
        db_counts = {
            'pitchers': conn.execute(text('SELECT COUNT(*) FROM pitchers')).scalar(),
            'batters': conn.execute(text('SELECT COUNT(*) FROM batters')).scalar(),
            'team_matchups': conn.execute(text('SELECT COUNT(*) FROM team_matchups')).scalar(),
        }

        null_name_age = conn.execute(text(
            'SELECT COUNT(*) FROM pitchers WHERE name IS NULL OR age IS NULL'
        )).scalar()
        dup_pitcher = conn.execute(text('''
            SELECT COUNT(*) FROM (
                SELECT name, age, COUNT(*) FROM pitchers
                GROUP BY name, age HAVING COUNT(*) > 1
            ) t
        ''')).scalar()
        dup_batter = conn.execute(text('''
            SELECT COUNT(*) FROM (
                SELECT name, COUNT(*) FROM batters
                GROUP BY name HAVING COUNT(*) > 1
            ) t
        ''')).scalar()

        negative_innings = conn.execute(text(
            'SELECT COUNT(*) FROM pitchers WHERE innings_thirds < 0'
        )).scalar()
        invalid_win_pct = conn.execute(text(
            'SELECT COUNT(*) FROM team_matchups WHERE win_pct NOT BETWEEN 0 AND 1'
        )).scalar()
        invalid_record_sum = conn.execute(text(
            'SELECT COUNT(*) FROM team_matchups WHERE wins + losses + draws <> games'
        )).scalar()

    print('==== 라이온즈 스탯 적재 검증 결과 ====')
    for table in raw_counts:
        match = '일치' if raw_counts[table] == db_counts[table] else '불일치'
        print(f'{table} : 원본 {raw_counts[table]}건 / DB {db_counts[table]}건 ({match})')
    print(f'pitchers name/age 결측 : {null_name_age}')
    print(f'pitchers (name,age) 중복키 : {dup_pitcher}')
    print(f'batters name 중복키 : {dup_batter}')
    print(f'이닝 음수 이상치 : {negative_innings}')
    print(f'승률 범위(0~1) 이탈 : {invalid_win_pct}')
    print(f'전적 합계(승+패+무=경기) 불일치 : {invalid_record_sum}')

    ok = (
        all(raw_counts[t] == db_counts[t] for t in raw_counts)
        and null_name_age == 0
        and dup_pitcher == 0
        and dup_batter == 0
        and negative_innings == 0
        and invalid_win_pct == 0
        and invalid_record_sum == 0
    )
    print()
    print(f'검증 결과 : {"PASS" if ok else "FAIL"}')
    return ok


if __name__ == '__main__':
    verify()
