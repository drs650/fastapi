# 2026 FIFA 월드컵 데이터 API

**사용 데이터셋:** FBref 스타일 2026 FIFA 월드컵(북중미) 선수·경기·팀 기록(players/matches/teams, 총 3개 테이블).
**선정 사유:** 팀에서 직접 전처리(인코딩 정리, 한국어 변환, KST 시간대 변환)까지 마친 정제 데이터가 있어 그대로 활용.

PostgreSQL에 저장된 데이터를 FastAPI로 조회·수정하는 실습 프로젝트입니다.

---

## 1. 프로젝트 구조

```
worldcup-api/
├── app/
│   ├── main.py          # FastAPI 앱 진입점
│   ├── database.py       # DB 커넥션 (환경변수로 DATABASE_URL 주입)
│   ├── models.py          # SQLAlchemy automap (테이블 컬럼이 많아 자동 리플렉션 사용)
│   ├── schemas.py         # 쓰기(POST/PUT)용 Pydantic 스키마
│   ├── auth.py            # 간단한 JWT 인증
│   └── routers/
│       ├── auth.py        # POST /auth/login
│       ├── players.py     # /players CRUD
│       ├── matches.py     # /matches 조회
│       ├── teams.py       # /teams 조회
│       └── stats.py       # pandas 기반 통계 API
├── scripts/
│   └── load_data.py       # schema.sql 실행 + CSV 적재
├── data/                  # players.csv, matches.csv, teams.csv
├── schema.sql             # 테이블 정의 (한국어 컬럼 코멘트 포함)
├── data_dictionary_ko.md  # 전체 컬럼 설명 (한국어)
├── requirements.txt
├── .env.example
└── TROUBLESHOOTING.md
```

## 2. 실행 방법

### 2-1. PostgreSQL 준비
```bash
# 로컬에 PostgreSQL이 떠 있다고 가정. DB만 하나 만들어주면 됨
createdb worldcup
```

### 2-2. 환경 설정
```bash
cp .env.example .env
# .env 안의 DATABASE_URL을 본인 환경에 맞게 수정
```

### 2-3. 의존성 설치
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2-4. 테이블 생성 + 데이터 적재
```bash
python scripts/load_data.py
```
`schema.sql`을 실행해 `players` / `matches` / `teams` 테이블을 만들고, `data/` 안의 CSV 3개를 그대로 적재합니다.

### 2-5. 서버 실행
```bash
uvicorn app.main:app --reload
```
브라우저에서 http://127.0.0.1:8000/docs 접속 → Swagger UI에서 바로 테스트 가능.

쓰기(POST/PUT/DELETE) API는 인증이 필요합니다. `/docs` 우측 상단 **Authorize** 버튼 클릭 →
`username: admin`, `password: admin1234` (`.env`에서 변경 가능)로 로그인하면 이후 요청에 토큰이 자동으로 붙습니다.

---

## 3. 엔드포인트

| Method | URL | 설명 | 인증 |
|---|---|---|---|
| POST | `/auth/login` | 로그인, JWT 토큰 발급 | - |
| GET | `/players` | 선수 목록 (team/position/search/min_goals 필터, 정렬, 페이지네이션) | - |
| GET | `/players/{id}` | 선수 상세 | - |
| POST | `/players` | 선수 추가 | ✅ |
| PUT | `/players/{id}` | 선수 정보 수정 (일부 필드만 전송 가능) | ✅ |
| DELETE | `/players/{id}` | 선수 삭제 | ✅ |
| GET | `/matches` | 경기 목록 (team/round/date_from/date_to 필터) | - |
| GET | `/matches/{id}` | 경기 상세 | - |
| GET | `/teams` | 팀 목록 (이름 검색) | - |
| GET | `/teams/{id}` | 팀 상세 | - |
| GET | `/stats/top-scorers` | pandas로 계산한 90분당 득점 상위 선수 | - |
| GET | `/stats/team-goal-diff` | pandas로 집계한 팀별 득실차/승점 순위표 | - |

## 4. 시도해본 것들

- 필터링/검색/정렬/페이지네이션 (`/players`, `/matches`)
- pandas로 SQL 결과 후처리 통계 API (`/stats/*`)
- JWT 로그인 붙여서 쓰기 API 보호
- SQLAlchemy automap으로 250개 넘는 컬럼을 손으로 모델링하지 않고 자동 리플렉션 처리
- Pydantic `RequestValidationError` 커스텀 핸들러로 422 에러 메시지 가독성 개선
- 컬럼 화이트리스트로 `sort_by` SQL 인젝션 방지

## 5. 팀원별 작업 내용

> ⚠️ 실제 팀원 이름/역할로 교체하세요.

| 팀원 | 담당 |
|---|---|
| OOO | DB 스키마 설계, 데이터 전처리(schema.sql, load_data.py) |
| OOO | players/matches/teams 라우터, 필터링·페이지네이션 |
| OOO | JWT 인증, pandas 통계 API, 에러 핸들링 |

## 6. requirements.txt 재생성 (최종 제출 시)

```bash
uv pip freeze > requirements.txt
```
