from typing import List, Annotated, Optional, Set, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func, cast, select, text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base
from app.database import SessionLocal
import app.models as models

router = APIRouter(
    tags=['services'],
    responses={404: {'description': 'Not found'}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class CategoryResponse(BaseModel):
    id: int
    name: str
    children: Optional[List[int]] = []


class ItemResponse(BaseModel):
    id: int
    name: str
    price: int


@router.get("/categories-for-items/", response_model=list[CategoryResponse])
async def get_categories_for_items_api(db: db_dependency, 
                                       item_ids: list[int] = Query(..., description="List of item IDs")):

    stmt = (
        select(
            models.Category.id,
            models.Category.name,
            func.array_agg(models.Category.id).label("children_ids")
        )
        .join(models.ItemCategory, models.Category.id == models.ItemCategory.category_id)
        .join(models.Item, models.ItemCategory.item_id == models.Item.id)
        .filter(models.Item.id.in_(item_ids))
        .group_by(models.Category.id, models.Category.name)
    )

    result = db.execute(stmt)
    categories = result.fetchall()

    if not categories:
        raise HTTPException(
            status_code=404, detail="No categories found for the given items"
        )

    categories_response = [
        CategoryResponse(
            id=row.id,
            name=row.name,
            children=row.children_ids if row.children_ids else []
        ) for row in categories
    ]

    return categories_response


@router.get("/items-in-category/{category_id}", response_model=List[ItemResponse])
async def get_items_in_category(category_id: int, db=Depends(get_db)):

    items = {}
    stmt = (
        select(models.Item)
        .join(models.ItemCategory, models.Item.id == models.ItemCategory.item_id)
        .join(models.Category, models.ItemCategory.category_id == models.Category.id)
        .where(models.Category.id == category_id)
    )

    result = db.execute(stmt)
    items = result.scalars().all()

    return items
