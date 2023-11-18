from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse

from app.models import Base
from app.database import engine
from app.routers import categories

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(categories.router)
