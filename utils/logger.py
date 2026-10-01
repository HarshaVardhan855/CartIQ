import logging
import sys
import io

def setup_logger(name: str = "cartiq") -> logging.Logger:
    """
    Sets up a structured logger for CartIQ.
    Forces UTF-8 output to avoid UnicodeEncodeError on Windows cp1252 terminals
    when log messages contain ₹ or other non-ASCII characters.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        # Wrap stdout in a UTF-8 TextIOWrapper to handle non-ASCII chars safely
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        stream_handler = logging.StreamHandler(utf8_stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger

logger = setup_logger()
