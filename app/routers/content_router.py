from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine 
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.security import get_current_user


from app.schemas.content_schema import * 
from app.models.content_model import *
from app.models.category_model import *

router = APIRouter()


@router.post("/", response_model=ContentOut)
def add_content(
    content: ContentCreate,
    db: Session = Depends(get_db)
):

    content_exist = db.query(Content).filter(
        Content.name == content.name
    ).first()

    if content_exist:
        raise HTTPException(400, "Contenido ya existente")

    nuevo = Content(
        name=content.name,
        description=content.description,
        image_url=content.image_url,
        banner_url=content.banner_url,
        duration_minutes=content.duration_minutes
    )

    if content.categories:

        categorias = db.query(Category).filter(
            Category.id.in_(content.categories)
        ).all()

        if len(categorias) != len(content.categories):
            raise HTTPException(
                status_code=400,
                detail="Alguna categoria no existe"
            )

        nuevo.categories = categorias

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo



from sqlalchemy import exists, or_
from app.models.watch_history import History


from fastapi import Query

@router.get("/search", response_model=list[ContentOut])
def search_contents(
    q: str,
    limit: int = Query(20),
    offset: int = Query(0, ge=0),
    sort: str = Query("name"),  # por defecto ordenar por name
    descending: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Content)
        .filter(
            Content.is_active == True,
            or_(
                Content.name.ilike(f"%{q}%"),
                Content.description.ilike(f"%{q}%")
            )
        )
    )
    
    column = getattr(Content, sort, None)  # chequea que exista el atributo
     
    if column is not None:
        query = query.order_by(column.desc() if descending else column.asc())
            
    contents = query.limit(limit).offset(offset).all()  

    return contents



@router.get("/", response_model=list[ContentOut])
def get_contents(
    category: int | None = None,
    watched: bool | None = None,
    limit: int = Query(20),
    offset: int = Query(0, ge=0),
    sort: str = Query("name"),  # por defecto ordenar por name
    descending: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
     # Creamos la consulta base
    query = db.query(Content).filter(Content.is_active == True)

    if category:
        query = query.join(Content.categories).filter(Category.id == category)

    if watched is not None:
        subquery = db.query(History).filter(
            History.user_id == current_user.id,
            History.content_id == Content.id
        )
        if watched:
            query = query.filter(subquery.exists())
        else:
            query = query.filter(~subquery.exists())

    # Sorting dinámico
    column = getattr(Content, sort, None) #chequea el contenido del atributo sort, si no hay nada None
     
    if column is not None:
        if descending:
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
            
    # Paginación y ejecución
    return query.limit(limit).offset(offset).all()





@router.get("/{content_id}", response_model=ContentOut)
def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db)
):
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.is_active == True
    ).first()

    if not content:
        raise HTTPException(404, "Contenido no encontrado")

    return content

@router.patch("/{content_id}", response_model=ContentOut)
def update_content(
    content_id: int,
    data: ContentUpdate,
    db: Session = Depends(get_db)
):

    content = db.query(Content).filter(
        Content.id == content_id,
        Content.is_active == True
    ).first()

    if not content:
        raise HTTPException(404, "Contenido no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for k, v in update_data.items():
        setattr(content, k, v)

    db.commit()
    db.refresh(content)

    return content




@router.patch("/{content_id}/desactivate", response_model=ContentOut)
def desactivate_content(
    content_id: int,
    db: Session = Depends(get_db)
):

    content = db.query(Content).filter(Content.id == content_id).first()

    if not content:
        raise HTTPException(404, "Contenido no encontrado")

    content.is_active = False

    db.commit()
    db.refresh(content)

    return content


