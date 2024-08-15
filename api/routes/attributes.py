from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Attribute, AttributeCreate, AttributeRead
from db import get_session

router = APIRouter()

# Attribute endpoints
@router.post("/", response_model=AttributeRead)
def create_attribute(
    attribute: AttributeCreate, session: Session = Depends(get_session)
):
    db_attribute = Attribute(name=attribute.name, value=attribute.value)
    session.add(db_attribute)
    session.commit()
    session.refresh(db_attribute)
    return db_attribute


@router.get("/", response_model=List[AttributeRead])
def read_attributes(session: Session = Depends(get_session)):
    attributes = session.exec(select(Attribute)).all()
    return attributes


@router.get("/{attribute_id}", response_model=AttributeRead)
def read_attribute(attribute_id: int, session: Session = Depends(get_session)):
    attribute = session.get(Attribute, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute


@router.put("/{attribute_id}", response_model=AttributeRead)
def update_attribute(
    attribute_id: int,
    attribute: AttributeCreate,
    session: Session = Depends(get_session),
):
    db_attribute = session.get(Attribute, attribute_id)
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    db_attribute.name = attribute.name
    db_attribute.value = attribute.value

    session.commit()
    session.refresh(db_attribute)
    return db_attribute


@router.delete("/{attribute_id}", response_model=AttributeRead)
def delete_attribute(attribute_id: int, session: Session = Depends(get_session)):
    attribute = session.get(Attribute, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    session.delete(attribute)
    session.commit()
    return attribute