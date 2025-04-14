from loguru import logger
import os
import sys
import logging

# Ensure logs directory exists
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logger with rotation
logger.remove()  # Remove default handler
logger.add(
    "logs/vatrecovery.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO",
    backtrace=True,
    diagnose=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Also log to stderr for console output with lower verbosity
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:HH:mm:ss} | <level>{level: <8}</level> | {message}"
)

logger.info("Logger initialized")
