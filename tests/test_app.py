import time

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

async def get_token(client, email, password):
    response = await client.post("/auth/login", json={"email": email, "password": password})
    return response.json().get("access_token")

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.post("/auth/register", json={
            "email": f"test_{time.time()}@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
            "first_name": "Test",
            "last_name": "User",
            "patronymic": None
        })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_register_password_mismatch():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.post("/auth/register", json={
            "email": "newuser2@example.com",
            "password": "secret123",
            "password_confirmation": "wrongeeee",
            "first_name": "Test",
            "last_name": "User",
            "patronymic": None
        })
    assert response.status_code == 400
    assert "Passwords do not match" in response.text


@pytest.mark.asyncio
async def test_register_email_exists():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        await ac.post("/auth/register", json={
            "email": "duplicate@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
            "first_name": "Test",
            "last_name": "User",
            "patronymic": None
        })
        response = await ac.post("/auth/register", json={
            "email": "duplicate@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
            "first_name": "Test",
            "last_name": "User",
            "patronymic": None
        })
    assert response.status_code == 400
    assert "Email are already registered" in response.text


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "wrongpassword"
        })
    assert response.status_code == 400
    assert "Wrong password" in response.text


@pytest.mark.asyncio
async def test_login_email_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anything"
        })
    assert response.status_code == 400
    assert "Email not found" in response.text


@pytest.mark.asyncio
async def test_get_profile_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_authorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        token = await get_token(ac, "admin@example.com", "admin123")
        response = await ac.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


@pytest.mark.asyncio
async def test_update_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        token = await get_token(ac, "admin@example.com", "admin123")
        response = await ac.put("/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated", "last_name": "Admin"}
        )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_get_products_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        response = await ac.get("/products/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_products_authorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        token = await get_token(ac, "admin@example.com", "admin123")
        response = await ac.get("/products/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        token = await get_token(ac, "admin@example.com", "admin123")
        response = await ac.post("/products/",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test Product", "price": 100, "in_stock": True}
        )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_admin_users_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        token = await get_token(ac, "admin@example.com", "admin123")  # admin имеет доступ
        response = await ac.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # админ должен иметь доступ


@pytest.mark.asyncio
async def test_get_admin_users_forbidden_for_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as ac:
        await ac.post("/auth/register", json={
            "email": "regular@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
            "first_name": "Regular",
            "last_name": "User",
            "patronymic": None
        })
        token = await get_token(ac, "regular@example.com", "secret123")
        response = await ac.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403