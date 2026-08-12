'''
================================================================================
models.py

SQLAlchemy ORM 모델 정의 파일
파이썬 클래스와 DB 테이블을 매핑(Mapping)하는 부분

================================================================================
'''
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.orm import Base


class Todo(Base):
    __tablename__ = 'todo' # 실제 DB에 생성될 테이블 이름

    # 컬럼(열) --> id, title, is_done, user_id
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True, # 기본키
        autoincrement=True, # 새 행이 추가될 때마다 1씩 자동 증가
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False, # 널이 가능하지 않다. --> 반드시 입력
    )
    is_done: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False, # 새로 생성될 때마다 기본값은 '완료 안 함'
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=True,
    )
    user: Mapped['User'] = relationship(
        back_populates='todos',
    )

# --- User 모델 (회원 테이블) -----------------------------------------
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False, # 필수 --> 비밀번호는 평문이 아닌 '해시된 값'으로 지정
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),  # 행 추가 시점에 DB가 자동으로 현재 시간을 채운다.
        nullable=False, # 필수
    )
    refresh_token: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True, # 로그인 전이거나, 로그아웃한 사용자는 None
    )
    todos: Mapped[list['Todo']] = relationship(
        back_populates='user',
        # cascade='all, delete-orphan'--> 회원이 삭제되면 그 회원의 Todo들도 함께 자동삭제 
        cascade='all, delete-orphan',
    )
