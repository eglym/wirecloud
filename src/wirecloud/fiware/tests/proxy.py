# -*- coding: utf-8 -*-

# Copyright (c) 2014 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import unittest

from wirecloud.commons.utils.testcases import WirecloudTestCase


@unittest.skipIf(not ('wirecloud.fiware' in settings.INSTALLED_APPS and 'social_auth' in settings.INSTALLED_APPS), 'FI-WARE IdM support not available')
class ProxyTestCase(WirecloudTestCase):

    fixtures = ('selenium_test_data', 'fiware_proxy_test_data')
    tags = ('proxy-fiware',)

    def read_response(self, response):

        if getattr(response, 'streaming', False) is True:
            return "".join(response.streaming_content)
        else:
            return response.content

    def test_fiware_idm_processor(self):

        def echo_headers_response(method, url, *args, **kwargs):
            body = json.dumps(kwargs['headers'])
            return {
                'headers': {
                    'Content-Type': 'application/json',
                    'Content-Length': len(body),
                },
                'content': body,
            }

        self.network._servers['http']['example.com'].add_response('POST', '/path', echo_headers_response)
        url = reverse('wirecloud|proxy', kwargs={'protocol': 'http', 'domain': 'example.com', 'path': '/path'})

        client = Client()
        client.login(username='admin', password='admin')
        response = client.post(url, data='{}', content_type='application/json',
                HTTP_HOST='localhost',
                HTTP_REFERER='http://localhost/user/workspace',
                HTTP_X_FI_WARE_OAUTH_TOKEN='true',
                HTTP_X_FI_WARE_OAUTH_HEADER_NAME='X-Auth-Token')
        self.assertEqual(response.status_code, 200)
        headers = json.loads(self.read_response(response))
        self.assertIn('X-Auth-Token', headers)
        self.assertEqual(headers['X-Auth-Token'], 'yLCdDImTd6V5xegxyaQjBvC8ENRziFchYKXN0ur1y__uQ2ig3uIEaP6nJ0WxiRWGyCKquPQQmTIlhhYCMQWPXg')
