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


async def get_item_info(images: list[UploadFile], item_count: int) -> dict:
    print("start info")
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
        "gemini-1.5-pro", generation_config={"response_mime_type": "application/json"}
    )
    prompt = f"""

    Based on the image, analyze the clothing items and provide the following information in JSON format:
    1. give it a name based on the appearance of the clothing.
    2. Check the item is a top, bottom. Top return 1, bottom return 2.
    3. Pick a suitable subcategory id base on the name and description from the following list: {', '.join(subcategories)} and return its order in the list count from 1.
    4. Describe the appearance, material, and texture of the clothing.
    5. Pick multiple attribute (top5) from the following list: {', '.join(attributes)} and return their index + 1.

    Return the information in the following JSON format for {item_count} items:
    {[{
        "name": "Name of the clothing item",
        "category_id": "Top(1) or Bottom(2)",
        "subcategory_id": f"Pick a suitable subcategory id base on the image and these subcategories from the following list: {', '.join(subcategories)} and return its order in the list count from 1.",
        "description": "Detailed description of appearance, material, and texture",
        "attribute_ids": ["attribute_id 1", "attribute_id 2", ...]
    }, ...]}

    check twice for the subcategory_id and attribute_ids, make sure they are in the correct order and suitable with a the name and description.
    be careful with jeans and skirt they are both bottoms but have different subcategory_id.
    """

    content = [prompt]
    content.extend([Image.open(img.file) for img in images])
    response = model.generate_content(content)
    item_infos = json.loads(response.text)
    print(item_infos)
    print("end info")
    return item_infos


async def upload_images(files: list[UploadFile]) -> list[str]:
    print("start image")
    bucket = storage.bucket()
    public_urls = []
    for file in files:
        blob = bucket.blob(f"items/{uuid.uuid4()}")
        file.file.seek(0)
        file = BytesIO(await file.read())
        blob.upload_from_file(file, content_type="image/png")
        blob.make_public()
        public_urls.append(blob.public_url)
    print("end image")

    return public_urls


async def split_image(image: UploadFile) -> list[UploadFile]:
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
        cropped_image = image.crop((min_x - 100, min_y - 100, max_x + 100, max_y + 100))

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

    def calculate_mask_iou(mask1, mask2):
        intersection = np.logical_and(mask1, mask2)
        union = np.logical_or(mask1, mask2)
        intersection_area = np.sum(intersection)
        union_area = np.sum(union)
        if union_area == 0:
            return 0
        
        iou = intersection_area / union_area
        return iou
    
    items = []
    items_mask = []
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
        #items.append(UploadFile(filename=f"{image.filename}_{i}", file=image_bytes))

        # 避免超相似的 items
        keep = True
        for i, stored_mask in enumerate(items_mask):
            iou = calculate_mask_iou(mask, stored_mask)
            if iou > 0.7:
                keep = False
        if(keep):
            items.append(UploadFile(filename=f"{image.filename}_{i}", file=image_bytes)) # 確定新增 item
            items_mask.append(mask)

    return items
