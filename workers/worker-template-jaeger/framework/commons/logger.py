import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, Style, init, Back

# Initialize colorama for cross-platform support
init(autoreset=True)

# Define a mapping for supported colors
COLOR_MAP = {
    "blue": Fore.BLUE,
    "blue_back": Back.BLUE,
    "red": Fore.RED,
    "red_back": Back.RED,
    "green": Fore.GREEN,
    "green_back": Back.GREEN,
    "yellow": Fore.YELLOW,
    "yellow_back": Back.YELLOW,
    "cyan": Fore.CYAN,
    "cyan_back": Back.CYAN,
    "magenta": Fore.MAGENTA,
    "magenta_back": Back.MAGENTA,
    "white": Fore.WHITE,
    "white_back": Back.WHITE,
    "gray": Fore.LIGHTBLACK_EX,
    "gray_back": Back.LIGHTBLACK_EX
}


# Custom Logger to handle color argument
class CustomLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        # Handle optional color argument (last positional argument)
        if isinstance(args, tuple) and len(args) > 0 and isinstance(args[-1], str) and args[-1].lower() in COLOR_MAP:
            color = args[-1].lower()
            msg = f"{COLOR_MAP[color]}{msg}{Style.RESET_ALL}"
            args = args[:-1]  # Remove the color argument from args
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


# Set the custom logger as the default logger
logging.setLoggerClass(CustomLogger)

# Define the logger
logger = logging.getLogger("RotatingLog")
logger.setLevel(logging.DEBUG)  # Set minimum log level to DEBUG

# Create the logs directory if it doesn't exist
try:
    Path('logs').mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Couldn't create logs dir: {e}")

# Add a Rotating File Handler for file-based logging
# file_handler = RotatingFileHandler(
#     "logs/logs.log",  # Log file name
#     maxBytes=5 * 1024 * 1024 * 1024,  # Maximum size of a single file in bytes (5GB)
#     backupCount=2  # Number of backup files to keep (total of 3 including the active one)
# )
# file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(file_formatter)
# logger.addHandler(file_handler)

# Add Stream Handler for console logging
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
