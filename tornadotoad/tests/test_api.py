# -*- coding: utf-8 -*-
import unittest

from lxml import etree
from mock import patch


@patch('tornadotoad.api.TornadoToad._send')
class TestApi(unittest.TestCase):

    def setUp(self):
        import tornadotoad
        tornadotoad.register(
                api_key='',
                environment='',
                project_root='',
                app_version='',
                log_403=True,
                log_404=True,
                log_405=True
            )

    def test_post_notice_ascii_string(self, sender):

        from tornadotoad.api import TornadoToad
        toad = TornadoToad()

        try:
            raise Exception("Ile-de-France")
        except Exception as e:
            toad.post_notice(e)

        # Check sent payload
        payload = sender.mock_calls[0][2]['body']
        root = etree.fromstring(payload)
        message = root.xpath('//message')[0].text
        self.assertEquals(message, u"Exception: Ile-de-France")

    def test_post_notice_utf8_string(self, sender):

        from tornadotoad.api import TornadoToad
        toad = TornadoToad()

        try:
            raise Exception("Île-de-France")
        except Exception as e:
            toad.post_notice(e)

        # Check sent payload
        payload = sender.mock_calls[0][2]['body']
        root = etree.fromstring(payload)
        message = root.xpath('//message')[0].text
        self.assertEquals(message, u"Exception: Île-de-France")

    def test_post_notice_unicode(self, sender):

        from tornadotoad.api import TornadoToad
        toad = TornadoToad()

        try:
            raise Exception(u"Île-de-France")
        except Exception as e:
            toad.post_notice(e)

        # Check sent payload
        payload = sender.mock_calls[0][2]['body']
        root = etree.fromstring(payload)
        message = root.xpath('//message')[0].text
        self.assertEquals(message, u"Exception: Île-de-France")


class TestMixin(unittest.TestCase):

    @patch('tornadotoad.api.TornadoToad._send')
    def test_send_error(self, sender):

        from tornado.httpserver import HTTPRequest
        from tornado.web import RequestHandler, Application
        from tornadotoad.mixin import RequestHandler as AirbrakeMixin

        class BaseHandler(AirbrakeMixin, RequestHandler):
            def send_error(self, **kwargs):
                super(BaseHandler, self).send_error(**kwargs)

        request = HTTPRequest('GET', '/')
        app = Application([])
        handler = BaseHandler(app, request)

        def finish_nothing():
            pass
        handler.finish = finish_nothing

        try:
            raise Exception("Une véritable exception")
        except:
            import sys
            exc_info = sys.exc_info()
            handler.send_error(status_code=500, exc_info=exc_info)

        # Check sent payload
        payload = sender.mock_calls[0][2]['body']
        root = etree.fromstring(payload)
        message = root.xpath('//message')[0].text
        self.assertEquals(message, u"Exception: Une véritable exception")
