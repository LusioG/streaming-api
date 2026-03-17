from fastapi import FastAPI
from app.database import Base, engine
from app.config import settings



# IMPORTAR MODELOS
from app.models.user_model import User
from app.models.content_model import Content
from app.models.category_model import Category
from app.models.watch_history import History

#IMPORTAR ROUTERS
from app.routers import user_router, content_router, watch_history_router, category_router

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version
)


# Registrás los routers
app.include_router(user_router.router, prefix="/users", tags=["users"])
app.include_router(content_router.router, prefix="/contents", tags=["contents"])
app.include_router(watch_history_router.router, prefix="/history", tags=["history"])
app.include_router(category_router.router, prefix="/category", tags=["category"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Streaming API running"}
