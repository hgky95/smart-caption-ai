import os
import logging
import hashlib
from datetime import datetime

import requests
from database.db import get_db_connection
from mysql.connector import Error

logger = logging.getLogger(__name__)

class ImageStorageService:
    def __init__(self):
        self.base_path = os.getenv('IMAGE_STORAGE_PATH')

    def store_images_description(self, images_url, summaries):
        logger.info(f"Storing images and its description to file and database")
        try:
            for image_url_dict, summary_dict in zip(images_url, summaries):
                url = image_url_dict['url']
                summary = summary_dict['summary']
                image_hash = hashlib.sha256(url.encode()).hexdigest();

                if self.is_image_exists(image_hash):
                    logger.info(f"Image already exists: {image_hash}")
                    continue

                file_extension = os.path.splitext(url)[-1].lower() or '.png'
                image_filename = f"{image_hash}{file_extension}"

                date_path = datetime.now().strftime('%Y/%m/%d')
                image_path = os.path.join(self.base_path, date_path)
                full_image_path = os.path.join(image_path, image_filename)
                response = requests.get(url, timeout=30)
                image_data = response.content

                if not os.path.exists(image_path):
                    os.makedirs(image_path, exist_ok=True)

                with open(full_image_path, 'wb') as f:
                    f.write(image_data)

                self.store_to_db(image_hash, full_image_path, url, summary)
        except Exception as e:
            logger.error(f"Error storing images and its description to file and database: {e}")

    def is_image_exists(self, image_hash):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM images WHERE hash_id = %s", (image_hash,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Error as e:
            logger.error(f"Error finding image by hash: {e}")
            return False
    
    def store_to_db(self, image_hash, file_path, original_url, summary):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (hash_id, file_path, original_url, summary) VALUES (%s, %s, %s, %s)", 
                           (image_hash, file_path, original_url, summary))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Stored image to db: {image_hash}")
        except Error as e:
            logger.error(f"Error storing image to db: {e}")
