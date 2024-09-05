from utils.elastic_utils import save_to_elasticsearch
from utils.logger import logger
import requests
from config import API_URL

def process(message, consumer_name, metadatas):
    if "text" in message["content"]:
        try:
            # Example API call
            input_request = [{"content": message['content']['text'], "language": "EMPTY"}]
            response = requests.post(API_URL, json=input_request)

            if response.status_code == 200:
                api_result = response.json()

                # Assume the API returns a dictionary of results that you want to add to the content
                message["content"]["language"] = api_result[0]['language']
                save_to_elasticsearch(message, consumer_name)
            else:
                logger.error(f"{consumer_name}: API call failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"{consumer_name}: API call failed with exception {e}")

    return message
