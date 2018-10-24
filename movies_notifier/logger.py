import os
import datetime
import sys
import logging

logFormatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt='%H:%M')
logger = logging.getLogger()

# level
logger.setLevel(logging.INFO)

# console
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# log file
LOG_DIR = './data/logs'
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().isoformat()
log_filepath = os.path.join(LOG_DIR, f'log_{timestamp}.txt')
fileHanlder = logging.FileHandler(log_filepath)
fileHanlder.setFormatter(logFormatter)
logger.addHandler(fileHanlder)



