## Imports
from flask import request, render_template
from logging import getLogger, INFO, WARN, ERROR
from logging.handlers import RotatingFileHandler
from time import strftime
from traceback import format_exc

from cms import app
from cms.admin.models import Content, Type
from auth.py import unauthorized
#!
request_log= getLogger('werkzeug')
request_log.disabled = True


@app.context_processor
def inject_titles():
    titles= Content.query.with_entities(Content.slug, Content.title).join(Type).filter(Type.name=='page')
    return dict(titles=titles)

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

error_log= configure_logging('error', ERROR)
@app.errorhandler(Exception)
def handle_exception(e):
    tb= format_exc()
    error_log.error('%s - - %s "%s %s %s" 500 -\n%s', request.remote_addr, timestamp, request.method, request.path, request.scheme.upper(), tb)
    original= getattr(e, 'original_exception', None)
    if original is None:
        return render_template('error.html'), 500
    return render_template('error.html', error=original), 500

unauthorized_log= configure_logging('unauthorized', WARN)