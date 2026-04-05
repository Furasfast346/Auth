import asyncio
from sqlalchemy import select, delete
from app.database import async_session
from app.models import User, Role, Permission, UserRole, RolePermission, Product
from app.routers.auth import pwd_context

async def seed_database():
    async with async_session() as session:
        await session.execute(delete(UserRole))
        await session.execute(delete(RolePermission))
        await session.execute(delete(User))
        await session.execute(delete(Role))
        await session.execute(delete(Permission))
        await session.execute(delete(Product))
        await session.commit()
        print("Старые данные удалены.")

        # 2. Роли
        roles_data = ["admin", "manager", "user"]
        roles = {}
        for role_name in roles_data:
            role = Role(name=role_name)
            session.add(role)
            roles[role_name] = role
        await session.flush()
        print("Роли добавлены.")

        # 3. Разрешения
        permissions_data = [
            "users:read", "users:write",
            "products:read", "products:write", "products:delete"
        ]
        perms = {}
        for perm_name in permissions_data:
            perm = Permission(name=perm_name)
            session.add(perm)
            perms[perm_name] = perm
        await session.flush()
        print("Разрешения добавлены.")

        admin_role = roles["admin"]
        for perm in perms.values():
            session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

        manager_role = roles["manager"]
        for pname in ["products:read", "products:write", "products:delete"]:
            session.add(RolePermission(role_id=manager_role.id, permission_id=perms[pname].id))

        user_role = roles["user"]
        session.add(RolePermission(role_id=user_role.id, permission_id=perms["products:read"].id))
        print("Связи ролей и разрешений добавлены.")

        existing_admin = await session.execute(select(User).where(User.email == "admin@example.com"))
        if not existing_admin.scalar_one_or_none():
            admin_user = User(
                email="admin@example.com",
                password_hash=pwd_context.hash("admin123"),
                first_name="Admin",
                last_name="Adminov",
                patronymic=None,
                is_active=True
            )
            session.add(admin_user)
            await session.flush()
            session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            print("Тестовый админ создан.")
        else:
            print("Тестовый админ уже существует.")

        products_data = [
            {"name": "Ноутбук", "price": 1200, "in_stock": True},
            {"name": "Мышь", "price": 25, "in_stock": True},
            {"name": "Клавиатура", "price": 80, "in_stock": False},
        ]
        for p in products_data:
            existing = await session.execute(select(Product).where(Product.name == p["name"]))
            if not existing.scalar_one_or_none():
                session.add(Product(**p))
        await session.commit()
        print("Товары добавлены.")

        print("\n✅ База данных успешно заполнена!")

async def main():
    await seed_database()

if __name__ == "__main__":
    asyncio.run(main())