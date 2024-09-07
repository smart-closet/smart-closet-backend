from io import BytesIO
import uuid
import cv2
from fastapi import UploadFile
import numpy as np
import csv
import os
import json
from dotenv import load_dotenv
from firebase_admin import storage
from PIL import Image
from inference_sdk import InferenceHTTPClient
import supervision as sv
import google.generativeai as genai


load_dotenv()
api_key = os.getenv("API_KEY")
df2_api_key = os.getenv("DF2_API_KEY")


async def get_item_info(image: UploadFile) -> dict:
    # 讀取 subcategory.csv 文件
    subcategories = []
    with open("tools/subcategory.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategories.append(row["value"])

    attributes = []
    with open("tools/attribute.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attributes.append(row["value"])

    # 使用 Gemini API 進行圖片分析
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
    )
    prompt = f"""response_mime_type: application/json
Based on the image, analyze the clothing item and provide the following information in JSON format:
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
    response = model.generate_content(
        [
            prompt,
            Image.open(image.file)
        ]
    )
    
    item_info = json.loads(response.text)
    item_info["subcategory_id"] = subcategories.index(item_info["subcategory"]) + 1
    item_info["attributes"] = " ".join(item_info["attribute"])

    return item_info


async def upload_image(file: UploadFile, name: str) -> str:
    bucket = storage.bucket()

    # Create a blob in Firebase Storage
    blob = bucket.blob(f"items/{uuid.uuid4()}-{name}-{file.filename}")

    # Upload the file contents
    blob.upload_from_string(await file.read(), content_type="image/png")
    blob.make_public()

    return blob.public_url


async def split_image(image: UploadFile) -> UploadFile:
    def maximize_non_transparent_area(image):
        # 確保圖片是 RGBA 格式
        image = image.convert("RGBA")

        # 找到非透明區域的邊界
        min_x, min_y, max_x, max_y = image.width, image.height, 0, 0
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = image.getpixel((x, y))
                if a != 0:  # 非透明部分
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        # 裁切出非透明區域
        cropped_image = image.crop((min_x, min_y, max_x + 1, max_y + 1))

        # 將裁切後的圖片放大到原始圖片的大小
        enlarged_image = cropped_image.resize(image.size, Image.LANCZOS)

        return enlarged_image

    model = InferenceHTTPClient(
        api_url="https://detect.roboflow.com", api_key=df2_api_key
    )

    file_bytes = np.frombuffer(await image.read(), np.uint8)
    cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    results = model.infer(cv_image, model_id="deepfashion2-m-10k/2")
    detections = sv.Detections.from_inference(results)

    items = []
    for i, mask in enumerate(detections.mask):
        mask = mask.astype("uint8") * 255
        clean_clothing_region = cv2.bitwise_and(cv_image, cv_image, mask=mask)
        clean_clothing_region_pil = Image.fromarray(
            cv2.cvtColor(clean_clothing_region, cv2.COLOR_BGR2RGB)
        )
        clean_clothing_region_pil = clean_clothing_region_pil.convert("RGBA")

        data = clean_clothing_region_pil.getdata()
        new_data = []
        for item in data:
            if (
                item[0] == 0 and item[1] == 0 and item[2] == 0
            ):  # Adjust this condition if necessary
                new_data.append((256, 256, 256, 0))  # Transparent
            else:
                new_data.append((item[0], item[1], item[2], 255))  # Fully opaque
        clean_clothing_region_pil.putdata(new_data)
        clean_clothing_region_pil = maximize_non_transparent_area(
            clean_clothing_region_pil
        )

        image_bytes = BytesIO()
        clean_clothing_region_pil.save(image_bytes, format="PNG")
        # clean_clothing_region_pil.save(f"clean_clothing_region_{i}.png")
        image_bytes.seek(0)
        items.append(UploadFile(filename=f"{image.filename}_{i}", file=image_bytes))

    return items
