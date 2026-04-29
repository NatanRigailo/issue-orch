import logging
import os

from app.scheduler import start

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "msg": %(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%S",
)

if __name__ == "__main__":
    start()
