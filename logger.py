import logging
from datetime import datetime

logger = logging.getLogger('seeltools')
logger.setLevel(logging.DEBUG)


fh = logging.FileHandler(f'log/debug_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.info('Logger initialized')
