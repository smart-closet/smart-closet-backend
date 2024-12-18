﻿from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlmodel import select
from models import Item
from db import get_session
from service.rule_base_utils import (
    get_rule_base_criteria,
    get_scenario_criteria,
    get_subcategory_ids,
)
from service.rank_utils import rank

router = APIRouter()


class RuleBaseFilterRequest(BaseModel):
    temperature: float
    consider_weather: bool = True
    user_occasion: Optional[str] = None
    personal_temp: Optional[int] = 0
    item_id: Optional[int] = None
    voice_occasion: Optional[str] = ""


@router.post("/", response_model=List[dict])
def ruleBase_filter(
    request: RuleBaseFilterRequest,
    session: Session = Depends(get_session),
):
    if len(request.voice_occasion) == 0:
        filter_criteria = get_rule_base_criteria(
            request.temperature, request.consider_weather, request.user_occasion
        )
    else:
        filter_criteria = get_scenario_criteria(request.voice_occasion)

    subcategory_ids = get_subcategory_ids(filter_criteria)
    

    # 查詢符合條件的項目
    items = session.exec(
        select(Item)
        .where(Item.category_id.in_([1, 2]))
        .where(Item.subcategory_id.in_(subcategory_ids))
    ).all()

    top, bottom = [
        [item.dict() for item in items if item.category_id == 1],
        [item.dict() for item in items if item.category_id == 2],
    ]

    if request.item_id:
        selected_item: Item = session.get(Item, request.item_id).model_dump()
        if selected_item["category_id"] == 1:
            top = [selected_item]
        elif selected_item["category_id"] == 2:
            bottom = [selected_item]

    ranked_results = rank(top, bottom)

    return ranked_results
