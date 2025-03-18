import os
import csv
import json

from src.shared.logger_service import LoggingService

logger = LoggingService().initialize_logger()

def save_as_csv_and_json(csv_file, json_file, data, fieldnames):
    try:
        if not data:
            return

        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)

        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as json_file_read:
                try:
                    existing_data = json.load(json_file_read)
                    if not isinstance(existing_data, list):
                        existing_data = []
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.extend(data)

        with open(json_file, 'w', encoding='utf-8') as json_file_write:
            json.dump(existing_data, json_file_write, ensure_ascii=False, indent=4)

        logger.info(f"✅ Data saved to {csv_file} & {json_file} ✅")

    except:
        logger.info(f"🚨 Data saved to {csv_file} & {json_file} 🚨")

def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Unexpected error loading {file_path}: {e}")