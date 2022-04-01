import sys

import pytest
from asynctest import CoroutineMock, PropertyMock, MagicMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase
from asynctest import patch

from src.badfish.badfish import main, BadfishException
from tests import config


class TestBase(AioHTTPTestCase):
    patch("asyncio.sleep").start()
    patch("time.sleep").start()

    async def get_application(self):
        return web.Application()

    @staticmethod
    def set_mock_response(mock, status, responses):
        mock.return_value.__aenter__.return_value.name = responses
        if type(status) == list:
            status_mock = MagicMock()
            type(status_mock).status = PropertyMock(side_effect=status)
            mock.return_value.__aenter__.return_value = status_mock
        else:
            mock.return_value.__aenter__.return_value.status = status
        mock.return_value.__aenter__.return_value.read = CoroutineMock()
        if type(responses) == list:
            mock.return_value.__aenter__.return_value.text = CoroutineMock(
                side_effect=responses
            )
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
