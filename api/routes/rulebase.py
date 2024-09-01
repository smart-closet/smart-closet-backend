from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Item, ItemRead, RuleBaseFilterRequest
from db import get_session
from service.rule_base_filter import rule_base_filter

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

    return items