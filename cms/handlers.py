## Imports
from flask import request, render_template
from logging import getLogger, INFO, WARN, ERROR
from logging.handlers import RotatingFileHandler
from time import strftime

from cms import app
from cms.admin.models import Content, Type
#!
request_log= getLogger('werkzeug')
request_log.disabled = True

def configure_logging(name, level):
    log= getLogger(name)
    log.setLevel(level)
    handler= RotatingFileHandler('logs/{}.log'.format(name), maxBytes=1024*1024, backupCount=10)
    log.addHandler(handler)
    return log

timestamp= strftime('[%d/%b/%Y %H:%M:%S]')

access_log= configure_logging('access', INFO)

@app.after_request
def after_request(response):
    if int(response.status_code) < 400:
        access_log.info('%s - - %s "%s %s %s" %s -', request.remote_addr, timestamp, request.method, request.path, request.scheme.upper(), response.status_code)

    return response