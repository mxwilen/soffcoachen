import logging

def configure_logging():
    """Configure the logging for suspicious activity."""
    logging.basicConfig(
        filename="suspicious_activity.log",
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
