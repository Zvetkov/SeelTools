import os
import logging
from datetime import datetime
from pathlib import Path


# def add_handler(log_path):
#     # text file logger


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


module_path = Path(os.path.abspath(__file__))
log_path = os.path.join(module_path.parent.parent, 'log')

if not os.path.exists(log_path):
    os.mkdir(log_path)
file_handler = logging.FileHandler(os.path.join(log_path, f'debug_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'))
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - line %(lineno)d - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# fh = logging.FileHandler(f'log/debug_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
# fh.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - line %(lineno)d - %(message)s')
# fh.setFormatter(formatter)
console_handler.setFormatter(formatter)

# logger.addHandler(fh)
logger.addHandler(console_handler)

# current_dir = os.path.dirname(os.path.abspath(__file__))
# add_handler(os.path.join(current_dir, 'log'))

# logger.info('Logger initialized')
