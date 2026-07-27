# ================================================
# lions_stats/loader.py
#
# hardhit.ai에서 내려받은 CSV 3개(투수/타자/상대전적)를
# pitchers / batters / team_matchups 테이블에 적재
#
# *** 원본 CSV 정제 포인트 ***
#   1) UTF-8 BOM 포함 -> encoding='utf-8-sig'로 읽어야 첫 컬럼명 앞에 잡글자가 안 붙는다
#   2) 헤더에 사이트 UI의 정렬 화살표가 섞여 있음 ('fWAR ↓', 'WAR ↓', '승률 ↓')
#       -> 컬럼명에서 ' ↓' 제거 후 DB 컬럼명으로 매핑
#   3) 표본이 작아 계산 불가능한 값은 '-' 문자열로 표시되어 있음 -> NaN(NULL)으로 치환
#   4) '이닝' 컬럼은 일반 소수가 아니라 야구식 표기 (.1 = 1아웃, .2 = 2아웃)
#       -> 계산용 정확한 실수값(innings_thirds)을 별도로 만든다
#   5) '전적' 컬럼은 "186-101-80-5"(경기-승-패-무) 문자열 하나에 값 4개가 뭉쳐있음
#       -> 4개의 숫자 컬럼으로 분해한다
#   6) 이름(name)은 자연키로 쓸 수 없다 (투수 테이블에 동명이인 '이승현' 존재)
#       -> (name, age) 조합에 UNIQUE 제약 + upsert
# ================================================

import os
import numpy as np
import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import engine
from models import Pitcher, Batter, TeamMatchup

BASE_DIR = os.getcwd()
INPUT_DIR = os.path.join(BASE_DIR, 'input')


def _clean_dash(series: pd.Series) -> pd.Series:
    """'-' 로 표시된 결측치를 NaN으로 바꾼다. (숫자 변환 전에 항상 먼저 호출)"""
    return series.replace('-', np.nan)


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(_clean_dash(series), errors='coerce')


def _parse_innings(text: str):
    """
    '197.1' -> (표시용 '197.1', 계산용 197.333...)
    야구 표기: 소수부 .1 = 1아웃(1/3이닝), .2 = 2아웃(2/3이닝), .0 = 0아웃
    """
    text = str(text)
    whole_str, _, frac_str = text.partition('.')
    whole = int(whole_str)
    outs = int(frac_str) if frac_str else 0  # 0, 1, 2 중 하나
    thirds = round(whole + outs / 3, 3)
    return text, thirds


def _parse_record(text: str):
    """'186-101-80-5' -> (games=186, wins=101, losses=80, draws=5)"""
    games, wins, losses, draws = (int(x) for x in str(text).split('-'))
    return games, wins, losses, draws


def _nan_to_none(records: list[dict]) -> list[dict]:
    """pandas가 만든 NaN을 psycopg가 이해하는 None(NULL)으로 바꾼다."""
    return [
        {k: (None if isinstance(v, float) and np.isnan(v) else v) for k, v in rec.items()}
        for rec in records
    ]


def _load_pitchers() -> int:
    df = pd.read_csv(os.path.join(INPUT_DIR, 'pitchers.csv'), encoding='utf-8-sig')
    df.columns = [c.replace(' \u2193', '').strip() for c in df.columns]  # 정렬 화살표 제거

    innings = df['이닝'].apply(_parse_innings)

    records = pd.DataFrame({
        'name': df['이름'],
        'age': df['나이'].astype(int),
        'throws': df['투구'],
        'role': _clean_dash(df['보직']),
        'games': df['경기'].astype(int),
        'innings_display': innings.apply(lambda t: t[0]),
        'innings_thirds': innings.apply(lambda t: t[1]),
        'park_factor': _to_numeric(df['파크팩터']),
        'k9': _to_numeric(df['K/9']),
        'bb9': _to_numeric(df['BB/9']),
        'k_bb': _to_numeric(df['K/BB']),
        'hr9': _to_numeric(df['HR/9']),
        'fip': _to_numeric(df['FIP']),
        'fip_minus': _to_numeric(df['FIP-']).astype('Int64'),
        'fwar': _to_numeric(df['fWAR']),
        'era': _to_numeric(df['ERA']),
        'era_minus': _to_numeric(df['ERA-']).astype('Int64'),
        'ra9': _to_numeric(df['RA9']),
        'ra9_minus': _to_numeric(df['RA9-']).astype('Int64'),
        'rwar': _to_numeric(df['rWAR']),
    }).to_dict(orient='records')
    records = _nan_to_none(records)

    stmt = pg_insert(Pitcher).values(records)
    update_cols = {c.name: getattr(stmt.excluded, c.name)
                   for c in Pitcher.__table__.columns if c.name != 'pitcher_id'}
    stmt = stmt.on_conflict_do_update(index_elements=['name', 'age'], set_=update_cols)
    with engine.begin() as conn:
        conn.execute(stmt)
    print(f'[loader] pitchers 적재 완료: {len(records)}건')
    return len(records)


def _load_batters() -> int:
    df = pd.read_csv(os.path.join(INPUT_DIR, 'batters.csv'), encoding='utf-8-sig')
    df.columns = [c.replace(' \u2193', '').strip() for c in df.columns]

    records = pd.DataFrame({
        'position': df['포지션'],
        'name': df['이름'],
        'age': df['나이'].astype(int),
        'games': df['경기'].astype(int),
        'plate_appearances': df['타석'].astype(int),
        'park_factor': _to_numeric(df['파크팩터']),
        'war': _to_numeric(df['WAR']),
        'wpa': _to_numeric(df['WPA']),
        'wrc_plus': _to_numeric(df['wRC+']).astype('Int64'),
        'woba': _to_numeric(df['wOBA']),
        'obp': _to_numeric(df['OBP']),
        'slg': _to_numeric(df['SLG']),
        'ops': _to_numeric(df['OPS']),
        'avg': _to_numeric(df['AVG']),
    }).to_dict(orient='records')
    records = _nan_to_none(records)

    stmt = pg_insert(Batter).values(records)
    update_cols = {c.name: getattr(stmt.excluded, c.name)
                   for c in Batter.__table__.columns if c.name != 'batter_id'}
    stmt = stmt.on_conflict_do_update(index_elements=['name'], set_=update_cols)
    with engine.begin() as conn:
        conn.execute(stmt)
    print(f'[loader] batters 적재 완료: {len(records)}건')
    return len(records)


def _load_team_matchups() -> int:
    df = pd.read_csv(os.path.join(INPUT_DIR, 'team_matchups.csv'), encoding='utf-8-sig')
    df.columns = [c.replace(' \u2193', '').strip() for c in df.columns]

    record_parts = df['전적 (경기-승-패-무)'].apply(_parse_record)

    records = pd.DataFrame({
        'opponent': df['상대팀'],
        'games': record_parts.apply(lambda t: t[0]),
        'wins': record_parts.apply(lambda t: t[1]),
        'losses': record_parts.apply(lambda t: t[2]),
        'draws': record_parts.apply(lambda t: t[3]),
        'win_pct': _to_numeric(df['승률']),
        'pythag_win_pct': _to_numeric(df['피타고리안승률']),
        'win_pct_diff': _to_numeric(df['Δ 승률-PW']),
        'diff_interpretation': df['승률-PW 해석'],
        'runs_scored': df['득점 합'].astype(int),
        'runs_allowed': df['실점 합'].astype(int),
        'runs_scored_per_g': _to_numeric(df['득점/G']),
        'runs_allowed_per_g': _to_numeric(df['실점/G']),
    }).to_dict(orient='records')
    records = _nan_to_none(records)

    stmt = pg_insert(TeamMatchup).values(records)
    update_cols = {c.name: getattr(stmt.excluded, c.name)
                   for c in TeamMatchup.__table__.columns if c.name != 'opponent'}
    stmt = stmt.on_conflict_do_update(index_elements=['opponent'], set_=update_cols)
    with engine.begin() as conn:
        conn.execute(stmt)
    print(f'[loader] team_matchups 적재 완료: {len(records)}건')
    return len(records)


def load_from_csv() -> dict:
    totals = {
        'pitchers': _load_pitchers(),
        'batters': _load_batters(),
        'team_matchups': _load_team_matchups(),
    }
    print(f'[loader] 전체 적재 완료 - {totals}')
    return totals


if __name__ == '__main__':
    load_from_csv()
