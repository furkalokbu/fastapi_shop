from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from app.database import SessionLocal
from sqlalchemy.orm import Session

import app.models as models

router = APIRouter(
    prefix='/categories',
    tags=['categories'],
    responses={404: {'description': 'Not found'}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]