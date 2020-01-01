import sys
import logging

from movies_notifier.config.common import LOG_FILEPATH

logFormatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt='%H:%M:%S')
logger = logging.getLogger()

# level
logger.setLevel(logging.INFO)

# console
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# log file

fileHanlder = logging.FileHandler(LOG_FILEPATH)
fileHanlder.setFormatter(logFormatter)
logger.addHandler(fileHanlder)



