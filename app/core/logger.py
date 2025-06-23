import logging
import os
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.expanduser("/var/log/lexit")
os.makedirs(LOG_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOG_PATH, "app.log")

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10_000_000, backupCount=5
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

for log_name in ("", "uvicorn", "uvicorn.access"):
    log = logging.getLogger(log_name)
    log.setLevel(logging.INFO)

    if not any(isinstance(h, RotatingFileHandler) for h in log.handlers):
        log.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):
        log.addHandler(console_handler)
