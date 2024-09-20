import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Define the logger
logger = logging.getLogger("RotatingLog")
logger.setLevel(logging.DEBUG)  # Set minimum log level to DEBUG

try:
    Path('logs').mkdir(parents=True, exist_ok=True)
except:
    logger.debug("Coulnd't create logs dir")

# Add a Rotating File Handler for file-based logging
file_handler = RotatingFileHandler(
    "logs/logs.log",  # Log file name
    maxBytes=5 * 1024 * 1024 * 1024,  # Maximum size of a single file in bytes (5GB)
    backupCount=2  # Number of backup files to keep (total of 3 including the active one)
)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Add Stream Handler for console logging
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
