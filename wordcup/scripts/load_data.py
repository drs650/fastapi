"""
1) schema.sql을 실행해 players / matches / teams 테이블을 생성하고
2) data/*.csv 를 읽어서 그대로 적재합니다.

실행 방법 (프로젝트 루트에서):
    python scripts/load_data.py
"""
import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldcup",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DATA_DIR = os.path.join(BASE_DIR, "data")

TABLES = {
    "players": "players.csv",
    "matches": "matches.csv",
    "teams": "teams.csv",
}


def run_schema(engine):
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema_sql = f.read()
    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                conn.execute(text(statement))
    print("schema.sql 실행 완료 (테이블 생성)")


def load_csv(engine, table, filename):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path)
    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"{filename} -> {table} 테이블에 {len(df)}행 적재 완료")


def main():
    engine = create_engine(DATABASE_URL)
    run_schema(engine)
    for table, filename in TABLES.items():
        load_csv(engine, table, filename)


if __name__ == "__main__":
    main()
