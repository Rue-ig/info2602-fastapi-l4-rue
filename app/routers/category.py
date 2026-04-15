from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

category_router = APIRouter(tags=["Category"])

@category_router.post('/category', response_model=CategoryResponse)
def create_category(db:SessionDep, user:AuthDep, category_data:CategoryCreate):
    category = Category(text=category_data.text, user_id=user.id)
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating a category",
        )
    
@category_router.post('/todo/{todo_id}/category/{cat_id}')
def add_category_to_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):
    selected_todo = db.exec(select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)).one_or_none()
    selected_cat = db.exec(select(Category).where(Category.id==cat_id, Category.user_id==user.id)).one_or_none()

    if  not selected_todo or not selected_cat:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    if selected_cat in selected_todo.categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already added to todo",
        )
    else:
        selected_todo.categories.append(selected_cat)

    try:
        db.add(selected_todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while adding category to todo",
        )
    
@category_router.delete('/todo/{todo_id}/category/{cat_id}')
def remove_category_from_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):
    selected_todo = db.exec(select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)).one_or_none()
    selected_cat = db.exec(select(Category).where(Category.id==cat_id, Category.user_id==user.id)).one_or_none()

    if  not selected_todo or not selected_cat:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    if selected_cat not in selected_todo.categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found in todo",
        )
    else:
        selected_todo.categories.remove(selected_cat)

    try:
        db.add(selected_todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while removing category from todo",
        )


@category_router.get('/category/{cat_id}/todos', response_model=list[TodoResponse])
def get_todos_for_category(cat_id:int, db:SessionDep, user:AuthDep):
    category = db.exec(select(Category).where(Category.id==cat_id, Category.user_id==user.id)).one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    return category.todos