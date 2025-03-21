import random
import time
from typing import List, Dict

from src.shared.utils.db_util import init_db, insert_dict, insert_batch_dicts, fetch_all, fetch_one
from src.shared.service.logger_service import LoggingService

logger = LoggingService().initialize_logger()

POSTS_DB_SCHEMA="""
        CREATE TABLE IF NOT EXISTS listings (
            post_number TEXT PRIMARY KEY,
            brand TEXT,
            model TEXT,
            title TEXT,
            link TEXT UNIQUE,
            subtitle TEXT,
            location TEXT,
            current_price TEXT,
            additional_info TEXT
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_number TEXT,
            image_url TEXT,
            FOREIGN KEY (post_number) REFERENCES listings(post_number) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS car_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_number TEXT,
            key TEXT,
            value TEXT,
            FOREIGN KEY (post_number) REFERENCES listings(post_number) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS technical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_number TEXT,
            key TEXT,
            value TEXT,
            FOREIGN KEY (post_number) REFERENCES listings(post_number) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS extras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_number TEXT,
            extra TEXT,
            FOREIGN KEY (post_number) REFERENCES listings(post_number) ON DELETE CASCADE
        );
        """

BRANDS_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS brands (
    name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    FOREIGN KEY (brand_name) REFERENCES brands(name) ON DELETE CASCADE
);
"""

# Create Database + Tables queries
def create_posts_database(file):
    init_db(file, POSTS_DB_SCHEMA)
    logger.info(f"✅ Database created at: {file}")

def create_brands_database(file: str):
    init_db(file, BRANDS_DB_SCHEMA)
    logger.info(f"✅ Brands database created at: {file}")

# Insert queries
def insert_post(file, data, retries=5, delay=0.5):
    for attempt in range(retries):
        try:
            insert_dict(file,"listings", {
                "post_number": data["post_number"],
                "brand": data["brand"],
                "model": data["model"],
                "title": data["title"],
                "link": data["link"],
                "subtitle": data["subtitle"],
                "location": data["location"],
                "current_price": data["current_price"],
                "additional_info": data["additional_info"]
            })

            insert_batch_dicts(file, "images", [
                {"post_number": data["post_number"], "image_url": img}
                for img in data.get("images", [])
            ])

            insert_batch_dicts(file, "car_parameters", [
                {"post_number": data["post_number"], "key": k, "value": v}
                for k, v in data.get("car_parameters", {}).items()
            ])

            insert_batch_dicts(file, "technical_data", [
                {"post_number": data["post_number"], "key": k, "value": v}
                for k, v in data.get("technical_data", {}).items()
            ])

            insert_batch_dicts(file, "extras", [
                {"post_number": data["post_number"], "extra": extra}
                for extra in data.get("extras", [])
            ])

            logger.info(f"✅ Inserted post: {data['title']} ({data['post_number']})")
            return
        except Exception as e:
            logger.warn(f"Post Insert Failed: {str(e)}")
            time.sleep(delay + random.uniform(0,0.5))

    logger.warn(f"Failed to insert post: {data['title']} ({data['post_number']}) after {retries} retries.")

def insert_brand(file: str, brand: dict):
    insert_dict(file, "brands", {
        "name": brand["name"],
        "url": brand["url"],
        "count": int(brand["count"]) if isinstance(brand["count"], str) else brand["count"]
    })

def insert_brands_bulk(db_path: str, brands: list[dict]):
    if not brands:
        return

    # Ensure all values are correctly typed (e.g., convert count to int)
    cleaned_brands = [
        {
            "name": brand["name"],
            "url": brand["url"],
            "count": int(brand["count"]) if isinstance(brand["count"], str) else brand["count"]
        }
        for brand in brands
    ]

    insert_batch_dicts(db_path, "brands", cleaned_brands)

def insert_models_bulk(db_path: str, brand_name: str, models: List[Dict[str, str]]) -> None:
    model_records = [
        {
            "brand_name": brand_name,
            "name": model["name"],
            "url": model["url"],
            "count": int(model.get("count", 0))
        }
        for model in models
    ]

    insert_batch_dicts(db_path, "models", model_records)

# Fetch queries
def fetch_all_brands(db_path: str):
    rows = fetch_all(db_path, "SELECT name, url, count FROM brands")
    return [{"name": name, "url": url, "count": count} for name, url, count in rows]

def get_brands_count(db_path: str) -> int:
    result = fetch_one(db_path, "SELECT COUNT(*) FROM brands")
    return result[0] if result else 0

def fetch_all_models(db_path: str) -> List[Dict[str, str]]:
    rows = fetch_all(db_path, "SELECT brand_name, name, url, count FROM models")

    return [
        {
            "brand_name": row[0],
            "name": row[1],
            "url": row[2],
            "count": row[3]
        }
        for row in rows
    ]