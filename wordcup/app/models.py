"""
players / matches / teams 테이블은 컬럼이 각각 72개, 45개, 136개나 돼서
SQLAlchemy 모델을 일일이 손으로 작성하는 대신 automap으로 기존 스키마를
그대로 리플렉션해서 씁니다. (schema.sql로 테이블을 먼저 만들어둔 상태여야 함)
"""
from sqlalchemy.ext.automap import automap_base
from app.database import engine

Base = automap_base()
Base.prepare(autoload_with=engine)

Player = Base.classes.players
Match = Base.classes.matches
Team = Base.classes.teams


def row_to_dict(row):
    """SQLAlchemy ORM 객체 -> dict (Pydantic 없이 바로 JSON 응답용)"""
    return {c.key: getattr(row, c.key) for c in row.__table__.columns}
