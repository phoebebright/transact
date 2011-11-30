from logging import getLogger, INFO
from cloghandler import ConcurrentRotatingFileHandler
from django.conf import settings
import os

log = getLogger()
# Use an absolute path to prevent file rotation trouble.
logfile = os.path.abspath(settings.APILOG)
# Rotate log after reaching 512K, keep 5 old copies.
rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 512*1024, 5)
log.addHandler(rotateHandler)
log.setLevel(settings.APILOG_LEVEL)

# log.info("Here is a very exciting log message, just for you")
