import time
from collections import defaultdict
from time import sleep

from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka.errors import NoBrokersAvailable, KafkaError
import json

from framework.redis.redis_utils import RedisUtils
from models.models import ConsumerConfig, create_session, init_db
from config import Config
from framework.commons.logger import logger
from ops_service.worker_kafka import process

# Initialize the database
init_db()

retry_number = 0

redis_util = RedisUtils(host=Config.REDIS_HOST, port=int(Config.REDIS_PORT), db=int(Config.REDIS_DB),
                        password=Config.REDIS_PASSWORD)


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
            logger.error(f"No Kafka brokers available: {e} -- {bootstrap_servers} --. Retrying in 5 seconds...")
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


def send_ack(consumer, message):
    try:
        # todo: sa-si tina valoarea actuala a rety-ului pt id-ul mesajul in Redis
        global retry_number
        if retry_number > 0:
            retry_number = 0
        # Commit the offset to acknowledge successful processing
        consumer.commit()
        logger.debug(f"Ack sent for message: {message}")
    except Exception as e:
        logger.error(f"Failed to send ack: {e}")


def send_nack(consumer, message):
    try:
        # todo: retry-ul merge la infinit
        # todo: sa-si tina valoarea actuala a rety-ului pt id-ul mesajul in Redis
        global retry_number
        retry_number += 1
        logger.info(f"Retry number: {retry_number}")
        # Create a TopicPartition instance for the current message
        topic_partition = TopicPartition(message.topic, message.partition)
        time.sleep(Config.NACK_TIME)

        # Seek to the message's offset to retry it on the next poll
        consumer.seek(topic_partition, message.offset)
        logger.warning(f"Nack sent for message: {message}. Will retry in the next poll.")
    except Exception as e:
        logger.error(f"Failed to send nack: {e}")


def handle_message(consumer, producer, topics_input, output_topics, consumer_name=Config.WORKER_NAME):
    try:
        logger.info("Starting message handling loop...")

        config = fetch_configuration(consumer_name)

        for message in consumer:
            try:
                if retry_number > Config.RETRY_COUNT:
                    try:
                        message_value = json.loads(message.value.decode('utf-8'))

                    except Exception as e:
                        # todo: implementat exceptie daca json-ul e corupt
                        message_value = "Error parsing message_value"

                    producer.send(Config.ERROR_TOPIC, message_value)
                    logger.info("Message sent to dead_letter topic")
                    # Send ack
                    try:
                        send_ack(consumer, message)
                    except:
                        logger.warn(f"Failed to send ack for message {message}", "yellow")
                else:
                    message_value = json.loads(message.value.decode('utf-8'))
                    message_id = message_value.get('id')

                    total_expected = len(topics_input)
                    if total_expected == 1 or Config.IS_AGGREGATOR is False:
                        process_and_forward(config, consumer, consumer_name, message_id, message_value,
                                            output_topics, producer, total_expected)
                    else:
                        # check in redis how many messages i have for that key
                        total_messages_for_key = redis_util.get_list_length(message_id)

                        if total_messages_for_key + 1 == total_expected:
                            ## pull messages from redis
                            messages_from_redis = [
                                json.loads(msg) for msg in redis_util.redis.lrange(message_id, 0, -1)
                            ]

                            ## add my message
                            messages_from_redis.append(message_value)
                            logger.info("message appended to redis")

                            ## aggregate messages
                            aggregated_message = aggregate_messages(messages_from_redis)

                            ## process and forward
                            process_and_forward(config, consumer, consumer_name, message_id, aggregated_message,
                                                output_topics, producer, total_expected)

                            ## clear redis
                            redis_util.delete_key(message_id)
                            logger.info("message deleted from redis")

                        else:
                            redis_util.redis.lpush(message_id, json.dumps(message_value))
                            redis_util.redis.expire(message_id, config.timeout if config.timeout else 600)

            except Exception as e:
                logger.error(f"Error processing message: {e}", "red_back")
                # Send nack
                send_nack(consumer, message)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}", "red_back")
    finally:
        close_resources(consumer, producer)


def process_and_forward(config, consumer, consumer_name, message_id, message_value, output_topics, producer,
                        total_expected):
    logger.info(
        f"All {total_expected} messages received for ID = {message_id}. Processing...", 'green')
    processed_message = process(message_value, consumer_name, config.metadatas)
    logger.debug(f"Processed message: {processed_message}")
    for output_topic in output_topics:
        producer.send(output_topic, processed_message)
        logger.debug(f"Processed message sent to Kafka topic {output_topic}", 'blue')
    # Send ack
    try:
        send_ack(consumer, processed_message)
    except:
        logger.warn(f"Failed to send ack for message {processed_message}", "red_back")


def aggregate_messages(messages):
    """
    Aggregates a list of dictionaries into a single dictionary.

    If dictionaries share the same keys, values are merged based on keys.

    :param messages: List of dictionaries with similar IDs to be aggregated.
    :return: A single aggregated dictionary.
    """
    aggregated_message = {}

    for message in messages:
        for key, value in message.items():
            # Add or update other message fields
            aggregated_message[key] = value

    return aggregated_message


def close_resources(consumer, producer):
    if consumer:
        try:
            consumer.close()
            logger.info("Kafka consumer closed.")
        except Exception as e:
            logger.error(f"Error closing Kafka consumer: {e}", "red_back")
    if producer:
        try:
            producer.close()
            logger.info("Kafka producer closed.")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}", "red_back")
