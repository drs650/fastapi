from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, players, matches, teams, stats

app = FastAPI(
    title="2026 FIFA 월드컵 데이터 API",
    description="PostgreSQL에 저장된 선수/경기/팀 데이터를 FastAPI로 조회·수정하는 실습 프로젝트",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {
        "message": "2026 FIFA 월드컵 데이터 API",
        "docs": "/docs",
        "endpoints": ["/players", "/matches", "/teams", "/stats/top-scorers", "/stats/team-goal-diff"],
    }


# 422 에러가 나면 어떤 필드가 문제인지 바로 보이도록 에러 메시지를 조금 더 친절하게 가공
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(x) for x in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "입력값을 확인해주세요", "errors": errors})
