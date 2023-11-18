from app.database import Base
from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))

    # __table_args__ = (
    #     CheckConstraint("parent_id IS NULL OR (SELECT level FROM categories WHERE id = parent_id) < 10"),
    # )
    
    children = relationship("Category")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    
    categories = relationship("Category", secondary="item_category")


class ItemCategory(Base):
    __tablename__ = "item_category"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True, index=True)
