from loguru import logger
logger.add("logs/vatrecovery.log", rotation="1 week", retention="4 weeks", level="INFO")
