from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None


class UserRegister(UserBase):
    password: str = Field(min_length=6)
    password_confirmation: str = Field(min_length=6)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RoleCreate(BaseModel):
    name: str

class PermissionCreate(BaseModel):
    name: str

class RolePermissionsUpdate(BaseModel):
    permission_ids: list[int]

class ProductCreate(BaseModel):
    name: str
    price: int
    in_stock: bool = True

class ProductUpdate(BaseModel):
    name: str
    price: int
    in_stock: bool

class ProductResponse(ProductCreate):
    id: int

class RoleAssign(BaseModel):
    role_id: int