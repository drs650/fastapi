from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Player, row_to_dict
from app.schemas import PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/players", tags=["players"])

# 정렬 허용 컬럼 화이트리스트 (아무 문자열이나 order_by에 꽂으면 SQL 인젝션 위험이 있어서 제한)
SORTABLE_COLUMNS = {"goals", "assists", "age", "games", "minutes", "player"}


@router.get("")
def list_players(
    db: Session = Depends(get_db),
    team: Optional[str] = Query(None, description="국가대표팀 이름으로 필터 (예: 대한민국)"),
    position: Optional[str] = Query(None, description="포지션 필터 (GK/DF/MF/FW)"),
    search: Optional[str] = Query(None, description="선수 이름 부분 검색"),
    min_goals: Optional[float] = Query(None, description="이 값 이상 득점한 선수만"),
    sort_by: str = Query("goals", description=f"정렬 기준: {sorted(SORTABLE_COLUMNS)}"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Player)

    if team:
        query = query.filter(Player.team == team)
    if position:
        query = query.filter(Player.position == position)
    if search:
        query = query.filter(Player.player.ilike(f"%{search}%"))
    if min_goals is not None:
        query = query.filter(Player.goals >= min_goals)

    total = query.count()

    if sort_by not in SORTABLE_COLUMNS:
        raise HTTPException(400, f"sort_by는 {sorted(SORTABLE_COLUMNS)} 중 하나여야 합니다")
    sort_col = getattr(Player, sort_by)
    query = query.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    rows = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [row_to_dict(r) for r in rows],
    }


@router.get("/{player_id}")
def get_player(player_id: int, db: Session = Depends(get_db)):
    row = db.query(Player).filter(Player.players_id == player_id).first()
    if not row:
        raise HTTPException(404, "해당 선수를 찾을 수 없습니다")
    return row_to_dict(row)


@router.post("", status_code=201)
def create_player(
    payload: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    new_player = Player(**payload.model_dump())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return row_to_dict(new_player)


@router.put("/{player_id}")
def update_player(
    player_id: int,
    payload: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    row = db.query(Player).filter(Player.players_id == player_id).first()
    if not row:
        raise HTTPException(404, "해당 선수를 찾을 수 없습니다")

    update_data = payload.model_dump(exclude_unset=True)  # 보낸 필드만 반영
    for key, value in update_data.items():
        setattr(row, key, value)

    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/{player_id}", status_code=204)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    row = db.query(Player).filter(Player.players_id == player_id).first()
    if not row:
        raise HTTPException(404, "해당 선수를 찾을 수 없습니다")
    db.delete(row)
    db.commit()
    return None
