from pydantic import BaseModel
from app import schemas


class PlayerCreateSchema(BaseModel):
    email: str
    nick_name: str


class PlayerUpdateSchema(BaseModel): ...


class LoginOutput(schemas.Token):
    email: str
    nick_name: str
    id: int


class PlayerLogin(BaseModel):
    email: str


class PlayerRegister(BaseModel):
    email: str
    nick_name: str
