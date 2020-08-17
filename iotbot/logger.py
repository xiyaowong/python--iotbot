import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format='{level.icon} {time:YYYY-MM-DD HH:mm:ss} <lvl>{level}\t{message}</lvl>',
    colorize=True
)
