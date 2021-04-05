import time
import logging
import os
import sys


def getLogger():
    logging.basicConfig(filename='logs/%s-%s.log' % (os.path.basename(sys.argv[0]), time.strftime("%Y-%m-%d", time.localtime())),
                        format='%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s', level=logging.DEBUG,
                        filemode='a', datefmt='%I:%M:%S %p')
    return logging.getLogger()

if __name__ == "__main__":
    logger = getLogger()
    logger.info("test")
