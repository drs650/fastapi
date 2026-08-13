'''
======================================================================================
services/todo_service.py

Todo 관련 "업무 규칙"을 담당하는 계층
DB 쿼리 자체는 직접하지 않고, TodoRepository에세 다 위임한다.
없으면 "404 에러를 낸다." 수정할 때 "title/is_done만 부분 반영한다." 등의 판단들을 정의
이 파일은 FastAPI의 요청/응답 객체를 직접 다루지 않는다. (routers에서 다룬다.)
======================================================================================
'''
from fastapi import HTTPException, status
from models import Todo
from repositories.todo_repository import TodoRepository
from schema.request import TodoCreateRequest, TodoUpdateRequest


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def get_todos(self, user_id: int) -> list[Todo]:
        return self.repository.find_all_by_user(user_id)

    def get_todo(self, todo_id: int, user_id: int) -> Todo:
        todo = self.repository.find_by_id(todo_id, user_id)
        if todo is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Todo not found")
        return todo

    def create_todo(self, body: TodoCreateRequest, user_id: int) -> Todo:
        todo = Todo(title=body.title, is_done=body.is_done, user_id=user_id)
        return self.repository.save(todo)

    def update_todo(self, todo_id: int, body: TodoUpdateRequest, user_id: int) -> Todo:
        todo = self.get_todo(todo_id, user_id)
        if body.title is not None:
            todo.title = body.title
        if body.is_done is not None:
            todo.is_done = body.is_done
        return self.repository.save(todo)

    def delete_todo(self, todo_id: int, user_id: int) -> None:
        todo = self.get_todo(todo_id, user_id)
        self.repository.delete(todo)
