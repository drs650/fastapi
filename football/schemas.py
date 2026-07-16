# ======================================================================
# football/schemas.py
#
# "API응답으로 어떤 모양의 JSON을 내보낼지"를 정의하는 파일
#
# models.py의 SQLAlchemy 모델은 DB 테이블 구조를 표현한다.
# schemas.py의 Pydnatic 모델은 클라이언트에게 보여줄 응답 구조를 표현한다.
#
# 같은 player라는 이름을 쓰더라도 역할이 다르다
# - models.Player : DB의 player 테이블과 매핑되는 ORM 클래스
# - schemas.Player : API 응답 JSON 모양을 검증 / 직렬화 하는 Pydantic 클래스
#
# ======================================================================
from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import date

# API 응답으로 내보낼 선수 성적 데이터 모양
class Performance(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    performance_id : int
    player_id : int
    week_number : str
    fantasy_points : float
    last_changed_date : date

# 선수 기본 정보 - 다른 응답 모델에서도 재사용하기 위해 Base 클래스로 분리
class PlayerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id : int
    gsis_id : str | None
    first_name : str
    last_name : str
    position : str
    last_changed_date : date

class Player(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    performances : List[Performance] = Field(default_factory=list)

# 팀 기본 정보 - 리그 응답 안에 팀 목록을 넣을 때도 이 모델을 재사용
class TeamBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id : int
    team_id : int
    team_name : str
    last_changed_date : date

# 팀 상세 응답 - 팀 기본 정보에 선수 목록을 함께 포함한다.
class Team(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    players : List[PlayerBase] = Field(default_factory=list)

# 리그 응답 - 리그 기본 정보와 소속 팀 목록을 함께 반환
class League(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id : int
    league_name : str
    scoring_type : str
    last_changed_date : date

    # 리그 응답에는 소속 팀 목록을 함께 담는다.
    # main.py /v0/leagues/{league_id} 응답에서 이 관계가 사용된다.
    teams : List[TeamBase] = Field(default_factory=list)

# 카운트 API 응답 전용 모델 - 테이블별 전체 개수를 담는다.
class Counts(BaseModel):
    league_count : int
    team_count : int
    player_count : int