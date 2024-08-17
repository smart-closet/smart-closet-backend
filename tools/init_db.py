import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import Attribute, Category, Item, Outfit

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

# Mock data
categories = [
    Category(name="top"),
    Category(name="bottom"),
    Category(name="shoes"),
    Category(name="bag"),
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
    ),
    Item(
        name="FUTURE ARCHIVE / FADE SWEAT CREW",
        image_url="https://cdn.beams.co.jp/img/goods/11130704146/O/11130704146_C_1.jpg",
        category_id=1,
    ),
    Item(
        name="FUTURE ARCHIVE / SWITH DENIM HOODY",
        image_url="https://cdn.beams.co.jp/img/goods/11181551791/L/11181551791_C_1.jpg",
        category_id=1,
    ),
    Item(
        name="FUTURE ARCHIVE / FADE RHINE STONE T-SHIRTS",
        image_url="https://cdn.beams.co.jp/img/goods/11020519803/L/11020519803_C_2.jpg",
        category_id=1,
    ),
    Item(
        name="Moisture-wicking Tech Polo Shirt",
        image_url="https://cdn.beams.co.jp/img/goods/11081098146/L/11081098146_C_2.jpg",
        category_id=1,
    ),
    Item(
        name="NEEDLES / H.D. PANT - MILITARY",
        image_url="https://cdn.beams.co.jp/img/goods/11241682334/L/11241682334_C_1.jpg",
        category_id=2,
    ),
    Item(
        name="Dickies × FUTURE ARCHIVE / 別注 BAGGY PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241388995/L/11241388995_C_3.jpg",
        category_id=2,
    ),
    Item(
        name="Dickies × FUTURE ARCHIVE / 別注 BAGGY PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241388995/L/11241388995_C_1.jpg",
        category_id=2,
    ),
    Item(
        name="FUTURE ARCHIVE / CHEMICAL SWEAT PANTS",
        image_url="https://cdn.beams.co.jp/img/goods/11241748146/L/11241748146_C_2.jpg",
        category_id=2,
    ),
    Item(
        name="FUTURE ARCHIVE / BAGGY FIT DENIM",
        image_url="https://cdn.beams.co.jp/img/goods/11211415791/L/11211415791_C_2.jpg",
        category_id=2,
    ),
    Item(
        name="SALOMON / XT-6 GORE-TEX BLACK /FTW SILVER",
        image_url="https://cdn.beams.co.jp/img/goods/11313754757/L/11313754757_C_1.jpg",
        category_id=3,
    ),
    Item(
        name="ARC'TERYX / Arro 22 Backpack",
        image_url="https://cdn.beams.co.jp/img/goods/11610342729/L/11610342729_C_1.jpg",
        category_id=4,
    )
]

outfits = [Outfit(name="Casual Outfit"), Outfit(name="Formal Outfit")]


# Function to insert mock data into the database
def create_mock_data():
    with Session(engine) as session:
        session.add_all(categories)
        session.add_all(attributes)
        session.add_all(items)
        session.add_all(outfits)
        session.commit()


# Insert the mock data
create_mock_data()

# Example query to verify data insertion
with Session(engine) as session:
    print("start query")
    statement = select(Item).where(Item.name == "ARC'TERYX / Arro 22 Backpack")
    results = session.exec(statement)
    for item in results:
        print(item)