from pydantic import BaseModel
from typing import Optional

class Login(BaseModel):
    email: str
    password: str

class Register(BaseModel):
    name:str
    email: str
    password: str
    types: str

class Notes(BaseModel):
    title: str
    description: str
    custome_id: Optional[str] = None

