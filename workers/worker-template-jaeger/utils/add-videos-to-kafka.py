import json
import os
from datetime import time

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaError

from framework.commons.logger import logger

from framework.etl.framework_etl import create_kafka_producer


def get_file_names(path):
    # List to store file names
    file_names = []

    # Check if the provided path is a directory
    if os.path.isdir(path):
        # Iterate through the files in the given directory
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                file_names.append(file_name)
    else:
        print(f"The path {path} is not a valid directory.")

    return file_names


# usage
directory_path = 'https://wowza-qlive.dcti.ro:7443/0039df70-6240-47cf-8fb4-dfe5316a4d14/'
files = get_file_names(directory_path)
print(files)

KAFKA_BOOTSTRAP_SERVERS = 'localhost'
producer = create_kafka_producer(KAFKA_BOOTSTRAP_SERVERS, 'topic_output_mist')

for file in files:
    producer.send('topic_input_mist', {'path': f'https://wowza-qlive.dcti.ro:7443/0039df70-6240-47cf-8fb4-dfe5316a4d14/{file}'})
    print(f'{file} sent to kafka')
