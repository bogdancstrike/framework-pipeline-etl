import ssl
from elasticsearch import Elasticsearch
from framework.commons.logger import logger
from dotenv import load_dotenv
from os import path
from config import Config
import config

ssl_context = ssl.create_default_context(cafile=Config.ELASTICSEARCH_CERT_PATH)

# Initialize the Elasticsearch client
# es = Elasticsearch(
#     [Config.ELASTICSEARCH_HOST],
#     basic_auth=(Config.ELASTICSEARCH_USERNAME, Config.ELASTICSEARCH_PASSWORD),
#     verify_certs=False
# )

es = Elasticsearch(
    [Config.ELASTICSEARCH_HOST],
    basic_auth=(Config.ELASTICSEARCH_USERNAME, Config.ELASTICSEARCH_PASSWORD),
    ssl_context=ssl_context,
    verify_certs=True
)

def save_or_update_in_elasticsearch(message):
    doc_id = message.get('id') or None  # Use existing ID if available, otherwise let ES generate it
    try:
        if doc_id:
            if es.exists(index=config.Config.ELASTICSEARCH_INDEX, id=doc_id):
                es.update(index=config.Config.ELASTICSEARCH_INDEX, id=doc_id, body={"doc": message})
                logger.info(f"Document with ID {doc_id} updated in index {config.Config.ELASTICSEARCH_INDEX}")
            else:
                res = es.index(index=config.Config.ELASTICSEARCH_INDEX, id=doc_id, document=message)
                doc_id = res.body['_id']
                message["id"] = doc_id
            logger.info(f"Document with ID {doc_id} created in index {config.Config.ELASTICSEARCH_INDEX}")
        else:
            res = es.index(index=config.Config.ELASTICSEARCH_INDEX, document=message)
            doc_id = res.body['_id']
            message["id"] = doc_id
            logger.info(f"Document created in index {config.Config.ELASTICSEARCH_INDEX} with ID {doc_id}")

        return doc_id

    except Exception as e:
        logger.error(f"Failed to save or update document: {e}")
        return None
