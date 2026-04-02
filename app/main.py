from fastapi import FastAPI
from app.routers import auth, users, admin, mock

app = FastAPI(title="Auth System")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(mock.router, prefix="/api", tags=["mock"])