import time
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaError
import json
from models.models import ConsumerConfig, create_session, init_db
from config import Config
from framework.commons.logger import logger
from ops_service.worker_kafka import process

# Initialize the database
init_db()


def fetch_configuration(consumer_name):
    session = create_session()
    config = session.query(ConsumerConfig).filter_by(consumer_name=consumer_name).first()
    session.close()
    if config:
        return config
    else:
        raise Exception(f"No configuration found for consumer: {consumer_name}")


def create_kafka_consumer(topics_input, bootstrap_servers):
    while True:
        try:
            consumer = KafkaConsumer(
                *topics_input,
                bootstrap_servers=bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=Config.WORKER_NAME
            )
            logger.info(f"Kafka consumer connected to topics {topics_input}")
            return consumer
        except NoBrokersAvailable as e:
            logger.error(f"No Kafka brokers available: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except KafkaError as e:
            logger.error(f"Kafka error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error while connecting to Kafka consumer: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def create_kafka_producer(bootstrap_servers, output_topics):
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info(f"Kafka producer connected to topics {output_topics}")
            return producer
        except NoBrokersAvailable as e:
            logger.error(f"No Kafka brokers available: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except KafkaError as e:
            logger.error(f"Kafka error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error while connecting to Kafka producer: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def handle_message(consumer, producer, topics_input, output_topics, consumer_name=Config.WORKER_NAME):
    try:
        logger.info("Starting message handling loop...")
        message_buffer = defaultdict(dict)
        topic_tracker = defaultdict(set)
        timestamp_buffer = {}

        config = fetch_configuration(consumer_name)

        # Use timeout from the DB, default to 240 if not set
        message_timeout = config.timeout if config.timeout else 240

        while True:
            current_time = time.time()
            message_batch = consumer.poll(timeout_ms=1000)

            for tp, messages in message_batch.items():
                for message in messages:
                    try:
                        message_value = json.loads(message.value.decode('utf-8'))
                        message_id = message_value.get('id')
                        topic = message.topic

                        if message_id not in message_buffer:
                            message_buffer[message_id] = {}
                            timestamp_buffer[message_id] = current_time

                        for key, value in message_value.items():
                            if key == "content" and key in message_buffer[message_id]:
                                message_buffer[message_id]["content"].update(value)
                            else:
                                message_buffer[message_id][key] = value

                        topic_tracker[message_id].add(topic)

                        num_received = len(topic_tracker[message_id])
                        total_expected = len(topics_input)
                        logger.info(
                            f"Message {num_received}/{total_expected} arrived for ID = {message_id} with content: {message_value}")

                        if num_received == total_expected:
                            logger.info(f"All {total_expected} messages received for ID = {message_id}. Processing...")

                            aggregated_message = message_buffer.pop(message_id)
                            processed_message = process(aggregated_message, consumer_name, config.metadatas)
                            # processed_message = process2()
                            logger.debug(f"Processed message: {processed_message}")

                            for output_topic in output_topics:
                                producer.send(output_topic, processed_message)
                                logger.debug(f"Processed message sent to Kafka topic {output_topic}")

                            timestamp_buffer.pop(message_id, None)
                            topic_tracker.pop(message_id, None)

                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

            for mid in list(timestamp_buffer.keys()):
                if current_time - timestamp_buffer[mid] > message_timeout:
                    logger.warn(
                        f"Timeout reached, ignoring and removing incomplete message with ID = {mid} from memory")
                    message_buffer.pop(mid, None)
                    timestamp_buffer.pop(mid, None)
                    topic_tracker.pop(mid, None)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
    finally:
        close_resources(consumer, producer)


def close_resources(consumer, producer):
    if consumer:
        try:
            consumer.close()
            logger.info("Kafka consumer closed.")
        except Exception as e:
            logger.error(f"Error closing Kafka consumer: {e}")
    if producer:
        try:
            producer.close()
            logger.info("Kafka producer closed.")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")
