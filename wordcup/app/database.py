"""
DB 연결 설정.
.env 파일 혹은 환경변수에서 DATABASE_URL을 읽어옵니다.
예: postgresql+psycopg2://user:password@localhost:5432/worldcup
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldcup",
)

# SQLite로 테스트할 때만 필요한 옵션 (Postgres에서는 무시됨)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI Depends()로 주입할 DB 세션"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
