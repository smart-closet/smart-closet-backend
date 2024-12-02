import asyncio
import time
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from PIL import Image
import numpy as np

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
from service.item_utils import get_item_info, split_image, upload_images
from concurrent.futures import ThreadPoolExecutor
from api.models.Color_FSM_model import identify_color

router = APIRouter()

def print_time_taken(start, message):
    print(f"{message}: Time taken: {time.time() - start}")

# Item endpoints
@router.post("/", response_model=List[ItemRead])
async def create_item(
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    total_time_start = time.time()

    start = time.time()
    images = await split_image(image)
    print_time_taken(start, "Splitting image")

    start = time.time()
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        image_urls_future = loop.run_in_executor(executor, lambda: asyncio.run(upload_images(images)))
        item_infos_future = loop.run_in_executor(executor, lambda: asyncio.run(get_item_info(images, len(images))))

        item_infos = await item_infos_future
        image_urls = await image_urls_future
    print_time_taken(start, "Getting item info & Uploading Images")

    items = []
    start = time.time()

    for idx, image in enumerate(images):
        item_info = item_infos[idx]

        db_item = Item(
            name=item_info["name"],
            image_url=image_urls[idx],
            category_id=item_info["category_id"],
            subcategory_id=item_info["subcategory_id"],
            description=item_info["description"],
            color = item_info["color"],
            save_color = item_info["save_color"]
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

    print_time_taken(start, "Inserting items")
    print(f"Time taken: {time.time() - total_time_start}")
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
