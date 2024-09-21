import time
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import (
    Item,
    ItemAttributeLink,
    ItemRead,
    ItemUpdate,
    Attribute,
    Category,
)

from db import get_session
from service.item_utils import get_item_info, upload_image, split_image

router = APIRouter()

def print_time_taken(start, message):
    print(f"{message}: Time taken: {time.time() - start}")
    start = time.time()


# Item endpoints
@router.post("/", response_model=List[ItemRead])
async def create_item(
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    start = time.time()
    images = await split_image(image)
    print_time_taken(start, "Splitting image")
    items = []
    item_infos = await get_item_info(images, len(images))
    print_time_taken(start, "Getting item info")

    for idx, image in enumerate(images):
        item_info = item_infos[idx]
        image_url = await upload_image(image)

        db_item = Item(
            name=item_info["name"],
            image_url=image_url,
            category_id=item_info["category_id"],
            subcategory_id=item_info["subcategory_id"],
            description=item_info["description"],
        )
        session.add(db_item)
        session.flush()
        items.append(db_item)

        new_links = [
            ItemAttributeLink(item_id=db_item.id, attribute_id=attribute_id)
            for attribute_id in item_info["attribute_ids"]
        ]

        session.add_all(new_links)

    session.commit()
    print(f"Time taken: {time.time() - start}")
    return items


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

    if item.category_id is not None:
        category = session.get(Category, item.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    db_item.name = item.name
    db_item.image_url = item.image_url
    if item.category_id is not None:
        db_item.category_id = item.category_id

    session.commit()
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
