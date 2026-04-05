from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.schemas import UserUpdate
from app.dependencies import SessionDep, get_current_user
from app.models import User

router = APIRouter()


@router.get('/me')
async def get_profile(session: SessionDep, current_user: User = Depends(get_current_user)):
    result = await session.execute(select(User).where(User.id == current_user.id).options(selectinload(User.roles)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    role_name = user.roles[0].name if user.roles else "user"

    return {"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
            "patronymic": user.patronymic, "is_active": user.is_active, "role": role_name}


@router.put('/me')
async def update_profile(data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    if data.first_name is not None:
        current_user.first_name = data.first_name
    if data.last_name is not None:
        current_user.last_name = data.last_name
    if data.patronymic is not None:
        current_user.patronymic = data.patronymic
    if data.email is not None:
        current_user.email = data.email
    await session.commit()
    await session.refresh(current_user)

    return {"first_name": current_user.first_name, "last_name": current_user.last_name,
            "patronymic": current_user.patronymic, "email": current_user.email}


@router.delete('/me')
async def delete_profile(session: SessionDep, current_user: User = Depends(get_current_user)):
    current_user.is_active = False
    await session.commit()
    return {"message": "Account deleted successfully"}
