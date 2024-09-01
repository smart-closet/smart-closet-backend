from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlmodel import select
from models import Item, RuleBaseFilterRequest
from db import get_session
from service.rule_base_filter import rule_base_filter
from service.rank import rank
import csv

router = APIRouter()

# 讀取 subcategory.csv 文件並創建一個名稱到 ID 的映射
def load_subcategory_mapping():
    subcategory_mapping = {}
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategory_mapping[row['value']] = int(row['id'])
    return subcategory_mapping

subcategory_mapping = load_subcategory_mapping()

@router.post("/", response_model=List[dict])
def ruleBase_filter(
    request: RuleBaseFilterRequest,
    session: Session = Depends(get_session),
):
    filter_criteria = rule_base_filter(
        request.city,
        request.place,
        request.consider_weather,
        request.user_occation,
    )[0]
    
    # 將子類別名稱轉換為 ID
    subcategory_ids = [subcategory_mapping.get(name) for name in filter_criteria['subcategories']]
    subcategory_ids = [id for id in subcategory_ids if id is not None]
    
    # 查詢符合條件的項目
    items = session.exec(
        select(Item)
        .where(Item.category_id.in_([1, 2]))
        .where(Item.subcategory_id.in_(subcategory_ids))
    ).all()

    print(items, subcategory_ids)    
    
    # 過濾 category_id 為 1 和 2 的項目
    top = [item.dict() for item in items if item.category_id == 1]
    bottom = [item.dict() for item in items if item.category_id == 2]

    # 使用 rank 函數
    ranked_results = rank(top, bottom)

    return ranked_results