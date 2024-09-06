import os
from dotenv import load_dotenv
import base64
import aiohttp
import requests
from pydantic import AnyUrl

load_dotenv()
api_key = os.getenv("VIRTUAL_TRY_ON_API_KEY")
api_url = "https://api.segmind.com/v1/idm-vton"

async def send_request(data, api_url, api_key):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url, json=data, headers={"x-api-key": api_key}
            ) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type")
                    if "image" in content_type:
                        image_data = await response.read()

                        image_base64 = base64.b64encode(image_data).decode("utf-8")
                        # image_binary = base64.b64decode(image_base64)
                        # timestamp = int(time.time())
                        # file_path = f"output_image_{timestamp}.jpg"
                        # with open(file_path, "wb") as f:
                        #     f.write(image_binary)

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
def construct_data(human_url: AnyUrl, cloth_url: AnyUrl, mode="upper_body"):
    human_url_str = str(human_url)
    cloth_url_str = str(cloth_url)

    if human_url_str.startswith("http://") or human_url_str.startswith("https://"):
        response_human = requests.get(human_url_str)
        response_human.raise_for_status()
        human_base64 = base64.b64encode(response_human.content).decode("utf-8")
    else:
        human_base64 = human_url_str

    response_cloth = requests.get(cloth_url_str)
    response_cloth.raise_for_status()
    cloth_base64 = base64.b64encode(response_cloth.content).decode("utf-8")

    data = {
        "crop": False,
        "seed": 42,
        "steps": 30,
        "category": mode,
        "force_dc": False,
        "human_img": human_base64,
        "garm_img": cloth_base64,
        "mask_only": False,
        "garment_des": "Green colour semi Formal Blazer"
    }
    return data
