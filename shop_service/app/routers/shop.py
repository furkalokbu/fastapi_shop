from typing import Annotated
from starlette import status
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

@router.get('/')
async def get_category(request: Request, db: db_dependency):
    category = db.query(models.Category).all()
    
    return {'category': category}


@router.post("/")
def create_category(db: db_dependency, name: str, parent_id: int = None):
    category = models.Category(name=name, parent_id=parent_id)
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.put("/{category_id}")
def update_category(db: db_dependency, category_id: int, name: str, parent_id: int = None):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = name
    category.parent_id = parent_id
    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(db: db_dependency, category_id: int):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()

    return {"message": "Category deleted"}
