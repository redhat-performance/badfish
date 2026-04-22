import asyncio
from unittest.mock import MagicMock, patch
from badfish.main import Badfish
from tests.test_base import TestBase


class TestPollHelpers(TestBase):
    @patch("badfish.main.HTTPClient")
    def test_poll_until_ready_timeout(self, mock_http_client):
        logger = MagicMock()
        badfish = Badfish("test-host", "user", "pass", logger, 2)

        async def always_false():
            return False

        async def run_test():
            return await badfish.poll_until_ready(always_false, "test service", sleep_interval=0)

        result = asyncio.get_event_loop().run_until_complete(run_test())

        assert result is False
        logger.warning.assert_called_once_with("test service did not become ready after 2 retry attempts.")

    @patch("badfish.main.HTTPClient")
    def test_poll_until_ready_success(self, mock_http_client):
        logger = MagicMock()
        badfish = Badfish("test-host", "user", "pass", logger, 5)

        call_count = [0]

        async def check_after_attempts():
            call_count[0] += 1
            return call_count[0] >= 3

        async def run_test():
            return await badfish.poll_until_ready(check_after_attempts, "test service", sleep_interval=0)

        result = asyncio.get_event_loop().run_until_complete(run_test())

        assert result is True
        logger.info.assert_any_call("Polling for test service")
        logger.info.assert_any_call("test service is ready.")
