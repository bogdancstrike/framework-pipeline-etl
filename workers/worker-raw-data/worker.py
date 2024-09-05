import json
import ssl
from datetime import datetime
from elasticsearch import Elasticsearch, ConnectionError
from config import ELASTICSEARCH_INDEX, ELASTICSEARCH_HOST, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD, \
    ELASTICSEARCH_CERT_PATH
from utils.logger import logger

ssl_context = ssl.create_default_context(cafile=ELASTICSEARCH_CERT_PATH)

es = Elasticsearch(
    [ELASTICSEARCH_HOST],
    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    ssl_context=ssl_context,
    verify_certs=True
)


def process(message, consumer_name, metadatas):
    try:
        logger.debug("processing message...")

        # Parse the incoming Kafka message

        # Prepare the document structure for Elasticsearch
        document = {
            "id": None,  # This will be filled by Elasticsearch
            "timestamp": datetime.utcnow().isoformat(),
            "type": "article",
            "content": message
        }

        # Save the document to Elasticsearch and capture the response
        es_response = es.index(index=ELASTICSEARCH_INDEX, body=document)
        logger.debug("Message saved to Elasticsearch")

        # Get the Elasticsearch generated ID
        es_id = es_response['_id']

        # Update the document with the Elasticsearch ID
        document['id'] = es_id

        # Log the structured message
        logger.debug(f"Structured message updated with Elasticsearch ID: {document}")

        # Return the updated document as the processed message
        return document

    except Exception as e:
        logger.error(f"Unexpected error in process function: {e}")
        raise
