from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import selectinload

from app.schemas import UserUpdate
from app.dependencies import SessionDep
from app.models import User
from passlib.context import CryptContext
from app.config import settings
import jwt
from sqlalchemy import select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

@router.get('/me')
async def get_profile(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_data = jwt.decode(credentials.credentials, settings.SECRET_KEY, settings.ALGORITHM)
    result = await session.execute(
        select(User)
        .where(User.email == user_data['email'])
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()
    return user

@router.put('/me')
async def update_profile(data: UserUpdate, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_data = jwt.decode(credentials.credentials, settings.SECRET_KEY, settings.ALGORITHM)
    result = await session.execute(select(User).where(User.email == user_data['email']))
    user = result.scalar_one_or_none()

    if user:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.patronymic = data.patronymic
        user.email = data.email
        await session.commit()
    await session.refresh(user)

    return {"first_name": user.first_name, "last_name": user.last_name, "patronymic": user.patronymic,
            "email": user.email}

@router.delete('/me')
async def delete_profile(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_data = jwt.decode(credentials.credentials, settings.SECRET_KEY, settings.ALGORITHM)
    result = await session.execute(select(User).where(User.email == user_data['email']))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    user.is_active = False
    await session.commit()

    return {"message": "Account deleted successfully"}