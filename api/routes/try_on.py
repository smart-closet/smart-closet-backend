from typing import Optional
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os

from sqlmodel import SQLModel
from service.try_on_utils import send_request, construct_data

router = APIRouter()

load_dotenv()
api_key = os.getenv("VIRTUAL_TRY_ON_API_KEY")
api_url = "https://api.segmind.com/v1/idm-vton"

class try_on_request(SQLModel):
    human_url: str
    top_url: Optional[str] = ""
    bottom_url: Optional[str] = ""

@router.post("/")
async def process_images(request: try_on_request):
    for url in request:
        print("received url: ", url, "\n")
    try:
        if request.top_url == "" and request.bottom_url == "":
            raise HTTPException(status_code=400, detail="Invalid number of images.")
        
        elif request.top_url is not None and request.bottom_url == "":
            print("generating upper body image")
            data = construct_data(request.human_url, request.top_url, "upper_body")
            result = await send_request(data, api_url, api_key)
            return {"result": result}
        
        elif request.bottom_url is not None and request.top_url == "":
            print("generating lower body image")
            data = construct_data(request.human_url, request.bottom_url, "lower_body")
            result = await send_request(data, api_url, api_key)
            return {"result": result}
        
        else:
            print("generating full body image")
            data = construct_data(request.human_url, request.top_url, "upper_body")
            first_result = await send_request(data, api_url, api_key)
            second_data = construct_data(first_result, request.bottom_url, "lower_body")
            final_result = await send_request(second_data, api_url, api_key)
            return {"result": final_result}
    
    except Exception as e:
        print("Error: ", e)
        
