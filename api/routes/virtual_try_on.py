from typing import List
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os

from pydantic import AnyUrl, BaseModel
from service.virtual_try_on_utils import send_request, construct_data

router = APIRouter()

load_dotenv()
api_key = os.getenv("VIRTUAL_TRY_ON_API_KEY")
api_url = "https://api.segmind.com/v1/idm-vton"


class ImageURLsRequest(BaseModel):
    urls: List[AnyUrl]  # List of URLs of images to be processed

    
@router.post("/process-images/")
async def process_images(request: ImageURLsRequest, response_model=str):
    for url in request.urls:
        print(f"Received URL: {url}")
    try:
        if len(request.urls) == 2:
            print("Processing 2 images")
            data = construct_data(request.urls[0], request.urls[1], "dresses")
            result = await send_request(data, api_url, api_key)
            return {"result": result}
        elif len(request.urls) == 3:
            print("Processing 3 images")
            data = construct_data(
                request.urls[0], request.urls[1], mode="upper_body")
            first_result = await send_request(data, api_url, api_key)
            print("First result received")
            second_data = construct_data(
                first_result, request.urls[2], mode="lower_body")
            final_result = await send_request(second_data, api_url, api_key)
            print("Second result received")
            return {"result": final_result}
        else:
            raise HTTPException(
                status_code=400, detail="Invalid number of images.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
