from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.models import db_helper
from app.core.schemas import UserCreate, UserRead
from .crud import user as user_crud

router = APIRouter(tags=["User"])

@router.post("/create_user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],):
 
    existing_user = await user_crud.get_user_by_username(session, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    if user.email:
        existing_email = await user_crud.get_user_by_email(session, email=user.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    try:
        db_user = await user_crud.create_user(session, user=user)
        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user due to integrity error",
        )


@router.get("/users", response_model=list[UserRead], status_code=status.HTTP_201_CREATED)
async def get_users(session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],):
 
    users = await user_crud.get_all_users(session=session)
    return users
    
