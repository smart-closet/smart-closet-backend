from fastapi import HTTPException
import requests
import base64
import csv

import os
from models import Item
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

def get_item_subcategory_id(item: Item) -> int:
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
                        "text": f"Based on the image, pick a suitable subcategory from the following list: {', '.join(subcategories)}"
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
    response.raise_for_status()  # 確保 HTTP 請求成功

    subcategory_name = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    # 從 CSV 文件中查找子類別 ID
    subcategory_id = None
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['value'] == subcategory_name:
                subcategory_id = int(row['id'])
                break

    if subcategory_id is None:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    return subcategory_id

def get_item_description(item: Item) -> str:
    response = requests.get(item.image_url)
    response.raise_for_status()
    image_base64_string = base64.b64encode(response.content).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Based on the picture of clothing, describe the appearance, material and texture of the clothing respectively. Do you think this outfit belongs to European and American style, Korean style or Japanese style?"
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
    response.raise_for_status()  # 確保 HTTP 請求成功

    description = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    return description
