import os
import platform
import ssl
import threading  # Import threading module
from _socket import gethostname
from pathlib import Path

import config
from framework.etl.framework_etl import fetch_configuration, create_kafka_consumer, create_kafka_producer, handle_message, close_resources
from config import Config
from models.instances import cors, jwt, bcrypt, talisman, flask_instrumentor, req_instrumentor
from framework.commons.logger import logger
from framework.api.dynamic import generate_endpoints_from_config
from framework.api.server import create_api, create_app
from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))
APP_FOLDER = Path(__file__).resolve().parent
APP_ROOT = APP_FOLDER.parent
VERSION = 0.1

app = Flask(
    __name__,
    root_path=APP_FOLDER.as_posix(),
    static_url_path='',
    instance_relative_config=True
)

def init_instances(app):
    cors.init_app(app)
    # db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    # migrate.init_app(app, db)
    talisman.init_app(app, content_security_policy=None, force_https=True, force_https_permanent=True)
    flask_instrumentor.instrument_app(app)
    req_instrumentor.instrument()
    # with app.app_context():
    # db.create_all()

def kafka_listener():
    consumer = None
    producer = None
    try:
        # Fetch configuration from the database
        config = fetch_configuration(Config.WORKER_NAME)

        # Parse topics and Kafka bootstrap server from configuration
        KAFKA_INPUT_TOPICS = config.topics_input.split(',')
        KAFKA_OUTPUT_TOPICS = config.topics_output.split(',')
        KAFKA_BOOTSTRAP_SERVERS = config.kafka_bootstrap_server.split(',')

        # Create Kafka consumer and producer with retry mechanisms
        consumer = create_kafka_consumer(KAFKA_INPUT_TOPICS, KAFKA_BOOTSTRAP_SERVERS)
        producer = create_kafka_producer(KAFKA_BOOTSTRAP_SERVERS, KAFKA_OUTPUT_TOPICS)

        # Handle incoming Kafka messages
        handle_message(consumer, producer, KAFKA_INPUT_TOPICS, KAFKA_OUTPUT_TOPICS)

    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
    finally:
        close_resources(consumer, producer)

def start_kafka_thread():
    # Start Kafka listener in a separate thread
    kafka_thread = threading.Thread(target=kafka_listener)
    kafka_thread.daemon = True  # Ensures it exits when the main program exits
    kafka_thread.start()

if __name__ == '__main__':
    start_kafka_thread()  # Start Kafka listener in a separate thread
    print('started kafka listeners...')

    app = create_app(app)
    api = create_api(
        app, version=VERSION,
        title='etl',
        description='ETL - API',
        iam_server=None
    )
    generate_endpoints_from_config(api)
    init_instances(app)
    with app.app_context():
        # db_init_test_data()
        pass
    app.app_context().push()

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER,
        purpose=ssl.Purpose.CLIENT_AUTH,
        # cafile='tls/trusted.pem'
    )
    context.load_cert_chain(config.Config.CERTIFICATE_APP, config.Config.KEY_APP)

    if 'liveconsole' not in gethostname():
        app.run(
            host="0.0.0.0", port=5001,
            ssl_context=context,
            use_reloader=False, debug=False
        )
        pass
    logger.info('{platform: %s, status: dead}' % (platform.system().lower()))
