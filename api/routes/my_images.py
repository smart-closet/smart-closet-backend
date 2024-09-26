from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlmodel import select

from db import get_session
from models import MyImage, MyImageRead, MyImageUpdate
from service.item_utils import upload_images

router = APIRouter()

# MyImage endpoints

@router.post("/", response_model=MyImageRead)
async def create_my_image(
    image: UploadFile = File(...), session: Session = Depends(get_session)
):
    image_url = upload_images([image])[0]
    db_my_image = MyImage(user_id=1, image_url=image_url)
    session.add(db_my_image)
    session.commit()
    session.refresh(db_my_image)
    return db_my_image


@router.get("/", response_model=List[MyImageRead])
def read_my_images(session: Session = Depends(get_session)):
    my_images = session.exec(select(MyImage)).all()
    return my_images


@router.get("/{my_image_id}", response_model=MyImageRead)
def read_my_image(my_image_id: int, session: Session = Depends(get_session)):
    my_image = session.get(MyImage, my_image_id)
    if not my_image:
        raise HTTPException(status_code=404, detail="MyImage not found")
    return my_image


@router.put("/{my_image_id}", response_model=MyImageRead)
def update_my_image(
    my_image_id: int, my_image: MyImageUpdate, session: Session = Depends(get_session)
):
    db_my_image = session.get(MyImage, my_image_id)
    if not db_my_image:
        raise HTTPException(status_code=404, detail="MyImage not found")

    db_my_image.user_id = my_image.user_id
    db_my_image.image_url = my_image.image_url

    session.commit()
    session.refresh(db_my_image)
    return db_my_image


@router.delete("/{my_image_id}", response_model=MyImageRead)
def delete_my_image(my_image_id: int, session: Session = Depends(get_session)):
    my_image = session.get(MyImage, my_image_id)
    if not my_image:
        raise HTTPException(status_code=404, detail="MyImage not found")
    session.delete(my_image)
    session.commit()
    return my_image
