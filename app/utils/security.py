from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.database import get_db

from jose import JWTError, jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

# Carga las variables de .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # valor por defecto
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

#Transforma la contraseña a codigo hash
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


#Los Token habilitan al usuario a usar endpoints protegidos

#El JWT se inserta en el encabezado de las peticiones que realizamos del front para validar identidad
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")



def get_current_user(
  token: str = Depends(oauth2_scheme),
  db: Session = Depends(get_db)      
):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401,"Token inválido")

    #EL campo "sub" dentro del token guarda la ID del usuario 
    user_id = int(payload.get("sub"))
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(401, "Usuario no existe")
    return user

    