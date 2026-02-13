import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import logging
from collections import defaultdict

# CORRECT IMPORT: Must match the application's runtime context (PYTHONPATH=src)
# Using 'src.badfish' here would cause isinstance checks to fail.
from badfish.main import execute_badfish
from badfish.helpers.exceptions import BadfishException


@pytest.fixture
def mock_args():
    """Returns a dictionary that returns None for missing keys."""
    return defaultdict(lambda: None)


@pytest.mark.asyncio
async def test_missing_credentials():
    host = "test_host"
    args = {}
    logger = MagicMock(spec=logging.Logger)
    format_handler = None

    with patch("os.environ.get", side_effect=lambda k: None):
        result = await execute_badfish(host, args, logger, format_handler)

    assert result == (host, False)
    logger.error.assert_called_once_with(
        "Missing credentials. Please provide credentials via CLI arguments " "or environment variables."
    )


@pytest.mark.asyncio
async def test_init_401_unauthorized(mock_args):
    """Test that a 401 response raises a clean BadfishException."""
    host = "test_host"
    mock_args.update({"u": "user", "p": "pass", "retries": 1})
    logger = MagicMock(spec=logging.Logger)

    # Mock response for HTTPClient.get_request
    mock_response = MagicMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value='{"error": "Unauthorized"}')

    # Patch 'badfish' (not src.badfish) to match the import above
    with patch("badfish.main.HTTPClient.get_request", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await execute_badfish(host, mock_args, logger, None)

    assert result == (host, False)

    # Verify logger was called with a BadfishException containing expected msg
    args, _ = logger.error.call_args
    exception_obj = args[0]

    assert isinstance(exception_obj, BadfishException)
    assert str(exception_obj) == f"Failed to authenticate. Verify your credentials for {host}"


@pytest.mark.asyncio
async def test_init_key_error_missing_version(mock_args):
    """Test that missing RedfishVersion key raises a clean BadfishException."""
    host = "test_host"
    mock_args.update({"u": "user", "p": "pass", "retries": 1})
    logger = MagicMock(spec=logging.Logger)

    # Mock response for HTTPClient.get_request (Success 200 but bad payload)
    mock_response = MagicMock()
    mock_response.status = 200
    # Payload missing "RedfishVersion"
    mock_response.text = AsyncMock(return_value='{"OtherKey": "Value"}')

    # Patch 'badfish' (not src.badfish) to match the import above
    with patch("badfish.main.HTTPClient.get_request", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await execute_badfish(host, mock_args, logger, None)

    assert result == (host, False)

    # Verify logger was called with a BadfishException containing expected msg
    args, _ = logger.error.call_args
    exception_obj = args[0]

    assert isinstance(exception_obj, BadfishException)
    assert str(exception_obj) == "Was unable to get Redfish Version. Please verify credentials/host."
