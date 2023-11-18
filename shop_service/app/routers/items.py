from typing import List
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import Base
from app.database import SessionLocal
import app.models as models

router = APIRouter(
    prefix='/items',
    tags=['items'],
    responses={404: {'description': 'Not found'}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class Item(BaseModel):
    id: int
    name: str
    price: int

class ItemCreate(BaseModel):
    name: str
    price: int

class ItemUpdate(BaseModel):
    name: str = None
    price: int = None
    category_ids: List[int]


@router.get("/", response_model=List[Item])
def get_all_items(db: db_dependency, skip: int = 0, limit: int = 10):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items


@router.post("/")
def create_item(db: db_dependency, item: ItemCreate, category_ids: List[int]):
    categories = db.query(models.Category).filter(models.Category.id.in_(category_ids)).all()
    if not categories:
        raise HTTPException(status_code=404, detail="Categories not found")

    item = models.Item(**item.dict(), categories=categories)
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@router.put("/{item_id}")
def update_item(db: db_dependency, item_id: int, item_update: ItemUpdate):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if item:
        for key, value in item_update.dict().items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_api(db: db_dependency, item_id: int):

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if item:
        db.delete(item)
        db.commit()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item
