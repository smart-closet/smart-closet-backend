from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional


class ItemAttributeLink(SQLModel, table=True):
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )
    attribute_id: Optional[int] = Field(
        default=None, foreign_key="attribute.id", primary_key=True
    )


class OutfitItemLink(SQLModel, table=True):
    outfit_id: Optional[int] = Field(
        default=None, foreign_key="outfit.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class AttributeBase(SQLModel):
    name: str
    value: str


class Attribute(AttributeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(
        back_populates="attributes", link_model=ItemAttributeLink
    )


class AttributeRead(AttributeBase):
    id: int


class AttributeCreate(AttributeBase):
    pass


class CategoryBase(SQLModel):
    name: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="category")
    subcategories: List["Subcategory"] = Relationship(back_populates="category")

    def item_ids(self):
        return [item.id for item in self.items]


class CategoryRead(CategoryBase):
    id: int


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str


class SubcategoryBase(SQLModel):
    name: str
    category_id: int = Field(foreign_key="category.id")


class Subcategory(SubcategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="subcategory")
    category: Category = Relationship(back_populates="subcategories")


class SubcategoryRead(SubcategoryBase):
    id: int
    name: str


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(SubcategoryBase):
    name: Optional[str] = None
    category_id: Optional[int] = None


class ItemBase(SQLModel):
    name: str
    image_url: Optional[str] = Field(default=None)
    category_id: int = Field(..., foreign_key="category.id")
    subcategory_id: Optional[int] = Field(default=None, foreign_key="subcategory.id")
    description: Optional[str] = None
    color: Optional[str] = None
    save_color: Optional[str] = None


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attributes: List[Attribute] = Relationship(
        back_populates="items", link_model=ItemAttributeLink
    )
    outfits: List["Outfit"] = Relationship(
        back_populates="items", link_model=OutfitItemLink
    )
    category: Category = Relationship(back_populates="items")
    subcategory: Optional[Subcategory] = Relationship(back_populates="items")


class ItemRead(ItemBase):
    id: int
    attributes: List[AttributeRead] = []
    category: CategoryRead
    subcategory: Optional[SubcategoryRead] = None


class ItemCreate(ItemBase):
    name: str
    image_url: str
    category_id: int
    subcategory_id: Optional[int] = None
    description: Optional[str] = None


class ItemUpdate(ItemBase):
    name: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    description: Optional[str] = None


# outfit model
class OutfitBase(SQLModel):
    pass


class Outfit(OutfitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(
        back_populates="outfits", link_model=OutfitItemLink
    )


class OutfitRead(OutfitBase):
    id: int
    items: List[ItemRead] = []


class OutfitCreate(OutfitBase):
    item_ids: List[int]


class OutfitUpdate(OutfitBase):
    name: str


class OutfitDelete(OutfitBase):
    name: str


class MyImageBase(SQLModel):
    user_id: int
    image_url: str


class MyImage(MyImageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MyImageRead(MyImageBase):
    id: int


class MyImageCreate(MyImageBase):
    pass


class MyImageUpdate(MyImageBase):
    user_id: Optional[int] = None
    image_url: Optional[str] = None
