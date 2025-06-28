import logging
import os

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.expanduser("~/hohotach/app/logs/hohotach_server.log")),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
