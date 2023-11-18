import random
from typing import Annotated
from faker import Faker
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models

router = APIRouter(
    tags=['populate database'],
    responses={404: {'description': 'Not found'}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

fake = Faker()


def create_categories(session, parent_id=None, level=1):
    for _ in range(random.randint(2, 5)):
        category = models.Category(name=fake.word(), parent_id=parent_id)
        session.add(category)
        session.flush()
        if level < 3 and random.choice([True, False]):
            create_categories(session, parent_id=category.id, level=level + 1)


def create_items(session, categories, num_items=50):
    for _ in range(num_items):
        item = models.Item(name=fake.word(), price=random.randint(10, 100))
        session.add(item)
        session.flush()

        item_categories = random.sample(categories, k=random.randint(1, 3))
        for category in item_categories:
            item_category = models.ItemCategory(item_id=item.id, category_id=category.id)
            session.add(item_category)


def populate_database(db):
    try:

        db.query(models.ItemCategory).delete()
        db.query(models.Item).delete()
        db.query(models.Category).delete()

        root_categories = []
        for _ in range(3):
            category = models.Category(name=fake.word())
            db.add(category)
            db.flush()
            root_categories.append(category)
            create_categories(db, parent_id=category.id)

        create_items(db, root_categories)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/populate_database/")
async def populate_database_route(db: db_dependency):
    populate_database(db)
    return {"message": "Database populated with test data"}
