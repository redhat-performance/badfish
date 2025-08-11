"""HTTP client operations for Badfish."""

import asyncio
import json
import base64
from typing import Optional, Dict, Any, Tuple

import aiohttp


class BadfishHTTPClient:
    """Handles all HTTP operations for Badfish."""
    
    def __init__(self, host: str, username: str, password: str, logger, retries: int = 15):
        self.host = host
        self.username = username
        self.password = password
        self.logger = logger
        self.retries = retries
        self.host_uri = f"https://{host}"
        self.redfish_uri = "/redfish/v1"
        self.root_uri = f"{self.host_uri}{self.redfish_uri}"
        self.semaphore = asyncio.Semaphore(50)
        self.token = None
        
    async def error_handler(self, response: aiohttp.ClientResponse, message: Optional[str] = None) -> None:
        """Handle HTTP errors with retries."""
        try:
            raw = await response.text("utf-8", "ignore")
        except Exception:
            await asyncio.sleep(1)
            return
            
        try:
            data = json.loads(raw)
            detail = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
        except Exception:
            if response.status == 401:
                detail = "Failed to authenticate. Verify your credentials."
            else:
                detail = f"HTTP {response.status}"
                
        if message:
            self.logger.error(f"{message}: {detail}")
        else:
            self.logger.error(detail)
            
    async def get_request(self, uri: str, _continue: bool = False, _get_token: bool = False) -> Optional[Dict[str, Any]]:
        """Execute GET request with retry logic."""
        return await self.get_raw(uri, _continue, _get_token)
        
    async def get_raw(self, uri: str, _continue: bool = False, _get_token: bool = False) -> Optional[Dict[str, Any]]:
        """Execute raw GET request."""
        headers = {"Content-Type": "application/json"}
        if self.token and not _get_token:
            headers["X-Auth-Token"] = self.token
            
        async with self.semaphore:
            for retry in range(self.retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=60)
                    connector = aiohttp.TCPConnector(ssl=False, limit=50)
                    
                    async with aiohttp.ClientSession(
                        connector=connector, timeout=timeout
                    ) as session:
                        response = await session.get(uri, headers=headers)
                        
                        if response.status in [200, 202]:
                            try:
                                data = await response.json()
                                return data
                            except Exception:
                                return None
                        elif response.status == 401 and retry < (self.retries - 1):
                            await asyncio.sleep(1)
                            continue
                        elif not _continue:
                            await self.error_handler(response)
                            return None
                            
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    if retry == (self.retries - 1):
                        self.logger.error(f"Connection failed after {self.retries} attempts")
                        return None
                    await asyncio.sleep(1)
                    
        return None
        
    async def post_request(
        self, 
        uri: str, 
        payload: Dict[str, Any], 
        headers: Dict[str, str], 
        _get_token: bool = False,
        return_headers: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], int, Optional[Dict[str, str]]]:
        """Execute POST request."""
        if self.token and not _get_token:
            headers["X-Auth-Token"] = self.token
            
        async with self.semaphore:
            for retry in range(self.retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=60)
                    connector = aiohttp.TCPConnector(ssl=False, limit=50)
                    
                    async with aiohttp.ClientSession(
                        connector=connector, timeout=timeout
                    ) as session:
                        response = await session.post(uri, json=payload, headers=headers)
                        
                        if response.status in [200, 201, 202, 204]:
                            try:
                                data = await response.json()
                                response_headers = dict(response.headers) if (_get_token or return_headers) else None
                                return data, response.status, response_headers
                            except Exception:
                                response_headers = dict(response.headers) if (_get_token or return_headers) else None
                                return None, response.status, response_headers
                        elif response.status == 401 and retry < (self.retries - 1):
                            await asyncio.sleep(1)
                            continue
                        else:
                            await self.error_handler(response)
                            return None, response.status, None
                            
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    if retry == (self.retries - 1):
                        self.logger.error(f"Connection failed after {self.retries} attempts")
                        return None, 0, None
                    await asyncio.sleep(1)
                    
        return None, 0, None
        
    async def patch_request(
        self,
        uri: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        _continue: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Execute PATCH request."""
        if self.token:
            headers["X-Auth-Token"] = self.token
            
        async with self.semaphore:
            for retry in range(self.retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=60)
                    connector = aiohttp.TCPConnector(ssl=False, limit=50)
                    
                    async with aiohttp.ClientSession(
                        connector=connector, timeout=timeout
                    ) as session:
                        response = await session.patch(uri, json=payload, headers=headers)
                        
                        if response.status in [200, 202, 204]:
                            try:
                                data = await response.json()
                                return data
                            except Exception:
                                return {}
                        elif response.status == 401 and retry < (self.retries - 1):
                            await asyncio.sleep(1)
                            continue
                        elif not _continue:
                            await self.error_handler(response)
                            return None
                            
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    if retry == (self.retries - 1):
                        self.logger.error(f"Connection failed after {self.retries} attempts")
                        return None
                    await asyncio.sleep(1)
                    
        return None
        
    async def delete_request(self, uri: str, headers: Dict[str, str]) -> bool:
        """Execute DELETE request."""
        if self.token:
            headers["X-Auth-Token"] = self.token
            
        async with self.semaphore:
            for retry in range(self.retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=60)
                    connector = aiohttp.TCPConnector(ssl=False, limit=50)
                    
                    async with aiohttp.ClientSession(
                        connector=connector, timeout=timeout
                    ) as session:
                        response = await session.delete(uri, headers=headers)
                        
                        if response.status in [200, 202, 204]:
                            return True
                        elif response.status == 401 and retry < (self.retries - 1):
                            await asyncio.sleep(1)
                            continue
                        else:
                            await self.error_handler(response)
                            return False
                            
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    if retry == (self.retries - 1):
                        self.logger.error(f"Connection failed after {self.retries} attempts")
                        return False
                    await asyncio.sleep(1)
                    
        return False
        
    async def validate_credentials(self) -> Optional[str]:
        """Validate credentials and obtain authentication token."""
        encoded_creds = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json"
        }
        
        payload = {"UserName": self.username, "Password": self.password}
        uri = f"{self.root_uri}/SessionService/Sessions"
        
        response, status = await self.post_request(uri, payload, headers, _get_token=True)
        
        if response and status in [200, 201]:
            try:
                return response.get("X-Auth-Token") or response.get("SessionToken")
            except (KeyError, TypeError):
                self.logger.error("Failed to retrieve authentication token")
                return None
        else:
            self.logger.error("Authentication failed")
            return None