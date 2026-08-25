import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/top-scorers")
def top_scorers(
    db: Session = Depends(get_db),
    min_minutes: int = Query(180, description="최소 출전 시간(분) 필터"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    pandas로 90분당 득점 상위 선수를 계산.
    단순 goals 정렬이 아니라 min_minutes 미만 선수는 걸러내서
    '몇 분 안 뛰고 한 골 넣은' 선수가 1위로 나오는 걸 방지.
    """
    df = pd.read_sql(
        "SELECT player, team, position, minutes, goals, assists FROM players",
        db.bind,
    )
    df = df[df["minutes"] >= min_minutes].copy()
    df["goals_per90"] = (df["goals"] / (df["minutes"] / 90)).round(2)
    df = df.sort_values("goals_per90", ascending=False).head(limit)
    return df.to_dict(orient="records")


@router.get("/team-goal-diff")
def team_goal_diff(db: Session = Depends(get_db)):
    """
    matches 테이블을 홈/원정 양쪽 관점으로 풀어서(pandas concat)
    팀별 득점/실점/득실차/승점을 집계.
    """
    df = pd.read_sql(
        "SELECT home_team, away_team, home_score, away_score FROM matches "
        "WHERE home_score IS NOT NULL AND away_score IS NOT NULL",
        db.bind,
    )

    home = df.rename(columns={
        "home_team": "team", "away_team": "opponent",
        "home_score": "goals_for", "away_score": "goals_against",
    })[["team", "opponent", "goals_for", "goals_against"]]

    away = df.rename(columns={
        "away_team": "team", "home_team": "opponent",
        "away_score": "goals_for", "home_score": "goals_against",
    })[["team", "opponent", "goals_for", "goals_against"]]

    long_df = pd.concat([home, away], ignore_index=True)

    def result_points(row):
        if row["goals_for"] > row["goals_against"]:
            return 3
        if row["goals_for"] == row["goals_against"]:
            return 1
        return 0

    long_df["points"] = long_df.apply(result_points, axis=1)

    summary = (
        long_df.groupby("team")
        .agg(
            played=("team", "count"),
            goals_for=("goals_for", "sum"),
            goals_against=("goals_against", "sum"),
            points=("points", "sum"),
        )
        .reset_index()
    )
    summary["goal_diff"] = summary["goals_for"] - summary["goals_against"]
    summary = summary.sort_values(["points", "goal_diff"], ascending=False)
    return summary.to_dict(orient="records")
