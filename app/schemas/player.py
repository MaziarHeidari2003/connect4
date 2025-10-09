from pydantic import BaseModel, EmailStr
from app import schemas


class PlayerCreateSchema(BaseModel):
    email: EmailStr
    nick_name: str


class PlayerUpdateSchema(BaseModel): ...


class LoginOutput(schemas.Token):
    email: EmailStr
    nick_name: str
    id: int


class PlayerLogin(BaseModel):
    email: EmailStr


class PlayerRegister(BaseModel):
    email: EmailStr
    nick_name: str
