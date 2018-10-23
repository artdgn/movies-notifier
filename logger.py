import sys
import logging

logFormatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt='%H:%M')
logger = logging.getLogger()

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.setLevel(logging.INFO)

