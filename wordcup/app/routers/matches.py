from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, row_to_dict

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("")
def list_matches(
    db: Session = Depends(get_db),
    team: Optional[str] = Query(None, description="홈팀 또는 원정팀으로 필터 (예: 대한민국)"),
    round: Optional[str] = Query(None, description="라운드 필터 (예: 조별리그, 8강, 결승)"),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD 이후 (KST 기준)"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD 이전 (KST 기준)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Match)

    if team:
        query = query.filter((Match.home_team == team) | (Match.away_team == team))
    if round:
        query = query.filter(Match.round == round)
    if date_from:
        query = query.filter(Match.date >= date_from)
    if date_to:
        query = query.filter(Match.date <= date_to)

    total = query.count()
    query = query.order_by(Match.date.asc(), Match.start_time.asc())
    rows = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [row_to_dict(r) for r in rows],
    }


@router.get("/{match_id}")
def get_match(match_id: int, db: Session = Depends(get_db)):
    row = db.query(Match).filter(Match.matches_id == match_id).first()
    if not row:
        raise HTTPException(404, "해당 경기를 찾을 수 없습니다")
    return row_to_dict(row)
