import threading
import shutil
import random
from mock import Mock
import time
from unittest import TestCase
import os

import requests

from samcli.local.lambda_service.service import LocalLambdaService
from tests.functional.function_code import nodejs_lambda, API_GATEWAY_ECHO_EVENT
from samcli.commands.local.lib import provider
from samcli.local.lambdafn.runtime import LambdaRuntime
from samcli.commands.local.lib.local_lambda import LocalLambdaRunner
from samcli.local.docker.manager import ContainerManager


class TestService_FlaskDefaultOptionsDisabled(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code_abs_path = nodejs_lambda(API_GATEWAY_ECHO_EVENT)

        # Let's convert this absolute path to relative path. Let the parent be the CWD, and codeuri be the folder
        cls.cwd = os.path.dirname(cls.code_abs_path)
        cls.code_uri = os.path.relpath(cls.code_abs_path, cls.cwd)  # Get relative path with respect to CWD

        cls.function_name = "HelloWorld"

        cls.function = provider.Function(name=cls.function_name, runtime="nodejs4.3", memory=256, timeout=5,
                                         handler="index.handler", codeuri=cls.code_uri, environment=None,
                                         rolearn=None)

        cls.base64_response_function = provider.Function(name=cls.function_name, runtime="nodejs4.3", memory=256, timeout=5,
                                                         handler="index.handler", codeuri=cls.code_uri, environment=None,
                                                         rolearn=None)

        cls.mock_function_provider = Mock()
        cls.mock_function_provider.get.return_value = cls.function

        list_of_function_names = ['HelloWorld']

        cls.service, cls.port, cls.url, cls.scheme = make_service(list_of_function_names, cls.mock_function_provider, cls.cwd)
        cls.service.create()
        t = threading.Thread(name='thread', target=cls.service.run, args=())
        t.setDaemon(True)
        t.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.code_abs_path)

    def setUp(self):
        # Print full diff when comparing large dictionaries
        self.maxDiff = None

    def test_flask_default_options_is_disabled(self):
        expected = {"lambda": "mock response"}

        response = requests.post(self.url + '/2015-03-31/functions/HelloWorld/invocations')

        actual = response.json()

        self.assertEquals(actual, expected)
        self.assertEquals(response.status_code, 200)


def make_service(list_of_function_names, function_provider, cwd):
    port = random_port()
    manager = ContainerManager()
    local_runtime = LambdaRuntime(manager)
    lambda_runner = LocalLambdaRunner(local_runtime=local_runtime,
                                      function_provider=function_provider,
                                      cwd=cwd)

    service = LocalLambdaService(list_of_function_names, lambda_runner, port=port)

    scheme = "http"
    url = '{}://0.0.0.0:{}'.format(scheme, port)
    return service, port, url, scheme

def random_port():
    return random.randint(30000, 40000)