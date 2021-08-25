import time
import logging
import os
import sys
from logging import handlers

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s')
fname = 'logs/%s.log' % os.path.basename(sys.argv[0])
logger = logging.getLogger(os.path.basename(sys.argv[0]))
th = handlers.TimedRotatingFileHandler(filename=fname, when='MIDNIGHT', backupCount=3, encoding='utf-8')
th.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'))
th.setLevel(logging.DEBUG)
logger.addHandler(th)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.info("test")
