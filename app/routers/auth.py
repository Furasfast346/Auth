from fastapi import APIRouter, HTTPException
from app.schemas import UserRegister
from app.dependencies import SessionDep
from app.models import User
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post('/register')
async def register(data: UserRegister, session: SessionDep):
    if data.password == data.password_confirmation:
        password = pwd_context.hash(data.password)
        new_user = User(first_name=data.first_name, last_name=data.last_name, email=data.email, patronymic=data.patronymic,
                        is_active=True, password_hash=password, role)
        session.add(new_user)
        await session.commit()

    return HTTPException(status_code=400, detail="Wrong Password")




@router.post('/login')
async def login():
    return {'msg': 'login endpoint'}
    #is_valid = pwd_context.verify("mypassword", hashed)



@router.post('/logout')
async def logout():
    return {'msg': 'logout endpoint'}