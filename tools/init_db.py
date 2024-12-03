import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import (
    Attribute,
    Category,
    Item,
    MyImage,
    Subcategory,
    ItemAttributeLink,
)
import csv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)


# 讀取 subcategory.csv 文件
def load_subcategories():
    subcategories = []
    with open("tools/subcategory.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category_id = 1 if row["category"] == "top" else 2
            subcategories.append(
                Subcategory(
                    id=int(row["id"]), name=row["value"], category_id=category_id
                )
            )
    return subcategories


def load_attributes():
    attributes = []
    with open("tools/attribute.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attributes.append(
                Attribute(id=int(row["id"]), name="material", value=row["value"])
            )
    return attributes


# Mock data
categories = [
    Category(id=1, name="top"),
    Category(id=2, name="bottom"),
    Category(id=3, name="shoes"),
    Category(id=4, name="bag"),
]

items = [
    Item(
        name="FUTURE ARCHIVE / FADE INSIDE OUT ZIP UP HOODIE",
        image_url="https://cdn.beams.co.jp/img/goods/11130702146/O/11130702146_C_2.jpg",
        category_id=1,
        subcategory_id=7,  # hoodie
        description="This hoodie is made of 100% cotton and features a unique inside-out design.",
        color="#303231",  # 用戶看到的顏色
        save_color="#211816",  # 用於顏色篩選的所保存的顏色
    ),
    Item(
        name="FUTURE ARCHIVE / FADE SWEAT CREW",
        image_url="https://cdn.beams.co.jp/img/goods/11130704146/O/11130704146_C_1.jpg",
        category_id=1,
        subcategory_id=47,  # long-sleeve-shirt
        description="This sweatshirt is made of 100% cotton and features a unique fade design.",
        color="#c3b5ab",  # 你可以新增顏色
        save_color="#d2b3ae",  # 你可以新增保存的顏色
    ),
    Item(
        name="FUTURE ARCHIVE / SWITH DENIM HOODY",
        image_url="https://cdn.beams.co.jp/img/goods/11181551791/L/11181551791_C_1.jpg",
        category_id=1,
        subcategory_id=7,  # hoodie
        description="This denim hoodie is made of 100% cotton and features a unique switch design.",
        color="#303231",  # 用戶看到的顏色
        save_color="#211816",  # 你可以新增保存的顏色
    ),
    Item(
        name="Moisture-wicking Tech Polo Shirt",
        image_url="https://cdn.beams.co.jp/img/goods/11081098146/L/11081098146_C_2.jpg",
        category_id=1,
        subcategory_id=1,  # polo-shirt
        description="This polo shirt is made of moisture-wicking fabric and features a classic design.",
        color="#37322f",  # 你可以新增顏色
        save_color="#221916",  # 你可以新增保存的顏色
    ),
    Item(
        name="Dickies × FUTURE ARCHIVE / 別注 BAGGY PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241388995/L/11241388995_C_3.jpg",
        category_id=2,
        subcategory_id=23,  # pants
        description="These baggy pants are made of 100% cotton and feature a relaxed fit.",
        color="#303231",  # 你可以新增顏色
        save_color="#93cc9e",  # 你可以新增保存的顏色
    ),
    Item(
        name="NEEDLES / Piping Cowboy Pant - Double Cloth",
        image_url="https://cdn.beams.co.jp/img/goods/11241683334/O/11241683334_D_3.jpg",
        category_id=2,
        subcategory_id=28,  # sweatpants
        description="These sweatpants are made of 100% cotton and feature a unique chemical design.",
    ),
    Item(
        name="FUTURE ARCHIVE / BAGGY FIT DENIM",
        image_url="https://cdn.beams.co.jp/img/goods/11211415791/L/11211415791_C_2.jpg",
        category_id=2,
        subcategory_id=24,  # jeans
        description="These baggy fit denim jeans are made of 100% cotton and feature a relaxed fit.",
        color="#6d6b64",  # 你可以新增顏色
        save_color="#947f62",  # 你可以新增保存的顏色
    ),
    Item(
        name="BEAMS HEART / 女裝 寬版打褶 丹寧 長裙",
        image_url="https://cdn.beams.co.jp/img/goods/43270116408/O/43270116408_D_15.jpg",
        category_id=2,
        subcategory_id=21,  # skirt
        description="This skirt is made of 100% cotton and features a unique honeycomb design.",
        color="#303231",  # 你可以新增顏色
        save_color="#211816",  # 你可以新增保存的顏色
    ),
    # Item(
    #     name="BEAMS HEART / 男裝 輕量 羅馬布 素面 襯衫",
    #     image_url="https://cdn.beams.co.jp/img/goods/41110064458/O/41110064458_D_10.jpg",
    #     category_id=1,
    #     subcategory_id=3,  # dress-shirt
    #     description="This dress shirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="BEAMS HEART / 男裝 可水洗 方平組織 二扣 西裝外套",
    #     image_url="https://cdn.beams.co.jp/img/goods/41160071195/O/41160071195_D_12.jpg",
    #     category_id=1,
    #     subcategory_id=11,  # suit-jacket
    #     description="This suit jacket is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="BEAMS HEART / 男裝 針頭狀花紋 TRAVEL 西裝 長褲",
    #     image_url="https://cdn.beams.co.jp/img/goods/41230066195/O/41230066195_D_19.jpg",
    #     category_id=2,
    #     subcategory_id=26,  # suit-pants
    #     description="These suit pants are made of 100% cotton and feature a unique wrinkled design.",
    # ),
    # Item(
    #     name="毛衣",
    #     image_url="https://cdn.beams.co.jp/img/goods/12130149803/O/12130149803_D_1.jpg",
    #     category_id=1,
    #     subcategory_id=6,  # sweater
    #     description="This sweater is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="粉色短裙",
    #     image_url="https://static.zara.net/assets/public/cb88/4996/03f14531a8f4/7c8f77eaac02/03152532621-e1/03152532621-e1.jpg?ts=1722596049527&w=850",
    #     category_id=2,
    #     subcategory_id=21,  # skirt
    #     description="This skirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="白色中長裙",
    #     image_url="https://static.zara.net/assets/public/8bec/0a70/13524c1f91a4/1fe2a365c82f/02298933712-e1/02298933712-e1.jpg?ts=1729165038480&w=850",
    #     category_id=2,
    #     subcategory_id=21,  # skirt
    #     description="This skirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="白色短裙",
    #     image_url="https://static.zara.net/assets/public/2691/c834/9484462482aa/3c5e51404c34/05536064250-e2/05536064250-e2.jpg?ts=1719303046584&w=850",
    #     category_id=2,
    #     subcategory_id=21,  # skirt
    #     description="This skirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="牛奶中腰長裙",
    #     image_url="https://static.zara.net/assets/public/624f/2f2b/26474773a35d/47861c3deff5/03607292400-e1/03607292400-e1.jpg?ts=1722929165357&w=850",
    #     category_id=2,
    #     subcategory_id=21,  # skirt
    #     description="This skirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="灰色運動衫",
    #     image_url="https://static.zara.net/assets/public/88aa/5803/3eb449c1b5b7/6a2e42355e20/03253318803-e1/03253318803-e1.jpg?ts=1719324485865&w=850",
    #     category_id=1,
    #     subcategory_id=1,
    #     description="This long-sleeve shirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="灰色運動褲",
    #     image_url="https://static.zara.net/assets/public/f216/b1c6/0c2a48b283f6/ccb60506f218/03253319803-e1/03253319803-e1.jpg?ts=1719324849550&w=850",
    #     category_id=2,
    #     subcategory_id=25,
    #     description="This long-sleeve shirt is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="白色短版背心",
    #     image_url="https://static.zara.net/assets/public/35fb/1690/22214375afdc/b30da1e12a6f/05644457250-e1/05644457250-e1.jpg?ts=1720693679026&w=850",
    #     category_id=1,
    #     subcategory_id=18,
    #     description="this tank top is made of 100% cotton and features a unique wrinkled design.",
    # ),
    # Item(
    #     name="藍色短版背心",
    #     image_url="https://static.zara.net/assets/public/fb26/2bd8/a9e440fe80bb/2a54d5aaae57/04174313420-e1/04174313420-e1.jpg?ts=1719326096149&w=850",
    #     category_id=1,
    #     subcategory_id=18,
    #     description="this tank top is made of 100% cotton and features a unique wrinkled design.",
    # ),
]

# Link items to outfits
item_attribute_links = [
    ItemAttributeLink(item_id=1, attribute_id=3),
    ItemAttributeLink(item_id=2, attribute_id=3),
    ItemAttributeLink(item_id=3, attribute_id=3),
    ItemAttributeLink(item_id=4, attribute_id=3),
]

my_images = [
    MyImage(
        user_id=1,
        image_url="https://storage.googleapis.com/quiztory-f5e09.appspot.com/items/ff484702-3dc1-4f4a-a9ca-4474170c20cf",
    ),
]


# Function to insert mock data into the database
def create_mock_data():
    with Session(engine) as session:
        subcategories = load_subcategories()
        attributes = load_attributes()

        session.add_all(attributes)
        session.add_all(categories)
        session.add_all(subcategories)
        session.add_all(attributes)
        session.add_all(items)
        session.add_all(my_images)
        session.commit()

        session.add_all(item_attribute_links)
        session.commit()


# Insert the mock data
create_mock_data()

# Example query to verify data insertion
with Session(engine) as session:
    print("start query")
    statement = select(Item).where(Item.name == "FUTURE ARCHIVE / BAGGY FIT DENIM")
    results = session.exec(statement)
    for item in results:
        print(item)
