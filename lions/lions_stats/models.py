# ================================================
# lions_stats/models.py
#
# 저장 모델 설계
#   pitchers      : 투수 스탯 (보직: 선발/스윙/셋업, 이름은 자연키로 쓸 수 없음! 동명이인 존재)
#   batters       : 타자 스탯 (포지션별)
#   team_matchups : 팀별 상대전적 (상대팀명이 진짜 자연키)
# ================================================

from sqlalchemy import (
    Column, BigInteger, SmallInteger, String, Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Pitcher(Base):
    """투수 시즌 스탯 1행 = 투수 1명"""
    __tablename__ = 'pitchers'

    # 대체키(surrogate key): 이름은 자연키로 쓸 수 없다.
    #   원본 데이터에 '이승현'이 두 명(23세·좌완·선발 / 34세·우완·셋업) 존재하기 때문.
    #   대신 (name, age) 조합에 UNIQUE 제약을 걸어 같은 선수가 중복 적재되지 않게 한다.
    pitcher_id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(50), nullable=False)
    age = Column(SmallInteger, nullable=False)
    throws = Column(String(4), nullable=False)          # 투구: R / L / RS(우완 사이드암 추정)
    role = Column(String(10), nullable=True)             # 보직: 선발/스윙/셋업 (원본 '-'는 NULL로 저장)
    games = Column(SmallInteger, nullable=False)

    innings_display = Column(String(10), nullable=False)   # 원본 그대로 표시용 ('197.1')
    innings_thirds = Column(Numeric(6, 3), nullable=False)  # 계산용 실제값 (197 + 1/3 = 197.333)

    park_factor = Column(Numeric(6, 2), nullable=True)
    k9 = Column(Numeric(5, 2), nullable=True)
    bb9 = Column(Numeric(5, 2), nullable=True)
    k_bb = Column(Numeric(5, 2), nullable=True)          # BB=0이면 원본이 '-' -> NULL
    hr9 = Column(Numeric(5, 2), nullable=True)

    fip = Column(Numeric(5, 2), nullable=False)
    fip_minus = Column(SmallInteger, nullable=False)
    fwar = Column(Numeric(4, 1), nullable=True)           # 표본이 매우 작으면 원본이 '-'

    era = Column(Numeric(5, 2), nullable=False)
    era_minus = Column(SmallInteger, nullable=False)
    ra9 = Column(Numeric(5, 2), nullable=False)
    ra9_minus = Column(SmallInteger, nullable=False)
    rwar = Column(Numeric(4, 1), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'age', name='uq_pitchers_name_age'),
    )

    def __repr__(self):
        return f'<Pitcher {self.name}({self.age}) {self.role}>'


class Batter(Base):
    """타자 시즌 스탯 1행 = 타자 1명"""
    __tablename__ = 'batters'

    # 이번 시즌 데이터에는 이름 중복이 없었지만(검증 완료), 다음 시즌 데이터를 더할 때도
    # 안전하도록 pitchers와 동일하게 대체키 + UNIQUE(name) 방식을 쓴다.
    batter_id = Column(BigInteger, primary_key=True, autoincrement=True)

    position = Column(String(10), nullable=False)         # 포지션 (1루수, 유격수 등)
    name = Column(String(50), nullable=False)
    age = Column(SmallInteger, nullable=False)
    games = Column(SmallInteger, nullable=False)
    plate_appearances = Column(SmallInteger, nullable=False)

    park_factor = Column(Numeric(6, 2), nullable=True)
    war = Column(Numeric(4, 1), nullable=False)
    wpa = Column(Numeric(6, 2), nullable=True)
    wrc_plus = Column(SmallInteger, nullable=True)         # 타석 0인 선수는 원본이 '-'
    woba = Column(Numeric(5, 3), nullable=True)
    obp = Column(Numeric(5, 3), nullable=True)
    slg = Column(Numeric(5, 3), nullable=True)
    ops = Column(Numeric(5, 3), nullable=True)
    avg = Column(Numeric(5, 3), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', name='uq_batters_name'),
    )

    def __repr__(self):
        return f'<Batter {self.name} {self.position}>'


class TeamMatchup(Base):
    """팀별(상대팀 기준) 통산 상대전적 1행 = 상대팀 1개"""
    __tablename__ = 'team_matchups'

    # 자연키(natural key): 상대팀명은 KBO 8개 구단으로 고정되어 있고 중복될 수 없다.
    opponent = Column(String(10), primary_key=True)

    # 원본의 '전적 (경기-승-패-무)' 문자열 "186-101-80-5"를 4개 숫자 컬럼으로 분해
    games = Column(SmallInteger, nullable=False)
    wins = Column(SmallInteger, nullable=False)
    losses = Column(SmallInteger, nullable=False)
    draws = Column(SmallInteger, nullable=False)

    win_pct = Column(Numeric(4, 3), nullable=False)         # 실제 승률
    pythag_win_pct = Column(Numeric(4, 3), nullable=False)  # 득실점 기반 피타고리안 승률
    win_pct_diff = Column(Numeric(5, 3), nullable=False)    # 실제승률 - 피타고리안승률
    diff_interpretation = Column(String(50), nullable=True)  # 원본 사이트의 해석 문구

    runs_scored = Column(SmallInteger, nullable=False)
    runs_allowed = Column(SmallInteger, nullable=False)
    runs_scored_per_g = Column(Numeric(4, 2), nullable=False)
    runs_allowed_per_g = Column(Numeric(4, 2), nullable=False)

    def __repr__(self):
        return f'<TeamMatchup vs {self.opponent}>'
