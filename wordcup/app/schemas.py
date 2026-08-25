"""
players 테이블은 컬럼이 72개나 되지만, 실습 편의를 위해
CRUD로 다루는 스키마는 자주 쓰는 핵심 필드만 추립니다.
(나머지 컬럼은 GET 응답에는 automap으로 전부 그대로 나갑니다)
"""
from typing import Optional
from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    player: str = Field(..., description="선수 이름")
    team: str = Field(..., description="소속 국가대표팀")
    team_country: Optional[str] = None
    position: str = Field(..., description="GK / DF / MF / FW")
    age: Optional[int] = None
    club: Optional[str] = None
    games: Optional[int] = 0
    goals: Optional[float] = 0
    assists: Optional[float] = 0


class PlayerUpdate(BaseModel):
    """
    PUT/PATCH용. 전체 필드를 Optional로 뒀다 — 이걸 안 하면
    수정하려는 필드 하나만 보내도 나머지가 required라서
    422 Unprocessable Entity가 계속 발생한다. (TROUBLESHOOTING.md 참고)
    """
    player: Optional[str] = None
    team: Optional[str] = None
    team_country: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    club: Optional[str] = None
    games: Optional[int] = None
    goals: Optional[float] = None
    assists: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
