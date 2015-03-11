#!/usr/bin/env python
import web
import json
import logging
import basic_auth
from htsp.htsp_client import HtspManager
from unicode_utils import unicode_to_string

restrict = basic_auth.restrict

module_logger = logging.getLogger('htsp_rest')

manager = None

def handle_error(result):
    if (manager.is_error(result)):
        if (manager.is_bad_request(result)):
            raise BadRequestError(str(result['error']))
        else:
            raise InternalError(str(result['error']))


class CustomError(web.HTTPError):
    '''Custom error.'''

    headers = {'Content-Type': 'application/json'}

    def __init__(self, status, error, headers=None):
        message = json.dumps({'error': error})
        web.HTTPError.__init__(self, status, headers or self.headers,
                               unicode(message))

class BadRequestError(CustomError):
    '''Bad Request error.'''

    def __init__(self, error, headers=None):
        CustomError.__init__(self, '400 Bad Request', error, headers)

class InternalError(CustomError):
    '''Internal error.'''

    def __init__(self, error, headers=None):
        CustomError.__init__(self, '500 Internal Error', error, headers)

class list_channels:
    def __init__(self):
        self.logger = logging.getLogger('htsp_rest.list_channels')

    @restrict
    def GET(self):
        self.logger.debug("channels: %s", manager.channels)
        output = json.dumps(manager.channels)
        return output

class list_tags:
    def __init__(self):
        self.logger = logging.getLogger('htsp_rest.list_tags')

    @restrict
    def GET(self):
        self.logger.debug("tags: %s", manager.tags)
        output = json.dumps(manager.tags)
        return output

class list_dvr:
    def __init__(self):
        self.logger = logging.getLogger('htsp_rest.list_dvr')

    @restrict
    def GET(self):
        self.logger.debug("dvr_entries: %s", manager.dvr_entries)
        output = json.dumps(manager.dvr_entries)
        return output

    @restrict
    def POST(self):
        input = web.input()
        data = web.data()
        self.logger.info("add dvr_entry, input: %s", data)
        dvr_entry = unicode_to_string(json.loads(data))
        self.logger.info("add dvr_entry: %s", dvr_entry)
        result = manager.add_dvr_entry(dvr_entry)
        handle_error(result)
        output = json.dumps({'status': 'OK'})
        return output


class dvr_entry_by_channel_start:
    def __init__(self):
        self.logger = logging.getLogger('htsp_rest.dvr_entry_by_channel_start')

    @restrict
    def DELETE(self, channel, start):
        dvr_entry = unicode_to_string({'channel': channel, 'start': start})
        self.logger.info("remove dvr_entry: %s", dvr_entry)
        result = manager.remove_dvr_entry(dvr_entry)
        handle_error(result)
        output = json.dumps({'status': 'OK'})
        return output


class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

class HtspRest:
    def __init__(self, htspManager, port):
        self.logger = logging.getLogger('htsp_rest.HtspRest')
        self.manager = htspManager
        self.port = port

    def run(self):
        urls = (
            '/channels', 'list_channels',
            '/tags', 'list_tags',
            '/dvr/recordings', 'list_dvr',
            '/dvr/recordings/channel/(.*)/start/(.*)', 'dvr_entry_by_channel_start'
        )

        self.manager.start()

        web.config.debug = False
        self.logger.debug("web.config: %s", web.config)
        app = MyApplication(urls, globals())

        self.logger.info("starting server, port: %s", self.port)
        app.run(port=self.port)
