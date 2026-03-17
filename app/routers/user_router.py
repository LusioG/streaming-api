
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm 
from app.database import get_db, engine 
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.security import get_current_user


from app.schemas.user_schema import * 
from app.models.user_model import *

router = APIRouter()

@router.post("/register", response_model=UserOut)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    user_exists = db.query(User).filter(
    User.email == user.email
    ).first()
 
    if user_exists:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed = hash_password(user.password)
    nuevo = User(
        email=user.email,
        username=user.username,
        password_hash=hashed
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), # Esto habilita el cuadrito
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
        ).first()

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user = Depends(get_current_user)):
    return user


@router.patch("/update/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.dict(exclude_unset=True)

    # manejar password aparte
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for k, v in update_data.items():
        setattr(user, k, v)

    db.commit()
    db.refresh(user)

    return user


