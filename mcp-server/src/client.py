import httpx
from typing import Any, Dict, Optional
from src.config import get_settings


class APIClient:
    def __init__(self):
        self.settings = get_settings()
        self.backend_url = self.settings.backend_url
        self.simulator_url = self.settings.simulator_url
        self.adapter_mode = self.settings.adapter_mode
        self.timeout = self.settings.http_timeout
        
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        url = base_url or self.backend_url
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{url}{endpoint}", 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                raise ConnectionError(f"Cannot connect to {url}. Is the service running?")
            except httpx.TimeoutException:
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if 'message' in error_json:
                        error_detail = error_json['message']
                    elif 'error' in error_json:
                        error_detail = error_json['error']
                except:
                    pass
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code}: {error_detail}",
                    request=e.request,
                    response=e.response
                )
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        url = base_url or self.backend_url
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{url}{endpoint}", 
                    json=data, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                raise ConnectionError(f"Cannot connect to {url}. Is the service running?")
            except httpx.TimeoutException:
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if 'message' in error_json:
                        error_detail = error_json['message']
                    elif 'error' in error_json:
                        error_detail = error_json['error']
                except:
                    pass
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code}: {error_detail}",
                    request=e.request,
                    response=e.response
                )
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request to API (always backend)"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{self.backend_url}{endpoint}", 
                    json=data, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                raise ConnectionError(f"Cannot connect to {self.backend_url}. Is the backend service running?")
            except httpx.TimeoutException:
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if 'message' in error_json:
                        error_detail = error_json['message']
                    elif 'error' in error_json:
                        error_detail = error_json['error']
                except:
                    pass
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code}: {error_detail}",
                    request=e.request,
                    response=e.response
                )
    
    async def delete(self, endpoint: str) -> None:
        """Make DELETE request to API (always backend)"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.backend_url}{endpoint}", 
                    timeout=self.timeout
                )
                response.raise_for_status()
            except httpx.ConnectError:
                raise ConnectionError(f"Cannot connect to {self.backend_url}. Is the backend service running?")
            except httpx.TimeoutException:
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if 'message' in error_json:
                        error_detail = error_json['message']
                    elif 'error' in error_json:
                        error_detail = error_json['error']
                except:
                    pass
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code}: {error_detail}",
                    request=e.request,
                    response=e.response
                )


# Global client instance
client = APIClient()
