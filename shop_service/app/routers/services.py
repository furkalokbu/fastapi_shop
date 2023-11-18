from typing import List, Annotated, Optional, Set, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from sqlalchemy.future import select

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
async def get_items_in_category(db: db_dependency, category_id: int):

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


@router.get("/item-counts-in-categories/", response_model=dict)
async def get_item_counts_in_categories(db: db_dependency, 
                                  category_ids: List[int] = Query(..., description="List of category IDs")):
    results = {}
    for category_id in category_ids:
        category = db.query(models.Category).get(category_id)
        if category:
            product_count = (
                db.query(models.Item)
                .join(models.ItemCategory)
                .filter(models.ItemCategory.category_id == category.id)
                .count()
            )
            results[category_id] = product_count
        else:
            results[category_id] = 0

    return results


@router.get("/total_unique_product_offers/")
async def get_total_unique_product_offers(db: db_dependency,
    category_ids: list[int] = Query(..., title="List of category IDs")):

    total_unique_product_offers = (
        db.query(models.Item)
        .join(models.ItemCategory)
        .filter(models.ItemCategory.category_id.in_(category_ids))
        .distinct(models.Item.id)
        .count()
    )

    return {"total_unique_product_offers": total_unique_product_offers}
