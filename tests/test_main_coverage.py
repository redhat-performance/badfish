import pytest
from unittest.mock import patch, MagicMock
import asyncio
import logging

from src.badfish.main import execute_badfish

@pytest.mark.asyncio
async def test_missing_credentials():
    host = "test_host"
    args = {}  # No 'u' or 'p' in args
    logger = MagicMock(spec=logging.Logger)
    format_handler = None

    with patch('os.environ.get', side_effect=lambda k: None):  # Mock env vars as missing
        result = await execute_badfish(host, args, logger, format_handler)

    assert result == (host, False)
    logger.error.assert_called_once_with(
        "Missing credentials. Please provide credentials via CLI arguments or environment variables."
    )
