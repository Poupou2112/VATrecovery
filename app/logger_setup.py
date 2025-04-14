import logging
from loguru import logger

def setup_logger():
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Adapté pour intercepter tous les logs standards et les renvoyer à Loguru
            level = logger.level(record.levelname).name if record.levelname in logger._levels else "INFO"
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Désactive les logs de uvicorn si besoin
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

    logger.info("Logger initialized")
