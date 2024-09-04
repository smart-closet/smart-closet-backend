import uuid
from fastapi import File, HTTPException
import requests
import base64
import csv
import os
import json
from dotenv import load_dotenv
from firebase_admin import storage


load_dotenv()
api_key = os.getenv("API_KEY")

def get_item_info(image_url: str) -> dict:
    response = requests.get(image_url)
    response.raise_for_status()
    image_base64_string = base64.b64encode(response.content).decode("utf-8")

    # 讀取 subcategory.csv 文件
    subcategories = []
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategories.append(row['value'])

    attributes = []
    with open('tools/attribute.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attributes.append(row['value'])

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""Based on the image, analyze the clothing item and provide the following information in JSON format:
1. Check the item is a top, bottom. Top return 1, bottom return 2.
1. Pick a suitable subcategory from the following list: {', '.join(subcategories)}
2. Describe the appearance, material, and texture of the clothing.
3. Pick multiple attribute from the following list: {', '.join(attributes)}

Return the information in the following JSON format:
{{
    "category_id": "Top(1) or Bottom(2)",
    "subcategory": "Selected subcategory",
    "description": "Detailed description of appearance, material, and texture",
    "attribute": ["Selected attribute 1", "Selected attribute 2", ...]
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
    item_info['attributes'] = " ".join(item_info['attribute'])


    return item_info

async def upload_image(file: File, name: str) -> str:
    bucket = storage.bucket()
        
    # Create a blob in Firebase Storage
    blob = bucket.blob(f"items/{uuid.uuid4()}-{name}-{file.filename}")

     # Upload the file contents
    blob.upload_from_string(
        await file.read(),
        content_type=file.content_type
    )

    blob.make_public()

    return blob.public_url