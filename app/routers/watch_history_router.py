from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db, engine 
from app.utils.security import get_current_user


from app.schemas.watch_history import * 
from app.models.watch_history import *

router = APIRouter()

@router.post("/")
def create_watch_history(
    data: WatchHistoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    history = History(
        user_id=current_user.id,
        content_id=data.content_id,
        progress=data.progress
    )

    db.add(history)
    db.commit()

    return {"message": "Vista registrada"}


from sqlalchemy.orm import joinedload

@router.get("/", response_model=list[WatchHistoryOut])
def get_user_history(
    current_user = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("content_id"),
    descending: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = db.query(History).options(
        joinedload(History.content)
    ).filter(
        History.user_id == current_user.id
    )

    column = getattr(History, sort, None)
    if column is not None:
        query = query.order_by(column.desc() if descending else column.asc())

    history = query.limit(limit).offset(offset).all()

    return history