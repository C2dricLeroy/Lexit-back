import logging
import os
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.expanduser("~/lexit_logs")
os.makedirs(LOG_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOG_PATH, "app.log")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=10_000_000, backupCount=5)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)

if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
    logger.addHandler(handler)

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = [handler]
uvicorn_logger.setLevel(logging.INFO)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = [handler]
uvicorn_access_logger.setLevel(logging.INFO)
