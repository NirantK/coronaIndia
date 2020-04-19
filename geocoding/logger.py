from loguru import logger
import sys

def get_logger(name):
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    logger.add(f"{name}.log")
    return logger