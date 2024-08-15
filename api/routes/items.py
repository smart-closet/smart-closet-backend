from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Item, ItemCreate, ItemRead, ItemUpdate, Attribute

from db import get_session


router = APIRouter()


# Item endpoints
@router.post("/", response_model=ItemRead)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item(name=item.name, image_url=item.image_url)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/", response_model=List[ItemRead])
def read_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int, item: ItemUpdate, session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.image_url = item.image_url

    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}", response_model=ItemRead)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return item

# Item Attributes endpoints

@router.delete(
    "/{item_id}/attributes/{attribute_id}",
    response_model=ItemRead,
)
def remove_attribute_from_item(
    item_id: int, attribute_id: int, session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_attribute = session.get(Attribute, attribute_id)
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    if db_attribute not in db_item.attributes:
        raise HTTPException(
            status_code=400, detail="Attribute is not associated with this item"
        )

    db_item.attributes.remove(db_attribute)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.post(
    "/{item_id}/attributes/{attribute_id}",
    response_model=ItemRead,
)
def add_attribute_to_item(
    item_id: int, attribute_id: int, session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_attribute = session.get(Attribute, attribute_id)
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    if db_attribute in db_item.attributes:
        raise HTTPException(
            status_code=400, detail="Attribute is already associated with this item"
        )

    db_item.attributes.append(db_attribute)
    session.commit()
    session.refresh(db_item)
    return db_item
