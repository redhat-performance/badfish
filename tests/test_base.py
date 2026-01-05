import sys
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from badfish.main import main
from badfish.helpers.exceptions import BadfishException
from tests import config


class TestBase(AioHTTPTestCase):
    patch("asyncio.sleep").start()
    patch("time.sleep").start()

    async def get_application(self):
        return web.Application()

    @staticmethod
    def set_mock_response(mock, status, responses, post=False, headers=None):
        mock.return_value.__aenter__.return_value.name = responses
        status_mock = MagicMock()
        if isinstance(status, list):
            if post:
                dup_stats = [val for val in status for _ in range(2)]
                type(status_mock).status = PropertyMock(side_effect=dup_stats)
            else:
                type(status_mock).status = PropertyMock(side_effect=status)
        else:
            type(status_mock).status = PropertyMock(return_value=status)
        mock.return_value.__aenter__.return_value = status_mock
        mock.return_value.__aenter__.return_value.read = AsyncMock()
        if isinstance(responses, list):
            mock.return_value.__aenter__.return_value.text = AsyncMock(side_effect=responses)
        else:
            mock.return_value.__aenter__.return_value.text = AsyncMock(return_value=responses)
        if headers is not None:
            mock.return_value.__aenter__.return_value.headers = headers

    @pytest.fixture(autouse=True)
    def inject_capsys(self, capsys):
        self._capsys = capsys

    @pytest.fixture(autouse=True)
    def capture_wrap(self):
        sys.stderr.close = lambda *args: None
        sys.stdout.close = lambda *args: None
        yield

    def badfish_call(
        self,
        mock_host=config.MOCK_HOST,
        mock_user=config.MOCK_USER,
        mock_pass=config.MOCK_PASS,
    ):
        argv = []

        if mock_host is not None:
            argv.extend(("-H", mock_host))
        if mock_user is not None:
            argv.extend(("-u", mock_user))
        if mock_pass is not None:
            argv.extend(("-p", mock_pass))

        argv.extend(self.args)
        try:
            main(argv)
        except BadfishException:
            pass
        out, err = self._capsys.readouterr()
        return out, err


class MockResponse:
    def __init__(self, text: str, status: int):
        self.txt = text
        self.status = status

    async def text(self, arg1, arg2):
        return self.txt

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self
