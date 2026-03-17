from pydantic import BaseModel, EmailStr
from datetime import datetime


# Schema para crear/añadir
class UserCreate(BaseModel):
    email: str 
    username: str
    password: str

# Schema para login
class UserLogin(BaseModel):
    email: EmailStr
    password:str

# Schema usuario completo (sin contraseña)
class UserOut(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
        
from typing import Optional

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None