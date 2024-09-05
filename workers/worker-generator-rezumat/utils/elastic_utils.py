import json
import ssl
from datetime import datetime
from elasticsearch import Elasticsearch, ConnectionError
from es_config import ELASTICSEARCH_HOST, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD, ELASTICSEARCH_CERT_PATH
from utils.logger import logger

# Setup SSL context for Elasticsearch
# ssl_context = ssl.create_default_context(cafile=ELASTICSEARCH_CERT_PATH)

# Initialize the Elasticsearch client
es = Elasticsearch(
    [ELASTICSEARCH_HOST],
    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    # ssl_context=ssl_context,
    verify_certs=False
)


def save_to_elasticsearch(message, topic):
    doc_id = message.get('id')
    index_name = 'workers'

    es.index(index=index_name, id=doc_id, body=message)
    print(f"Document with ID {doc_id} was saved to index {index_name}")