from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    patronymic: Mapped[str | None]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    roles: Mapped[list['Role']] = relationship(
        secondary='user_roles',
        back_populates='users'
    )


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list['User']] = relationship(
        secondary='user_roles',
        back_populates='roles'
    )
    permissions: Mapped[list['Permission']] = relationship(
        secondary='role_permissions',
        back_populates='roles'
    )


class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    roles: Mapped[list['Role']] = relationship(
        secondary='role_permissions',
        back_populates='permissions'
    )


class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), primary_key=True)


class RolePermission(Base):
    __tablename__ = 'role_permissions'

    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id'), primary_key=True)