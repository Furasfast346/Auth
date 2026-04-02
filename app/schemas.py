from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None


class UserRegister(UserBase):
    password: str = Field(min_length=8)
    password_confirmation: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
