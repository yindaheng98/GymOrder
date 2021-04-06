import time
import logging
import os
import sys
from logging import handlers

def getLogger():
    fname = 'logs/%s.log' % os.path.basename(sys.argv[0])
    logger = logging.getLogger(fname)
    th = handlers.TimedRotatingFileHandler(filename=fname, when='d', backupCount=3, encoding='utf-8')
    th.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s', '%I:%M:%S %p'))
    th.setLevel(logging.DEBUG)
    logger.addHandler(th)
    logger.setLevel(logging.DEBUG)
    return logger

if __name__ == "__main__":
    logger = getLogger()
    logger.info("test")
