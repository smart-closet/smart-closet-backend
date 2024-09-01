import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import Attribute, Category, Item, Outfit, Subcategory
import csv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

# 讀取 subcategory.csv 文件
def load_subcategories():
    subcategories = []
    with open('tools/subcategory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category_id = 1 if row['category'] == 'top' else 2
            subcategories.append(Subcategory(id=int(row['id']), name=row['value'], category_id=category_id))
    return subcategories

# Mock data
categories = [
    Category(id=1, name="top"),
    Category(id=2, name="bottom"),
    Category(id=3, name="shoes"),
    Category(id=4, name="bag"),
]

attributes = [
    Attribute(name="color", value="Red"),
    Attribute(name="size", value="M"),
    Attribute(name="material", value="Cotton"),
]

items = [
    Item(
        name="FUTURE ARCHIVE / FADE INSIDE OUT ZIP UP HOODIE",
        image_url="https://cdn.beams.co.jp/img/goods/11130702146/O/11130702146_C_2.jpg",
        category_id=1,
        subcategory_id=7,  # hoodie
    ),
    Item(
        name="FUTURE ARCHIVE / FADE SWEAT CREW",
        image_url="https://cdn.beams.co.jp/img/goods/11130704146/O/11130704146_C_1.jpg",
        category_id=1,
        subcategory_id=1,  # t-shirt
    ),
    Item(
        name="FUTURE ARCHIVE / SWITH DENIM HOODY",
        image_url="https://cdn.beams.co.jp/img/goods/11181551791/L/11181551791_C_1.jpg",
        category_id=1,
        subcategory_id=7,  # hoodie
    ),
    Item(
        name="Moisture-wicking Tech Polo Shirt",
        image_url="https://cdn.beams.co.jp/img/goods/11081098146/L/11081098146_C_2.jpg",
        category_id=1,
        subcategory_id=14,  # polo-shirt
    ),
    Item(
        name="NEEDLES / H.D. PANT - MILITARY",
        image_url="https://cdn.beams.co.jp/img/goods/11241682334/L/11241682334_C_1.jpg",
        category_id=2,
        subcategory_id=23,  # pants
    ),
    Item(
        name="Dickies × FUTURE ARCHIVE / 別注 BAGGY PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241388995/L/11241388995_C_3.jpg",
        category_id=2,
        subcategory_id=23,  # pants
    ),
    Item(
        name="FUTURE ARCHIVE / CHEMICAL SWEAT PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241748146/L/11241748146_C_2.jpg",
        category_id=2,
        subcategory_id=28,  # sweatpants
    ),
    Item(
        name="FUTURE ARCHIVE / BAGGY FIT DENIM",
        image_url="https://cdn.beams.co.jp/img/goods/11211415791/L/11211415791_C_2.jpg",
        category_id=2,
        subcategory_id=24,  # jeans
    ),
    Item(
        name="PURPLE LABEL / 女裝 蜂巢格 網眼布 短裙",
        image_url="https://cdn.beams.co.jp/img/goods/85270027551/L/85270027551_D_13.jpg",
        category_id=2,
        subcategory_id=21,  # skirt
    ),

    Item(
        name="BEAMS HEART / 女裝 起皺 襯衫式 上衣",
        image_url="https://cdn.beams.co.jp/img/goods/43110101819/L/43110101819_C_2.jpg",
        category_id=1,
        subcategory_id=3,  # jeans
    ),
]

outfits = [Outfit(name="Casual Outfit"), Outfit(name="Formal Outfit")]

# Function to insert mock data into the database
def create_mock_data():
    with Session(engine) as session:
        subcategories = load_subcategories()

        session.add_all(categories)
        session.add_all(subcategories)
        session.add_all(attributes)
        session.add_all(items)
        session.add_all(outfits)        
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