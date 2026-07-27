# ========================================================
# lions_stats/database.py
#
# PostgreSQL 연결 및 세션 관리 (DB명 : lionsdb)
# ========================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DB_URL = 'postgresql+psycopg://postgres:1234@localhost:5432/lionsdb'

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db(drop_existing: bool = True):
    """
    pitchers / batters / team_matchups 테이블을 초기화(준비)하는 함수

    drop_existing=True(기본값) : 기존 테이블을 지우고 새로 만든다 (완전 재설계)
    drop_existing=False        : 기존 테이블이 있으면 그대로 두고, 없을 때만 만든다
    """
    if drop_existing:
        Base.metadata.drop_all(bind=engine)
        print('[database] 기존 테이블 삭제(재설계를 위해)')

    Base.metadata.create_all(bind=engine)
    print('[database] pitchers / batters / team_matchups 준비 완료')


def get_session():
    return SessionLocal()
