import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import aiohttp
import pytest

from badfish.helpers.http_client import HTTPClient
from badfish.helpers.exceptions import BadfishException


class DummyLogger:
    def __init__(self):
        self.debug_msgs = []
        self.warn_msgs = []

    def debug(self, msg):
        self.debug_msgs.append(str(msg))

    # Some paths call warning()
    def warning(self, msg):
        self.warn_msgs.append(str(msg))


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
    mock.return_value.__aenter__.return_value.read = AsyncMock(return_value=b"")
    if isinstance(responses, list):
        mock.return_value.__aenter__.return_value.text = AsyncMock(side_effect=responses)
    else:
        mock.return_value.__aenter__.return_value.text = AsyncMock(return_value=responses)
    mock.return_value.__aenter__.return_value.headers = headers or {}


@pytest.mark.asyncio
async def test_error_handler_valueerror_raises():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    resp = SimpleNamespace(text=AsyncMock(return_value="not-json"))
    with pytest.raises(BadfishException, match="Error reading response from host."):
        await client.error_handler(resp)


@pytest.mark.asyncio
async def test_error_handler_extended_info_with_custom_message():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    payload = {"error": {"@Message.ExtendedInfo": [{"Message": "detail", "Resolution": "fix it"}]}}
    resp = SimpleNamespace(text=AsyncMock(return_value=json.dumps(payload)))
    with pytest.raises(BadfishException, match="custom"):
        await client.error_handler(resp, message="custom")
    assert any("fix it" in m for m in logger.debug_msgs)
    assert any("detail" in m for m in logger.debug_msgs)


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_get_raw_success_with_token(mock_get):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    client.token = "TKN"
    set_mock_response(mock_get, 200, "{}")
    resp = await client.get_raw("https://x")
    assert resp.status == 200
    # Ensure header used (inspect kwargs robustly)
    called = False
    for args, kwargs in mock_get.call_args_list:
        if kwargs.get("headers", {}).get("X-Auth-Token") == "TKN":
            called = True
            break
    assert called


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_get_raw_success_with_basic_auth(mock_get):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    set_mock_response(mock_get, 200, "{}")
    resp = await client.get_raw("https://x", _get_token=True)
    assert resp.status == 200
    found_auth = False
    for args, kwargs in mock_get.call_args_list:
        if isinstance(kwargs.get("auth"), aiohttp.BasicAuth):
            found_auth = True
            break
    assert found_auth


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get", side_effect=Exception("boom"))
async def test_get_raw_exception_continue_returns_none(mock_get):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    resp = await client.get_raw("https://x", _continue=True)
    assert resp is None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get", side_effect=Exception("boom"))
async def test_get_raw_exception_raises(mock_get):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    with pytest.raises(BadfishException):
        await client.get_raw("https://x")
    assert any("Failed to communicate" not in m for m in logger.debug_msgs)  # debug captured


@pytest.mark.asyncio
async def test_get_json_success_and_invalid():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)

    class FakeResp:
        def __init__(self, text):
            self.status = 200
            self._text = text

        async def text(self, *args, **kwargs):
            return self._text

    client.get_raw = AsyncMock(return_value=FakeResp('{"a":1}'))
    data = await client.get_json("https://x1")
    assert data == {"a": 1}

    client.get_raw = AsyncMock(return_value=FakeResp("not json"))
    data = await client.get_json("https://x2")
    assert data is None

    client.get_raw = AsyncMock(return_value=None)
    data = await client.get_json("https://x3")
    assert data is None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_post_request_with_and_without_204(mock_post):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    client.token = "TT"

    # Non-204 => reads body, returns response
    set_mock_response(mock_post, 200, "OK", post=True)
    resp = await client.post_request("https://x", {"k": "v"}, {"h": "v"})
    assert resp.status == 200

    # 204 => returns without read
    set_mock_response(mock_post, 204, "", post=True)
    resp2 = await client.post_request("https://x", {"k": "v"}, {"h": "v"})
    assert resp2.status == 204


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", side_effect=Exception("err"))
async def test_post_request_raises(mock_post):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    with pytest.raises(BadfishException):
        await client.post_request("https://x", {}, {})


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.patch")
async def test_patch_request_success(mock_patch):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    set_mock_response(mock_patch, 200, "OK")
    resp = await client.patch_request("https://x", {}, {})
    assert resp.status == 200


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.patch", side_effect=Exception("bad"))
async def test_patch_request_continue_and_raise(mock_patch):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    # Continue returns None
    out = await client.patch_request("https://x", {}, {}, _continue=True)
    assert out is None
    # Raise by default
    with pytest.raises(BadfishException):
        await client.patch_request("https://x", {}, {})


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.delete")
async def test_delete_request_success(mock_delete):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    set_mock_response(mock_delete, 200, "OK")
    resp = await client.delete_request("https://x", {})
    assert resp.status == 200


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.delete", side_effect=Exception("x"))
async def test_delete_request_raises(mock_delete):
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    with pytest.raises(BadfishException):
        await client.delete_request("https://x", {})


@pytest.mark.asyncio
async def test_find_session_uri_paths_and_404_switch():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)

    # First call: root with Redfish 1.60 -> SessionService/Sessions
    # Second call: check session URI returns 200 => keep
    resp1 = SimpleNamespace(status=200, text=AsyncMock(return_value=json.dumps({"RedfishVersion": "1.60"})))
    resp2 = SimpleNamespace(status=200, text=AsyncMock(return_value="{}"))
    client.get_request = AsyncMock(side_effect=[resp1, resp2])
    out = await client.find_session_uri()
    assert out == "/redfish/v1/SessionService/Sessions"

    # If check returns 404, switch to SessionService/Sessions anyway
    resp1b = SimpleNamespace(status=200, text=AsyncMock(return_value=json.dumps({"RedfishVersion": "1.50"})))
    resp2b = SimpleNamespace(status=404, text=AsyncMock(return_value="{}"))
    client.get_request = AsyncMock(side_effect=[resp1b, resp2b])
    out2 = await client.find_session_uri()
    assert out2 == "/redfish/v1/SessionService/Sessions"


@pytest.mark.asyncio
async def test_find_session_uri_auth_or_comm_errors():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    # Unauthorized
    resp401 = SimpleNamespace(status=401, text=AsyncMock(return_value="{}"))
    client.get_request = AsyncMock(return_value=resp401)
    with pytest.raises(BadfishException, match="Failed to authenticate"):
        await client.find_session_uri()

    # Non-200/201
    resp500 = SimpleNamespace(status=500, text=AsyncMock(return_value="{}"))
    client.get_request = AsyncMock(return_value=resp500)
    with pytest.raises(BadfishException, match="Failed to communicate"):
        await client.find_session_uri()


@pytest.mark.asyncio
async def test_validate_credentials_success_and_errors():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)
    client.find_session_uri = AsyncMock(return_value="/redfish/v1/Sessions")

    headers = {"Location": "/redfish/v1/SessionService/Sessions/1", "X-Auth-Token": "TK"}
    resp_ok = SimpleNamespace(status=200, text=AsyncMock(return_value="OK"), headers=headers)
    client.post_request = AsyncMock(return_value=resp_ok)
    token = await client.validate_credentials()
    assert token == "TK"
    assert client.session_id == headers["Location"]

    # 401
    resp_unauth = SimpleNamespace(status=401, text=AsyncMock(return_value=""), headers={})
    client.post_request = AsyncMock(return_value=resp_unauth)
    with pytest.raises(BadfishException, match="Failed to authenticate"):
        await client.validate_credentials()

    # 500
    resp_err = SimpleNamespace(status=500, text=AsyncMock(return_value=""), headers={})
    client.post_request = AsyncMock(return_value=resp_err)
    with pytest.raises(BadfishException, match="Failed to communicate"):
        await client.validate_credentials()


@pytest.mark.asyncio
async def test_delete_session_paths_and_cleanup():
    logger = DummyLogger()
    client = HTTPClient("host", "u", "p", logger)

    # No session id => returns and keeps cleared
    client.session_id = None
    await client.delete_session()
    assert client.session_id is None and client.token is None

    # 200/201 => debug, then cleanup
    client.session_id = "/redfish/v1/SessionService/Sessions/1"
    client.token = "TK"
    resp_ok = SimpleNamespace(status=200, read=AsyncMock(return_value=b""))
    client.delete_request = AsyncMock(return_value=resp_ok)
    await client.delete_session()
    assert any("successfully deleted" in m for m in logger.debug_msgs)
    assert client.session_id is None and client.token is None

    # 404 => debug not found
    client.session_id = "/redfish/v1/SessionService/Sessions/2"
    client.token = "TK"
    resp_404 = SimpleNamespace(status=404, read=AsyncMock(return_value=b""))
    client.delete_request = AsyncMock(return_value=resp_404)
    await client.delete_session()
    assert any("not found" in m for m in logger.debug_msgs)

    # Other status => warning
    client.session_id = "/redfish/v1/SessionService/Sessions/3"
    client.token = "TK"
    resp_418 = SimpleNamespace(status=418, read=AsyncMock(return_value=b""))
    client.delete_request = AsyncMock(return_value=resp_418)
    await client.delete_session()
    assert any("Unexpected status" in m for m in logger.warn_msgs)

    # Exception during delete => warning
    client.session_id = "/redfish/v1/SessionService/Sessions/4"
    client.token = "TK"

    async def raise_exc(*args, **kwargs):
        raise RuntimeError("fail")

    client.delete_request = AsyncMock(side_effect=raise_exc)
    await client.delete_session()
    assert any("Failed to delete session" in m for m in logger.warn_msgs)
