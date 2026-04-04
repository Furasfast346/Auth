from fastapi import FastAPI
from app.routers import auth, users, admin, products
from app.database import init_db
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auth System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def on_startup():
    await init_db()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
#app.include_router(admin.router, prefix="/admin", tags=["admin"])
#app.include_router(mock.router, prefix="/api", tags=["mock"])

if __name__ == "__main__":
    uvicorn.run('app.main:app', reload=True)
