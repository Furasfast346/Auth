from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from app.dependencies import SessionDep
from app.models import User, Role, UserRole, Permission, RolePermission
from app.routers.users import get_current_admin
from app.schemas import RoleCreate, PermissionCreate, RolePermissionsUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def get_all_users(session: SessionDep, admin: User = Depends(get_current_admin)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = False
    await session.commit()
    return {"message": "User deactivated"}


@router.patch("/users/{user_id}/activate")
async def activate_user(user_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = True
    await session.commit()
    return {"message": "User activated"}


@router.put("/users/{user_id}/role")
async def set_user_role(user_id: int, role_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    await session.execute(delete(UserRole).where(UserRole.user_id == user_id))
    session.add(UserRole(user_id=user_id, role_id=role_id))
    await session.commit()
    return {"message": f"User {user_id} now has role {role.name}"}


@router.get('/roles')
async def get_roles(session: SessionDep, admin: User = Depends(get_current_admin)):
    result = await session.execute(select(Role))
    roles = result.scalars().all()
    return roles


@router.post('/roles')
async def create_role(data: RoleCreate, session: SessionDep, admin: User = Depends(get_current_admin)):
    existing = await session.execute(select(Role).where(Role.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Role already exists")
    new_role = Role(name=data.name)
    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


@router.delete('/roles/{role_id}')
async def delete_role(role_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    users_with_role = await session.execute(select(UserRole).where(UserRole.role_id == role_id))
    if users_with_role.first():
        raise HTTPException(400, "Cannot delete role: users have this role")
    await session.delete(role)
    await session.commit()
    return {"message": "Role deleted"}


@router.put('/roles/{role_id}/permissions')
async def add_permission(role_id: int, data: RolePermissionsUpdate, session: SessionDep, admin: User = Depends(get_current_admin)):
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(404, 'Role not found')

    for perm_id in data.permission_ids:
        perm = await session.get(Permission, perm_id)
        if not perm:
            raise HTTPException(404, 'Permission not found')
    await session.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    for perm_id in data.permission_ids:
        session.add(RolePermission(role_id=role_id, permission_id=perm_id))
    await session.commit()
    return {"message": f"Permissions assigned to role {role.name}"}


@router.get('/permissions')
async def get_permissions(session: SessionDep, admin: User = Depends(get_current_admin)):
    result = await session.execute(select(Permission))
    permissions = result.scalars().all()
    return permissions


@router.post('/permissions')
async def create_permission(data: PermissionCreate, session: SessionDep, admin: User = Depends(get_current_admin)):
    existing = await session.execute(select(Permission).where(Permission.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Permission Already exists')
    new_permission = Permission(name=data.name)
    session.add(new_permission)
    await session.commit()
    await session.refresh(new_permission)
    return new_permission


@router.delete('/permissions/{permission_id}')
async def delete_permission(permission_id: int, session: SessionDep, admin: User = Depends(get_current_admin)):
    permission = await session.get(Permission, permission_id)
    if not permission:
        raise HTTPException(404, 'permission not found')
    existing = await session.execute(select(RolePermission).where(RolePermission.permission_id == permission_id))
    if existing.scalars().one_or_none():
        raise HTTPException(400, "Cannot delete permission: it is assigned to a role")
    await session.delete(permission)
    await session.commit()