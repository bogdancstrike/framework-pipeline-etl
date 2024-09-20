from utils.logger import logger


def process(message, consumer_name, metadatas):
    """
    Process the Kafka message by adding or modifying fields.

    This function is intended to be customized by developers to implement specific processing logic.
    The message passed to this function will contain all fields combined from multiple input topics (if applicable).

    Args:
        message (dict): The aggregated message with fields combined from one or more topics.
        consumer_name (str): The name of the consumer, as defined in `config.py`.
        metadatas (str): Additional metadata from the consumer configuration.

    Returns:
        dict: The final processed message.
    """
    # Example of using metadata
    if metadatas:
        logger.debug(f"{consumer_name}: processing message with metadata: {metadatas}")
        message['metadatas'] = metadatas  # Include metadata in the message

    logger.debug(f"{consumer_name}: processing message")
    return message
