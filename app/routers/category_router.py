from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.database import get_db, engine

from sqlalchemy import func
from app.models.category_model import Category
from app.models.content_model import Content
from app.models.watch_history import History
from app.models.content_category import content_categories

from app.schemas.category_schema import * 


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

@router.get("/recommendations/{user_id}", response_model=list[CategoryOut])
def get_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    result = (
        db.query(Category)
        .join(content_categories, Category.id == content_categories.c.category_id)
        .join(Content, Content.id == content_categories.c.content_id)
        .join(History, History.content_id == Content.id)
        .filter(History.user_id == user_id)
        .group_by(Category.id)
        .order_by(func.count(Category.id).desc())
        .limit(5)
        .all()
    )

    return result