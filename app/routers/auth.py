from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from app.schemas import UserRegister, UserLogin
from app.dependencies import SessionDep
from app.models import User, UserRole
from passlib.context import CryptContext
from app.config import settings
import jwt
from sqlalchemy import select


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post('/register')
async def register(data: UserRegister, session: SessionDep):
    if data.password != data.password_confirmation:
        raise HTTPException(status_code=400, detail='Passwords do not match')

    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        if not existing_user.is_active:
            raise HTTPException(status_code=400, detail='User was deleted')
        raise HTTPException(status_code=400, detail='Email are already registered')

    password = pwd_context.hash(data.password)
    new_user = User(first_name=data.first_name, last_name=data.last_name,
                    email=data.email, patronymic=data.patronymic,
                    is_active=True, password_hash=password)
    session.add(new_user)
    await session.flush()
    session.add(UserRole(user_id=new_user.id, role_id=3))  # 3 — ID роли "user"
    await session.commit()

    encoded = jwt.encode({'email': data.email, 'role': 'user'}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(encoded)
    return {'access_token': encoded}


@router.post('/login')
async def login(data: UserLogin, session: SessionDep):
    result = await session.execute(
        select(User)
        .where(User.email == data.email)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    if not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Wrong password")

    role_name = user.roles[0].name if user.roles else "user"

    encoded = jwt.encode(
        {'email': user.email, 'role': role_name}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {'access_token': encoded}


@router.post('/logout')
async def logout():
    return {"message": "Logged out successfully"}
