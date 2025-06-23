import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.badfish.main import Badfish, BadfishException, badfish_factory


class MockLogger:
    def __init__(self):
        self.debug_calls = []
        self.warning_calls = []
        self.info_calls = []
        self.error_calls = []
    
    def debug(self, message):
        self.debug_calls.append(message)
    
    def warning(self, message):
        self.warning_calls.append(message)
    
    def info(self, message):
        self.info_calls.append(message)
    
    def error(self, message):
        self.error_calls.append(message)


MOCK_HOST = "test-host.example.com"
MOCK_USERNAME = "test_user"
MOCK_PASSWORD = "test_password"
MOCK_RETRIES = 5


class TestContextManager:
    """Test cases for the async context manager methods."""

    @pytest.mark.asyncio
    async def test_context_manager_successful_entry_exit(self):
        """Test successful entry and exit of the context manager."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        # Mock the init method
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                async with badfish_instance as bf:
                    assert bf is badfish_instance
                    mock_init.assert_called_once()
                
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exception_handling(self):
        """Test that exceptions are properly handled and logged."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        # Mock the init method to raise an exception
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = BadfishException("Test exception")
            
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                with pytest.raises(BadfishException):
                    async with badfish_instance:
                        pass
                
                # When init fails, __aexit__ is not called because the exception is raised before entering the context
                mock_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager_direct_method_calls(self):
        """Test direct calls to __aenter__ and __aexit__ methods."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                # Test direct __aenter__ call
                result = await badfish_instance.__aenter__()
                assert result is badfish_instance
                mock_init.assert_called_once()
                
                # Test direct __aexit__ call
                await badfish_instance.__aexit__(None, None, None)
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_nested_usage(self):
        """Test nested usage of the context manager."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                # First context manager usage
                async with badfish_instance as bf1:
                    assert bf1 is badfish_instance
                    
                    # Nested context manager usage (should call init again)
                    async with badfish_instance as bf2:
                        assert bf2 is badfish_instance
                
                # delete_session should be called twice (once for each context)
                assert mock_delete.call_count == 2
                # init should be called twice (once for each context entry)
                assert mock_init.call_count == 2

    @pytest.mark.asyncio
    async def test_context_manager_integration_with_factory(self):
        """Test context manager integration with badfish_factory."""
        logger = MockLogger()
        
        with patch.object(Badfish, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(Badfish, 'delete_session', new_callable=AsyncMock) as mock_delete:
                async with await badfish_factory(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES) as badfish:
                    assert isinstance(badfish, Badfish)
                    assert badfish.host == MOCK_HOST
                    assert badfish.username == MOCK_USERNAME
                    assert badfish.password == MOCK_PASSWORD
                    # badfish_factory calls init, then context manager calls it again
                    assert mock_init.call_count == 2
                
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_session_cleanup(self):
        """Test that session cleanup happens even with exceptions."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                try:
                    async with badfish_instance:
                        raise ValueError("Unexpected error")
                except ValueError:
                    pass
                
                # delete_session should still be called despite the exception
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_init_failure(self):
        """Test context manager behavior when init fails."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = BadfishException("Init failed")
            
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                with pytest.raises(BadfishException):
                    async with badfish_instance:
                        pass
                
                # When init fails, __aexit__ is not called
                mock_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager_delete_session_failure(self):
        """Test context manager behavior when delete_session fails."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        
        with patch.object(badfish_instance, 'init', new_callable=AsyncMock) as mock_init:
            with patch.object(badfish_instance, 'delete_session', new_callable=AsyncMock) as mock_delete:
                mock_delete.side_effect = BadfishException("Delete session failed")
                
                # The exception should be re-raised from __aexit__
                with pytest.raises(BadfishException):
                    async with badfish_instance:
                        pass


class TestDeleteSession:
    """Test cases for the delete_session method."""

    @pytest.mark.asyncio
    async def test_delete_session_success(self):
        """Test successful session deletion."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        # Mock the delete_request method
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            # Mock response with status 200
            mock_response = MagicMock()
            mock_response.status = 200
            mock_delete_request.return_value = mock_response
            
            await badfish_instance.delete_session()
            
            # Verify delete_request was called with correct parameters
            mock_delete_request.assert_called_once()
            call_args = mock_delete_request.call_args
            assert call_args[0][0] == f"https://{MOCK_HOST}/redfish/v1/SessionService/Sessions/123"
            assert call_args[1]['headers'] == {"content-type": "application/json"}
            
            # Verify session_id and token are cleared
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None
            
            # Verify success message was logged
            assert any("Session successfully deleted" in call for call in logger.debug_calls)

    @pytest.mark.asyncio
    async def test_delete_session_404_status(self):
        """Test session deletion with 404 status (session not found)."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            # Mock response with status 404
            mock_response = MagicMock()
            mock_response.status = 404
            mock_delete_request.return_value = mock_response
            
            await badfish_instance.delete_session()
            
            # Verify session_id and token are still cleared
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None
            
            # Verify appropriate message was logged
            assert any("Session not found (404)" in call for call in logger.debug_calls)

    @pytest.mark.asyncio
    async def test_delete_session_unexpected_status(self):
        """Test session deletion with unexpected status code."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            # Mock response with unexpected status
            mock_response = MagicMock()
            mock_response.status = 500
            mock_delete_request.return_value = mock_response
            
            await badfish_instance.delete_session()
            
            # Verify session_id and token are still cleared
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None
            
            # Verify warning was logged
            assert any("Unexpected status 500" in call for call in logger.warning_calls)

    @pytest.mark.asyncio
    async def test_delete_session_exception_handling(self):
        """Test session deletion when delete_request raises an exception."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            mock_delete_request.side_effect = BadfishException("Network error")
            
            await badfish_instance.delete_session()
            
            # Verify session_id and token are still cleared despite the exception
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None
            
            # Verify exception was logged as warning
            assert any("Failed to delete session" in call for call in logger.warning_calls)
            assert any("Network error" in call for call in logger.warning_calls)

    @pytest.mark.asyncio
    async def test_delete_session_no_session_id(self):
        """Test delete_session when no session_id is set."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = None
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            await badfish_instance.delete_session()
            
            # delete_request should not be called
            mock_delete_request.assert_not_called()
            
            # token should still be cleared
            assert badfish_instance.token is None
            
            # Verify appropriate message was logged
            assert any("No session ID found" in call for call in logger.debug_calls)

    @pytest.mark.asyncio
    async def test_delete_session_cleanup_always_executes(self):
        """Test that cleanup (clearing session_id and token) always executes."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            # Mock response to raise an exception
            mock_delete_request.side_effect = Exception("Unexpected error")
            
            # The method should not raise the exception due to try/finally
            await badfish_instance.delete_session()
            
            # Verify session_id and token are still cleared despite the exception
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None

    @pytest.mark.asyncio
    async def test_delete_session_other_exception(self):
        """Test delete_session with non-BadfishException."""
        logger = MockLogger()
        badfish_instance = Badfish(MOCK_HOST, MOCK_USERNAME, MOCK_PASSWORD, logger, MOCK_RETRIES)
        badfish_instance.session_id = "/redfish/v1/SessionService/Sessions/123"
        badfish_instance.token = "test_token"
        
        with patch.object(badfish_instance, 'delete_request', new_callable=AsyncMock) as mock_delete_request:
            # Mock response to raise a different exception
            mock_delete_request.side_effect = ValueError("Unexpected error")
            
            # The method should not raise the exception due to try/finally
            await badfish_instance.delete_session()
            
            # Verify session_id and token are still cleared
            assert badfish_instance.session_id is None
            assert badfish_instance.token is None 