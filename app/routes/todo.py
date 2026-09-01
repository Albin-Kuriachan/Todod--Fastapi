from fastapi import APIRouter, Depends, HTTPException, status, Response,Query,Path
from app.models.todo_model import Todo
from app.schemas.todo import TodoCreate, TodoResponse,TodoUpdate
from app.database.connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.auth_fun import  get_current_user
from app.models.user_models import User


db_session = Depends(get_db)

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_toddo =Todo(**todo.model_dump(), user_id=current_user.id)
    db.add(new_toddo)
    db.commit()
    db.refresh(new_toddo)
    return new_toddo

@router.get("/", response_model=list[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0,ge=0,description="Number of items to skip"),
    limit: int = Query(10,ge=1,le=100,description="Number of items to return")
):
    todos = db.execute(select(Todo).where(Todo.user_id == current_user.id).limit(limit).offset(skip)).scalars().all()
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo( 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_id: int = Path(gt=0)
):
    todo = db.execute(select(Todo).where(Todo.id == todo_id,Todo.user_id == current_user.id)).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int, 
    todo: TodoUpdate, 
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    todo_to_update = db.execute(select(Todo).where(Todo.id == todo_id,Todo.user_id == current_user.id)).scalar_one_or_none()
    if not todo_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo_update = todo.model_dump()
    for key, value in todo_update.items():
        setattr(todo_to_update, key, value)
    db.commit()
    db.refresh(todo_to_update)
    return todo_to_update

@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(todo_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    todo_to_complete = db.execute(select(Todo).where(Todo.id == todo_id)).scalar_one_or_none()
    if not todo_to_complete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo_to_complete.complete = True
    db.commit()
    db.refresh(todo_to_complete)
    return todo_to_complete

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    todo_to_delete = db.execute(select(Todo).where(Todo.id == todo_id,Todo.user_id == current_user.id)).scalar_one_or_none()
    if not todo_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)