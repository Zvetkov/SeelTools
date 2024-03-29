import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("SeelTools")

module_path = Path(os.path.abspath(__file__))
log_path = os.path.join(module_path.parent.parent, 'log')

if not os.path.exists(log_path):
    os.mkdir(log_path)
file_handler = logging.FileHandler(os.path.join(log_path, f'debug_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'))
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - line %(lineno)d - %(message)s')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter2 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - line %(lineno)d - %(message)s')
console_handler.setFormatter(formatter2)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
