from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class ItemAttributeLink(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)
    attribute_id: Optional[int] = Field(default=None, foreign_key="attribute.id", primary_key=True)

class AttributeBase(SQLModel):
    name: str
    value: str

class Attribute(AttributeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="attributes", link_model=ItemAttributeLink)

class AttributeRead(AttributeBase):
    id: int

class AttributeCreate(AttributeBase):
    pass

class ItemBase(SQLModel):
    name: str
    image_url: Optional[str] = Field(default=None)

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attributes: List[Attribute] = Relationship(back_populates="items", link_model=ItemAttributeLink)

class ItemRead(ItemBase):
    id: int
    attributes: List[AttributeRead] = []

class ItemCreate(ItemBase):
    name: str
    image_url: Optional[str] = Field(default=None)  # Added image_url field

class ItemUpdate(ItemBase):
    name: str
    image_url: Optional[str] = Field(default=None)  # Added image_url field