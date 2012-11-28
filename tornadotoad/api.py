import sys
import traceback
import urllib
from xml.etree.ElementTree import Element, SubElement, tostring

import tornado.httpclient
import tornado.ioloop

from tornadotoad import my


class TornadoToad(object):
    api_version = "2.2"
    notifier_name = "TornadoToad"
    notifier_version = "0.3"
    notifier_url = "http://github.com/ephramzerb/tornadotoad"

    def post_notice(self, exception, request=None):
        """Log an exception to Airbrake.

        Will send request asynchronously if there is an accessible IOloop
        (created by a started  Tornado App).  If no IOloop present, post
        synchronously.
        """
        if not my.registered:
            return False

        url = self.ssl_prefix() + "api.airbrake.io/notifier_api/v2/notices"
        body = self._build_notice_body(exception, request=request)
        self._send(url, body=body, headers={'Content-Type': 'text/xml'})

    def deploy(self, scm_repository=None, scm_revision=None,
              local_username=None):
        """Signify a deploy in Hoptoad.

        This will clear all the logged exception in Hoptoad for the registered
        environment. The keyword arguments are extra meta data that can be
        passed along.

        - scm_repository: What's your version control repo's address.
        - scm_revision: What's the version control revision.
        - local_username: Who deployed?

        More: http://help.airbrake.io/kb/api-2/notifier-api-version-22
        """
        params = {}
        params['api_key'] = my.api_key
        params['deploy[rails_env]'] = my.environment
        if scm_repository:
            params['deploy[scm_repository]'] = scm_repository
        if scm_revision:
            params['deploy[scm_revision]'] = scm_revision
        if local_username:
            params['deploy[local_username]'] = local_username
        url = self.ssl_prefix() + "hoptoadapp.com/deploys.txt"
        self._send(url, body=urllib.urlencode(params))

    def _build_notice_body(self, exception, request=None):
        root = Element('notice', {'version': self.api_version})
        api_key = SubElement(root, "api-key")
        api_key.text = my.api_key

        # notifier, notifier/name, notifier/version, notifier/url
        notifier = SubElement(root, "notifier")
        notifier_name = SubElement(notifier, "name")
        notifier_name.text = self.notifier_name
        notifier_version = SubElement(notifier, "version")
        notifier_version.text = self.notifier_version
        notifier_url = SubElement(notifier, "url")
        notifier_url.text = self.notifier_url

        # error
        error = SubElement(root, "error")
        error_class = SubElement(error, "class")
        error_class.text = exception.__class__.__name__

        # error/message
        error_message = SubElement(error, "message")

        error_message.text = u'%s: %s' % (
            exception[0],
            str(exception[1]).decode('utf-8')
        )

        # error/backtrace
        backtrace = SubElement(error, "backtrace")
        _type, _value, tb = sys.exc_info()
        tracebacks = traceback.extract_tb(tb)
        tracebacks.reverse()
        for tb in tracebacks:
            file_name, number, method, _ = tb
            line = SubElement(backtrace, "line", {'number': str(number),
                                                  'method': method,
                                                  'file': file_name})

        # request (optional)
        request_el = self._build_request_el(request) if request else None
        if request_el is not None:
            root.append(request_el)

        # server-environment
        server_environment = SubElement(root, "server-environment")
        project_root = SubElement(server_environment, "project-root")
        project_root.text = my.project_root
        environment = SubElement(server_environment, "environment-name")
        environment.text = my.environment
        app_version = SubElement(server_environment, "app-version")
        app_version.text = my.app_version

        return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, 'utf-8')

    def _build_request_el(self, request):
        """Compose and return a <request> element from a dict generated by
        the tornadotoad mixin."""
        # make sure we have all the requisite pieces.
        if 'url' not in request and 'component' not in request:
            return False

        # request
        request_el = Element("request")
        url = SubElement(request_el, "url")
        url.text = request['url']

        # request/component
        component = SubElement(request_el, "component")
        component.text = request['component']

        # request/cgi-data/var
        if 'cgi-data' in request and len(request['cgi-data'].keys()) > 0:
            cgi_data = SubElement(request_el, "cgi-data")
            for key in request['cgi-data'].keys():
                # don't send cookie data, for now.
                if key not in ['Cookie']:
                    key_el = SubElement(cgi_data, "var", {'key': key})
                    key_el.text = request['cgi-data'][key]

        # request/params/var
        if 'params' in request and len(request['params'].keys()) > 0:
            params = SubElement(request_el, "params")
            for key in request['params'].keys():
                key_el = SubElement(params, "var", {'key': key})
                key_el.text = str(request['params'][key]).decode('utf-8')

        return request_el

    def _send(self, url, body=None, headers=None):
        request = tornado.httpclient.HTTPRequest(url=url, method="POST",
                                                 body=body, headers=headers)
        if tornado.ioloop.IOLoop.initialized():
            http = tornado.httpclient.AsyncHTTPClient()
            http.fetch(request, self._done)
        else:
            http = tornado.httpclient.HTTPClient()
            response = http.fetch(request)

    def _done(self, response):
        pass

    @classmethod
    def ssl_prefix(cls):
        if my.use_ssl:
            return "https://"
        else:
            return "http://"
