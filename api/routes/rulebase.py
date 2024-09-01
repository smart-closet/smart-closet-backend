from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Item, ItemRead, RuleBaseFilterRequest
from db import get_session
from service.rule_base_filter import rule_base_filter
from service.rank import rank

router = APIRouter()


@router.post("/", response_model=List[ItemRead])  # 定義用outfiread 的格式回傳 api
def ruleBase_filter(
    request: RuleBaseFilterRequest,
    session: Session = Depends(get_session),  # 添加這行
):
    result = rule_base_filter(
        request.city,
        request.place,
        request.consider_weather,
        request.user_occation,
        request.personal_temp,
    )
    print("check:::::", result)  ##有成功調用 rule_base 產生出正確的 attribute
    items = session.exec(select(Item)).all()

    # 過濾 category_id 為 1 和 2 的項目
    top = [item.dict() for item in items if item.category.id == 1]
    bottom = [item.dict() for item in items if item.category.id == 2]

    # 使用 rank 函數
    ranked_results = rank(top, bottom)
    print("check:::::", ranked_results)  ##有成功調用 rank 產生出正確的 attribute

    return items  # 確保這裡返回 ranked_results，而不是 items