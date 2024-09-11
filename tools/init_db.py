import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import Attribute, Category, Item, Outfit, Subcategory, ItemAttributeLink
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
    ),
    Item(
        name="FUTURE ARCHIVE / FADE SWEAT CREW",
        image_url="https://cdn.beams.co.jp/img/goods/11130704146/O/11130704146_C_1.jpg",
        category_id=1,
        subcategory_id=47,  # long-sleeve-shirt
        description="This sweatshirt is made of 100% cotton and features a unique fade design.",
    ),
    Item(
        name="FUTURE ARCHIVE / SWITH DENIM HOODY",
        image_url="https://cdn.beams.co.jp/img/goods/11181551791/L/11181551791_C_1.jpg",
        category_id=1,
        subcategory_id=7,  # hoodie
        description="This denim hoodie is made of 100% cotton and features a unique switch design.",
    ),
    Item(
        name="Moisture-wicking Tech Polo Shirt",
        image_url="https://cdn.beams.co.jp/img/goods/11081098146/L/11081098146_C_2.jpg",
        category_id=1,
        subcategory_id=1,  # polo-shirt
        description="This polo shirt is made of moisture-wicking fabric and features a classic design.",
    ),
    Item(
        name="NEEDLES / H.D. PANT - MILITARY",
        image_url="https://cdn.beams.co.jp/img/goods/11241682334/L/11241682334_C_1.jpg",
        category_id=2,
        subcategory_id=23,  # pants
        description="These military pants are made of 100% cotton and feature a relaxed fit.",
    ),
    Item(
        name="Dickies × FUTURE ARCHIVE / 別注 BAGGY PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241388995/L/11241388995_C_3.jpg",
        category_id=2,
        subcategory_id=23,  # pants
        description="These baggy pants are made of 100% cotton and feature a relaxed fit.",
    ),
    Item(
        name="FUTURE ARCHIVE / CHEMICAL SWEAT PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241748146/L/11241748146_C_2.jpg",
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
    ),
    Item(
        name="PURPLE LABEL / 女裝 蜂巢格 網眼布 短裙",
        image_url="https://cdn.beams.co.jp/img/goods/85270027551/L/85270027551_D_13.jpg",
        category_id=2,
        subcategory_id=21,  # skirt
        description="This skirt is made of 100% cotton and features a unique honeycomb design.",
    ),
    Item(
        name="BEAMS HEART / 女裝 起皺 襯衫式 上衣",
        image_url="https://cdn.beams.co.jp/img/goods/43110101819/L/43110101819_C_2.jpg",
        category_id=1,
        subcategory_id=3,  # dress-shirt
        description="This dress shirt is made of 100% cotton and features a unique wrinkled design.",
    ),
]

outfits = [Outfit(name="Casual Outfit"), Outfit(name="Formal Outfit")]

# Link items to outfits
item_outfit_links = [
    ItemAttributeLink(item_id=1, attribute_id=3),
    ItemAttributeLink(item_id=2, attribute_id=3),
    ItemAttributeLink(item_id=3, attribute_id=3),
    ItemAttributeLink(item_id=4, attribute_id=3),
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
        session.add_all(outfits)
        session.commit()

        session.add_all(item_outfit_links)
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
