from fastapi import FastAPI
from app.routers import auth, users, admin, mock
from .database import init_db


app = FastAPI(title="Auth System")

@app.on_event('startup')
async def on_startup():
    await init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(mock.router, prefix="/api", tags=["mock"])