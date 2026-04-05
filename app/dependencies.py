from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import async_session
from app.models import User, Role
from app.config import settings
import jwt

async def get_session():
    async with async_session() as session:
        yield session
SessionDep = Annotated[AsyncSession, Depends(get_session)]


security = HTTPBearer()


async def get_current_user(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(401, "Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")

    return user


async def get_current_admin(session: SessionDep, current_user: User = Depends(get_current_user)) -> User:
    result = await session.execute(select(User).where(User.id == current_user.id).options(selectinload(User.roles)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")

    if not any(role.name == "admin" for role in user.roles):
        raise HTTPException(403, "Admin rights required")

    return user


async def has_permission(user: User, permission_name: str, session: SessionDep) -> bool:
    result = await session.execute(select(User).where(User.id == user.id).options(selectinload(User.roles).selectinload(Role.permissions)))
    user_with_roles = result.scalar_one_or_none()

    if not user_with_roles:
        return False

    for role in user_with_roles.roles:
        for perm in role.permissions:
            if perm.name == permission_name:
                return True
    return False



def require_permission(permission_name: str):
    async def dependency(session: SessionDep, current_user: User = Depends(get_current_user)):
        if not await has_permission(current_user, permission_name, session):
            raise HTTPException(403, f"Forbidden: {permission_name} required")
        return current_user

    return dependency