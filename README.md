# Auth System — система аутентификации и авторизации

Современный бэкенд на **FastAPI** с JWT-аутентификацией, ролевой моделью доступа (RBAC), админ-панелью и полным CRUD для пользователей, товаров и ролей.

## Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — асинхронная ORM
- **SQLite** — база данных
- **JWT (PyJWT)** — токены доступа
- **bcrypt** — хэширование паролей
- **Pytest** — тестирование
- **Docker** — контейнеризация
- **HTML/CSS/JS** — фронтенд (демонстрация)

## Установка и запуск

### Локальный запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Furasfast346/Auth.git
cd Auth

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload

### Запуск через Докер
docker build -t auth-system .
docker run -p 8000:8000 auth-system
