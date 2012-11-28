# -*- coding: utf-8 -*-
import unittest

import tornadotoad
from tornadotoad.api import TornadoToad
import tornadotoad.mixin
from tornado.web import RequestHandler, HTTPError, Application
from tornado.httpserver import HTTPRequest

from mock import patch


class TestApi(unittest.TestCase):
    def test_post_notice(self):
        patcher = patch('tornadotoad.api.TornadoToad._send')
        patcher.start()
        tornadotoad.register(
                api_key='',
                environment='',
                project_root='',
                app_version='',
                log_403=True,
                log_404=True,
                log_405=True
            )
        try:
            raise Exception("\xc3\x8ele-de-France'")
        except:
            import sys
            e = sys.exc_info()
            toad = TornadoToad()
            toad.post_notice(e)


class BaseHandler(tornadotoad.mixin.RequestHandler, RequestHandler):
    def send_error(self, **kwargs):
        super(BaseHandler, self).send_error(**kwargs)


class TestMixin(unittest.TestCase):
    #let's mock a request handler?
    def tedst_send_error(self):
        #patcher = patch('tornadotoad.api.TornadoToad._send')
        #patcher.start()
        request = HTTPRequest('GET', '/')
        app = Application([])
        handler = BaseHandler(app, request)
        def finish_nothing():
            pass
        handler.finish = finish_nothing
        try:
            raise Exception("Il s'agit d'une véritable exception")
        except:
            import sys
            e = sys.exc_info()
            handler.send_error(status_code=500, exc_info=e)
            f
