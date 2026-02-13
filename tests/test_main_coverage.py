import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import logging
from collections import defaultdict
import json

# CORRECT IMPORT: Must match the application's runtime context (PYTHONPATH=src)
# Using 'src.badfish' here would cause isinstance checks to fail.
from badfish.main import execute_badfish, Badfish
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
        "Missing credentials. Please provide credentials via CLI arguments "
        "or environment variables."
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
    with patch(
        "badfish.main.HTTPClient.get_request", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response

        result = await execute_badfish(host, mock_args, logger, None)

    assert result == (host, False)

    # Verify logger was called with a BadfishException containing expected msg
    args, _ = logger.error.call_args
    exception_obj = args[0]

    assert isinstance(exception_obj, BadfishException)
    assert (
        str(exception_obj)
        == f"Failed to authenticate. Verify your credentials for {host}"
    )


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
    with patch(
        "badfish.main.HTTPClient.get_request", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response

        result = await execute_badfish(host, mock_args, logger, None)

    assert result == (host, False)

    # Verify logger was called with a BadfishException containing expected msg
    args, _ = logger.error.call_args
    exception_obj = args[0]

    assert isinstance(exception_obj, BadfishException)
    assert (
        str(exception_obj)
        == "Was unable to get Redfish Version. Please verify credentials/host."
    )


@pytest.mark.asyncio
async def test_init_no_response_from_host(mock_args):
    """Test that no response from host raises BadfishException (L383)."""
    host = "test_host"
    mock_args.update({"u": "user", "p": "pass", "retries": 1})
    logger = MagicMock(spec=logging.Logger)

    with patch(
        "badfish.main.HTTPClient.get_request", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None  # L383 condition

        result = await execute_badfish(host, mock_args, logger, None)

    assert result == (host, False)
    args, _ = logger.error.call_args
    assert isinstance(args[0], BadfishException)
    assert str(args[0]) == f"Failed to communicate with {host}"


@pytest.mark.asyncio
async def test_find_session_uri_fallback():
    """Test fallback logic when session URI check fails (L400)."""
    host = "test_host"
    logger = MagicMock(spec=logging.Logger)

    bf = Badfish(host, "user", "pass", logger, 1)
    bf.http_client = MagicMock()

    # 1. Root response: Version 1.0.0 ( < 160) -> sets uri to /redfish/v1/Sessions
    root_data = {"RedfishVersion": "1.0.0"}
    root_resp = MagicMock()
    root_resp.status = 200
    root_resp.text = AsyncMock(return_value=json.dumps(root_data))

    # 2. Check response: 404 (Not 200) -> Should fallback to /redfish/v1/SessionService/Sessions
    check_resp = MagicMock()
    check_resp.status = 404

    bf.http_client.get_request = AsyncMock(side_effect=[root_resp, check_resp])

    uri = await bf.find_session_uri()

    assert uri == "/redfish/v1/SessionService/Sessions"


@pytest.mark.asyncio
async def test_set_nic_attribute_invalid_fqdd_exception():
    """Test handling of invalid FQDD string operation raising exception (L2417-2419)."""
    host = "test_host"
    logger = MagicMock(spec=logging.Logger)

    bf = Badfish(host, "user", "pass", logger, 1)

    # Bypass get_nic_attribute_info check
    bf.get_nic_attribute_info = AsyncMock(
        return_value={
            "Type": "String",
            "CurrentValue": "Old",
            "MaxLength": 10,
            "MinLength": 1,
        }
    )

    # Mock fqdd object to raise ValueError on split
    # This simulates the except (IndexError, ValueError) block catch
    mock_fqdd = MagicMock()
    mock_fqdd.split.side_effect = ValueError("Mock Split Error")

    await bf.set_nic_attribute(mock_fqdd, "Attr", "NewVal")

    logger.error.assert_any_call("Invalid FQDD supplied.")
