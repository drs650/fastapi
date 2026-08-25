from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Team, row_to_dict

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def list_teams(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="팀 이름 부분 검색"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Team)
    if search:
        query = query.filter(Team.team.ilike(f"%{search}%"))
    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [row_to_dict(r) for r in rows],
    }


@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    row = db.query(Team).filter(Team.teams_id == team_id).first()
    if not row:
        raise HTTPException(404, "해당 팀을 찾을 수 없습니다")
    return row_to_dict(row)
