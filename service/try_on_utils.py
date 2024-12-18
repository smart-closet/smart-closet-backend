import os

# import time
from dotenv import load_dotenv
import base64
import aiohttp
import requests

load_dotenv()
api_key = os.getenv("VIRTUAL_TRY_ON_API_KEY")
api_url = "https://api.segmind.com/v1/idm-vton"


async def send_request(data, api_url, api_key):
    try:
        async with aiohttp.ClientSession() as session:
            print(api_key)
            async with session.post(
                api_url, json=data, headers={"x-api-key": api_key}
            ) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type")
                    if "image" in content_type:
                        image_data = await response.read()
                        image_base64 = base64.b64encode(image_data).decode("utf-8")

                        image_binary = base64.b64decode(image_base64)
                        timestamp = 2345678
                        file_path = f"output_image_{timestamp}.jpg"
                        with open(file_path, "wb") as f:
                            f.write(image_binary)

                        return image_base64
                    else:
                        print(f"Unexpected content type: {content_type}")
                        print(await response.text())
                else:
                    print(f"Error: {response.status}")
                    print(await response.text())

    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")


# mode can be upper_body, lower_body and dresses
def construct_data(human_url: str, cloth_url: str, mode="upper_body"):
    human_url_str = str(human_url)
    cloth_url_str = str(cloth_url)

    try:
        # 處理 human_url
        if human_url_str.startswith("http://") or human_url_str.startswith("https://"):
            response_human = requests.get(human_url_str)
            response_human.raise_for_status()  # 這將引發 HTTPError
            if not response_human.content:
                raise ValueError("Human image content is empty.")

            human_base64 = base64.b64encode(response_human.content).decode("utf-8")
        else:
            human_base64 = human_url_str

        # 處理 cloth_url
        if cloth_url_str.startswith("http://") or cloth_url_str.startswith("https://"):
            response_cloth = requests.get(cloth_url_str)
            response_cloth.raise_for_status()
            if not response_cloth.content:
                raise ValueError("Cloth image content is empty.")

            cloth_base64 = base64.b64encode(response_cloth.content).decode("utf-8")
        else:
            cloth_base64 = cloth_url_str

        # 確保 base64 資料不為 None
        if human_base64 is None or cloth_base64 is None:
            raise ValueError("Failed to encode images as base64 strings.")

    except requests.RequestException as e:
        print(f"Error fetching image from URL: {e}")
        return None  # 或者返回一個錯誤信息

    data = {
        "crop": False,
        "seed": 42,
        "steps": 30,
        "category": mode,
        "force_dc": False,
        "human_img": human_base64,
        "garm_img": cloth_base64,
        "mask_only": False,
        "garment_des": "Green colour semi Formal Blazer",
    }
    return data