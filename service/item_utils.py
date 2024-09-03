from fastapi import HTTPException
import requests
import base64
import csv
import os
import json
from models import Item
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

def get_item_info(item: Item) -> dict:
    response = requests.get(item.image_url)
    response.raise_for_status()
    image_base64_string = base64.b64encode(response.content).decode("utf-8")

    # 讀取 subcategory.csv 文件
    subcategories = []
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategories.append(row['value'])

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""Based on the image, analyze the clothing item and provide the following information in JSON format:
1. Pick a suitable subcategory from the following list: {', '.join(subcategories)}
2. Describe the appearance, material, and texture of the clothing.
3. Determine if this outfit belongs to European and American style, Korean style, or Japanese style.

Return the information in the following JSON format:
{{
    "subcategory": "Selected subcategory",
    "description": "Detailed description of appearance, material, and texture",
    "style": "European and American / Korean / Japanese"
}}"""
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64_string,
                        }
                    },
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    item_info = json.loads(result)

    # 從 CSV 文件中查找子類別 ID
    subcategory_id = None
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['value'] == item_info['subcategory']:
                subcategory_id = int(row['id'])
                break

    if subcategory_id is None:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    item_info['subcategory_id'] = subcategory_id
    return item_info

def get_item_subcategory_id(item: Item) -> int:
    subcategory_id, _ = get_item_info(item)
    return subcategory_id

def get_item_description(item: Item) -> str:
    _, description = get_item_info(item)
    return description
