import csv
import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
df2_api_key = os.getenv("DF2_API_KEY")


def load_subcategory_mapping():
    subcategory_mapping = {}
    with open("tools/subcategory.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subcategory_mapping[row["value"]] = int(row["id"])
    return subcategory_mapping


def split_clothing_dict(data):
    # Initialize list of dictionaries to hold the split data
    split_data = []

    # Loop over the indices to create separate dictionaries
    for i in range(0, len(data["body_temp"])):
        # Create a new dictionary for each temperature
        temp_dict = {
            "body_temp": data["body_temp"][i],
            "material": data["material"][i],
            "subcategories": data["subcategories"][i],
            "outer_layer": data["outer_layer"][i],
        }
        split_data.append(temp_dict)

    return split_data


def weather_rule_base(temperature, personal_temp=0):
    body_temp = int(temperature - personal_temp)

    candidate_cloth_type = []
    final_recommend = {
        "body_temp": [],
        "material": [],
        "subcategories": [],
        "outer_layer": [],
        "Note": [],
    }

    # 所有溫度皆適合的服飾 及和溫度無關的材質(花紋)
    all_temp_cloth = [
        "pants",
        "cotton-pants",
        "sweatpants",
        "long-skirt",
        "jeans",
        "jumpsuit",
        "overalls",
        "leggings",
        "sweatpants",
    ]
    clothe_type = {
        1: [
            "tank-top",
            "dress",
            "skirt",
            "shorts",
            "t-shirt",
            "shirt",
            "polo-shirt",
            "tank-top",
            "suit-pants",
            "sheer",
            "yoga-pants",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
        ],
        2: [
            "dress",
            "skirt",
            "shorts",
            "t-shirt",
            "shirt",
            "polo-shirt",
            "knit-top",
            "suit-pants",
            "yoga-pants",
            "sheer",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
        ],
        3: ["dress", "pants", "shorts", "suit-pants", "yoga-pants", "overalls"],
        4: ["long-sleeve button-up shirt", "hoodie", "long-sleeve-shirt"],
        5: [
            "long-sleeve flannel-shirt",
            "long-sleeve button-up shirt",
            "hoodie",
            "turtleneck",
            "long-sleeve-shirt",
        ],
        6: [
            "sweater",
            "hoodie",
            "turtleneck",
            "college-sweatshirt",
            "long-sleeve-shirt",
        ],
        7: [
            "sweater",
            "hoodie",
            "turtleneck",
            "wool-pants",
            "windproof-pants",
            "college-sweatshirt",
            "long-sleeve-shirt",
        ],
        8: [
            "sweater",
            "hoodie",
            "turtleneck",
            "wool-pants",
            "windproof-pants",
            "college-sweatshirt",
        ],
    }
    # 不同等級的外套
    outer_layer = {
        0: ["vest", "cotton-vest"],
        1: ["sweater-vest", "jacket", "suit-jacket", "denim-jacket"],
        2: [
            "insulated-vest",
            "leather-jacket",
            "coat",
            "trench-coat",
            "cotton-coat",
            "padded-jacket",
            "down-jacket",
        ],
        3: ["padded-jacket", "down-jacket", "ski-jacket", "winter-sportswear"],
    }
    # 材質分為三種，透氣0，中性1，保暖2
    fabric_type = {
        0: ["cotton", "linen", "linen-blend", "satin", "denim", "chiffon"],
        1: ["cotton", "knit", "nylon", "faux-suede", "chiffon"],
        2: ["velvet", "cotton", "woven", "crochet", "faux-fur", "faux-leather"],
    }

    # 如果是極端熱的情況 -> 材質選:透氣，服裝種類選:1度C
    if body_temp >= 27:
        candidate_cloth_type += list(set(clothe_type[1] + clothe_type[2]))
        final_recommend["body_temp"].append(body_temp)
        final_recommend["material"].extend(fabric_type[0])
        final_recommend["subcategories"].extend(candidate_cloth_type)
    # 如果是極端冷的情況 -> 材質選:保暖, 服裝種類選 7~8 度C, 建議洋蔥式穿搭
    elif body_temp <= 13:
        if body_temp <= 5:  # 霸王寒流級(建議洋蔥式穿搭)
            candidate_cloth_type += list(set(clothe_type[7] + clothe_type[8]))
            final_recommend["outer_layer"].extend(outer_layer[3])
            final_recommend["Note"].append("thermal-underwear")
        else:  # 小冬天
            candidate_cloth_type += list(set(clothe_type[6] + clothe_type[7]))
            final_recommend["outer_layer"].extend(outer_layer[2])

        final_recommend["body_temp"].append(body_temp)
        final_recommend["material"].extend(fabric_type[2])
        final_recommend["subcategories"].extend(candidate_cloth_type)

    # 正常情況
    else:
        # 比較偏熱的情況下(22~26)，材質的選擇於0-2度C,間度1度C
        temp_rang = [body_temp + 2, body_temp, body_temp - 2]
        for temp in temp_rang:
            final_recommend["body_temp"].append(temp)
            target = max(1, min(25 - temp, 5))
            if temp >= 26:
                final_recommend["material"].append(fabric_type[0])
                final_recommend["subcategories"].append(clothe_type[1])
                final_recommend["outer_layer"].append([])
            elif temp >= 21:  # 類型適合[1,2,3]
                final_recommend["material"].append(fabric_type[0])
                final_recommend["subcategories"].append(clothe_type[target])
                final_recommend["outer_layer"].append(outer_layer[0])
            elif temp >= 14:
                final_recommend["material"].append(fabric_type[2])  # 不確定要不要加0
                final_recommend["subcategories"].append(clothe_type[target])
                final_recommend["outer_layer"].append(outer_layer[1])
            else:
                final_recommend["material"].append(fabric_type[2])  # 不確定要不要加
                final_recommend["subcategories"].append(clothe_type[8])
                final_recommend["outer_layer"].append(outer_layer[2])

    if len(final_recommend["body_temp"]) >= 2:
        # print("ok")
        for i in final_recommend["subcategories"]:
            i.extend(all_temp_cloth)
        final_recommend = split_clothing_dict(final_recommend)
    else:
        final_recommend["subcategories"].extend(all_temp_cloth)
        final_recommend = [final_recommend]
    return final_recommend


# 場合篩選
def occasion_filter(user_occasion):
    data = {
        "occasion": [],
        "pattern": [],
        "material": [],
        "subcategories": [],
        "戶外與否": [],
    }
    occasion_cloth_type = {
        "Dating": [
            "long-skirt",
            "dress",
            "t-shirt",
            "sweater",
            "dress-shirt",
            "long-sleeve flannel-shirt",
            "long-sleeve button-up shirt",
            "short-sleeve button-up shirt",
            "short-sleeve flannel-shirt",
            "pants",
            "jeans",
            "cotton-pants",
            "shorts",
        ],
        "Daily_Work_and_Conference": [
            "dress-shirt",
            "jeans",
            "t-shirt",
            "sweater",
            "pants",
            "long-skirt",
            "cotton-pants",
            "shirt",
            "suit-jacket",
            "button-up-shirt",
            "long-sleeve button-up shirt",
        ],
        "Travel": ["t-shirt", "pants"],
        "Sports": ["t-shirt", "shorts", "yoga-pants", "sweatpants"],
        "Prom": ["skirt", "shirt", "sweater", "pants", "long-skirt"],
        "Shopping": ["pants", "t-shirt", "skirt", "cotton-pants", "shirt", "shorts"],
        "Party": [
            "dress",
            "long-skirt",
            "cotton-pants",
            "suit-jacket",
            "pants",
            "button-up-shirt",
            "dress-shirt",
        ],
        "School": [
            "pants",
            "jeans",
            "t-shirt",
            "hoodie",
            "sweater",
            "college-sweatshirt",
            "shorts",
            "shirt",
            "short-sleeve button-up shirt",
            "short-sleeve flannel shirt",
            "long-sleeve button-up shirt",
            "long-sleeve-shirt",
        ],
        "Wedding_Guest": [
            "dress",
            "dress-shirt",
            "long-sleeve button-up shirt",
            "short-sleeve button-up shirt",
            "cotton-pants",
            "skirt",
            "suit-jacket",
        ],
    }
    occasion_cloth_texture = {
        "Dating": [
            "chiffon",
            "leather",
            "denim",
            "cotton",
            "faux-fur",
            "faux-leather",
            "faux-suede",
            "leather",
            "suede",
            "woven",
            "thermal",
            "velvet",
        ],
        "Daily_Work_and_Conference": ["denim", "cotton"],
        "Travel": ["chiffon", "cotton", "denim", "cotton-pants"],
        "Sports": ["cotton", "Nylon"],
        "Prom": ["leather", "chiffon", "cutton", "velvet"],
        "Shopping": [
            "leather",
            "denim",
            "cotton",
            "chiffon",
        ],
        "Party": ["chiffon", "crochet", "sheer", "velvet"],
        "School": ["leather", "cotton", "denim", "woven"],
        "Wedding_Guest": ["cotton", "leather", "chiffon"],
    }
    occasion_cloth_Fabric = {
        "Dating": [
            "print",
            "pleated",
            "striped",
            "floral",
            "animal",
            "paisley-print",
            "abstract-print",
        ],
        "Daily_Work_and_Conference": [
            "striped",
            "print",
            "grid-print",
            "dotted",
            "colorblock",
        ],
        "Travel": ["print", "striped", "paisley-print", "camouflage", "colorblock"],
        "Sports": ["camouflage", "graphic", "tie-dye", "dotted", "abstract-print"],
        "Prom": ["print", "pleated", "floral", "glitter", "ornate-print", "baroque"],
        "Shopping": [
            "print",
            "striped",
            "floral",
            "graphic",
            "dotted",
            "paisley-print",
        ],
        "Party": ["pleated", "floral", "print", "glitter", "colorblock", "zebra-print"],
        "School": ["striped", "print", "grid-print", "abstract-print", "dotted"],
        "Wedding_Guest": [
            "floral",
            "paisley-print",
            "abstract-print",
            "ornate-print",
            "marble-print",
        ],
    }

    indoor_activity = ["Conference", "Prom", "Party", "Wedding_Guest"]
    outdoor = False

    if user_occasion not in indoor_activity:
        outdoor = True
    data["occasion"] = user_occasion
    data["pattern"] = occasion_cloth_Fabric[user_occasion]
    data["subcategories"] = occasion_cloth_type[user_occasion]
    data["material"] = occasion_cloth_texture[user_occasion]
    data["戶外與否"] = outdoor

    return data


def rule_base_filter(temperature, consider_weather=True, user_occasion=None):
    # 如果只考量天氣不考慮環境
    if consider_weather is True and user_occasion is None:
        candidate = weather_rule_base(temperature)

    # 只考量場合不考慮天氣 (不想考慮 or 室內)
    elif (consider_weather is False and user_occasion != "None") or (
        occasion_filter(user_occasion)["戶外與否"] is False
    ):
        candidate = occasion_filter(user_occasion)

    # 考量天氣與場合
    else:
        candidate = weather_rule_base(temperature)
        occasion_info = occasion_filter(user_occasion)
        for i in range(0, len(candidate)):
            item = candidate[i]["material"]
            candidate[i]["material"] = list(set(item) & set(occasion_info["material"]))
            item = candidate[i]["subcategories"]
            candidate[i]["subcategories"] = list(
                set(item) & set(occasion_info["subcategories"])
            )

    if type(candidate) is not list:
        return [candidate]
    else:
        return candidate


def scenario_filter(user_scenario):
    print("scenario_filter")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash-latest",
        generation_config={"response_mime_type": "application/json"},
    )

    # define prompt
    prompt = """Please consider the following scenario a user describe 
    and pick the cloths that satisfy the scenario, please only list the satisfy clothes, materials, patterns, mixed_categories without more description, 
    and output the answers as json format, where the keys are clothes, subcategories, patterns and the corresponding answer show place at the value :

    subcategories = [
        "t-shirt", "shirt", "dress-shirt", "button-up-shirt", "flannel-shirt", "sweater", 
        "hoodie", "jacket", "coat", "trench-coat", "suit-jacket", "denim-jacket", 
        "leather-jacket", "polo-shirt", "knit-top", "vest", "sweater-vest", "tank-top", 
        "turtleneck", "dress", "skirt", "long-skirt", "pants", "jeans", "shorts", 
        "suit-pants", "yoga-pants", "sweatpants", "overalls", "jumpsuit", "pajamas", 
        "bathrobe", "cotton-pants", "wool-pants", "leggings", "windproof-pants", 
        "cotton-vest", "down-jacket", "ski-jacket", "cotton-coat", "thermal-underwear", 
        "padded-jacket", "winter-sportswear", "insulated-vest", "thick-jeans", 
        "college-sweatshirt"
    ]

    material = [
        'cotton', 'denim', 'chiffon', 'faux-fur', 'faux-leather',
        'faux-suede', 'leather', 'linen', 'linen-blend', 'mesh',
        'metallic', 'neoprene', 'nylon', 'organza', 'sateen',
        'satin', 'suede', 'velvet', 'woven', 'thermal', 'crochet']
    patterns = [
        'abstract-print', 'animal', 'baroque', 'bird-print',
        'botanical-print', 'camouflage', 'colorblock', 'dotted',
        'floral', 'glitter', 'graphic', 'grid-print', 'leaf-print',
        'leopard-print', 'marble-print', 'medallion-print',
        'mixed-print', 'multi-stripe', 'ombre', 'ornate-print',
        'paisley-print', 'palm-print', 'pattern', 'pleated',
        'print', 'striped', 'tie-dye', 'zigzag']
    mixed_categories = [
        'boho', 'cargo', 'chic', 'cozy',
        'cute', 'elegant', 'everyday', 'fancy', 'retro',
        'safari', 'sporty', 'sweet', 'utility']



    """
    # user_scenario = '我今天要報告希望看起來正式又專業'
    response = model.generate_content(prompt + user_scenario)
    gemini_results_test = json.loads(
        response.text.replace("```json", "").replace("```", "")
    )
    print(gemini_results_test)
    return gemini_results_test
