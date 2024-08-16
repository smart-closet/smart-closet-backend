from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class ItemAttributeLink(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)
    attribute_id: Optional[int] = Field(default=None, foreign_key="attribute.id", primary_key=True)

class OutfitItemLink(SQLModel, table=True):
    outfit_id: Optional[int] = Field(default=None, foreign_key="outfit.id", primary_key=True)
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)

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

class CategoryBase(SQLModel):
    name: str

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="category")
    
    def item_ids(self):
        return [item.id for item in self.items]

class CategoryRead(CategoryBase):
    id: int

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: str

class ItemBase(SQLModel):
    name: str
    image_url: Optional[str] = Field(default=None)
    category_id: int = Field(..., foreign_key="category.id")

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attributes: List[Attribute] = Relationship(back_populates="items", link_model=ItemAttributeLink)
    outfits: List["Outfit"] = Relationship(back_populates="items", link_model=OutfitItemLink)
    category: Category = Relationship(back_populates="items")

class ItemRead(ItemBase):
    id: int
    attributes: List[AttributeRead] = []

class ItemCreate(ItemBase):
    name: str
    image_url: Optional[str] = Field(default=None)
    category_id: int  # Added category_id

class ItemUpdate(ItemBase):
    name: str
    image_url: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)  # Added category_id

# outfit model
class OutfitBase(SQLModel):
    name: str

class Outfit(OutfitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="outfits", link_model=OutfitItemLink)

class OutfitRead(OutfitBase):
    id: int
    items: List[ItemRead] = []

class OutfitCreate(OutfitBase):
    name: str

class OutfitUpdate(OutfitBase):
    name: str

class OutfitDelete(OutfitBase):
    name: str