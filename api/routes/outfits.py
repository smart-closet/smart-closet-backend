from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Outfit, OutfitCreate, OutfitRead, OutfitUpdate, Item
from db import get_session

router = APIRouter()

# Outfit endpoints
@router.post("/", response_model=OutfitRead)
def create_outfit(outfit: OutfitCreate, session: Session = Depends(get_session)):
    db_outfit = Outfit(name=outfit.name)
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    return db_outfit


@router.get("/", response_model=List[OutfitRead])
def read_outfits(session: Session = Depends(get_session)):
    outfits = session.exec(select(Outfit)).all()
    return outfits


@router.get("/{outfit_id}", response_model=OutfitRead)
def read_outfit(outfit_id: int, session: Session = Depends(get_session)):
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return outfit


@router.put("/{outfit_id}", response_model=OutfitRead)
def update_outfit(outfit_id: int, outfit: OutfitUpdate, session: Session = Depends(get_session)):
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db_outfit.name = outfit.name
    session.commit()
    session.refresh(db_outfit)
    return db_outfit

@router.delete("/{outfit_id}", response_model=OutfitRead)
def delete_outfit(outfit_id: int, session: Session = Depends(get_session)):
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    session.delete(outfit)
    session.commit()
    return outfit

@router.post("/{outfit_id}/items/{item_id}", response_model=OutfitRead)
def add_item_to_outfit(outfit_id: int, item_id: int, session: Session = Depends(get_session)):
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item in db_outfit.items:
        raise HTTPException(status_code=400, detail="Item is already associated with this outfit")

    db_outfit.items.append(db_item)
    session.commit()
    session.refresh(db_outfit)
    return db_outfit

@router.delete("/{outfit_id}/items/{item_id}", response_model=OutfitRead)
def remove_item_from_outfit(outfit_id: int, item_id: int, session: Session = Depends(get_session)):
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item not in db_outfit.items:
        raise HTTPException(status_code=400, detail="Item is not associated with this outfit")

    db_outfit.items.remove(db_item)
    session.commit()
    session.refresh(db_outfit)
    return db_outfit