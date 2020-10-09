import sys
import time

import pytest
from asynctest import CoroutineMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase
from asynctest import patch

from badfish.badfish import main, BadfishException
from tests import config


class TestBase(AioHTTPTestCase):
    patch("asyncio.sleep").start()

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

    @pytest.fixture(autouse=True)
    def capture_wrap(self):
        sys.stderr.close = lambda *args: None
        sys.stdout.close = lambda *args: None
        yield

    def badfish_call(self):
        argv = ["-H", config.MOCK_HOST, "-u", config.MOCK_USER, "-p", config.MOCK_PASS]
        argv.extend(self.args)
        try:
            main(argv)
        except BadfishException:
            pass
        out, err = self._capsys.readouterr()
        return out, err
