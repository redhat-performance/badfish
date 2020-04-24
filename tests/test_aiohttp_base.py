import time

import pytest
from asynctest import CoroutineMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from src.badfish import main
from tests import config
from tests.config import JOB_ID


class TestBase(AioHTTPTestCase):
    time.sleep = lambda x: None

    async def get_application(self):
        return web.Application()

    @staticmethod
    def set_mock_response(mock, status, responses):
        mock.return_value.__aenter__.return_value.status = status
        mock.return_value.__aenter__.return_value.read = CoroutineMock()
        if type(responses) == list:
            mock.return_value.__aenter__.return_value.text = CoroutineMock()
            mock.return_value.__aenter__.return_value.text.side_effect = responses
        else:
            mock.return_value.__aenter__.return_value.text = CoroutineMock(
                return_value=responses
            )

    @pytest.fixture(autouse=True)
    def inject_capsys(self, capsys):
        self._capsys = capsys

    def badfish_call(self):
        argv = ["-H", config.MOCK_HOST, "-u", config.MOCK_USER, "-p", config.MOCK_PASS]
        argv.extend(self.args)
        main(argv)
        out, err = self._capsys.readouterr()
        return out, err
