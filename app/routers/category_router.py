from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.database import get_db, engine

from app.schemas.category_schema import * 
from app.models.category_model import *

router = APIRouter()

@router.post("/", response_model=CategoryOut)
def add_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    category_exist = db.query(Category).filter(
        Category.name == category.name
    ).first()

    if category_exist:
        raise HTTPException(409, "Categoria ya existente")

    nueva = Category(
            name=category.name
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva

@router.get("/", response_model=list[CategoryOut])
def get_categories(
    limit: int = Query(20),
    offset: int = Query(0, ge=0),
    sort: str = Query("name"),  # por defecto ordenar por name
    descending: bool = Query(False),
    db: Session = Depends(get_db)
):
    # Creamos la consulta base
    query = db.query(Category)
    
    # Sorting dinámico
    column = getattr(Category, sort, None)  # chequea que exista el atributo
    if column is not None:
        query = query.order_by(column.desc() if descending else column.asc())
    
    # Paginación y ejecución
    categories = query.limit(limit).offset(offset).all()

    return categories