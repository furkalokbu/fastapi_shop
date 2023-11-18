from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, Request, Form
from app.database import SessionLocal
from sqlalchemy.orm import Session

import app.models as models

router = APIRouter(
    prefix='/shop',
    tags=['shop'],
    responses={404: {'description': 'Not found'}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/')
async def get_category(request: Request, db: db_dependency):

    # parent_category = models.Category(name="Parent Category")
    # db.add(parent_category)
    # db.commit()

    # child_category = models.Category(name="Child Category", parent_id=parent_category.id)
    # db.add(child_category)
    # db.commit()

    category = db.query(models.Category).all()
    
    return {'category': category}
