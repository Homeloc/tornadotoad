# -*- coding: utf-8 -*-
import unittest
import sys
sys.path.append("..")

import tornadotoad
from tornadotoad.api import TornadoToad
from tornado.web import HTTPError


class TestApi(unittest.TestCase):
    def test_post_notice(self):
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
            raise Exception("Il s'agit d'une véritable exception")
        except:
            import sys
            e = sys.exc_info()
            toad = TornadoToad()
        try:
            toad.post_notice(e)
        except HTTPError:
            # a HTTP error is normal, since we didn't specify correct credentials for airbrake
            pass
