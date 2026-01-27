"""
HTTP Client for external endpoint integration
Handles authentication, requests, and error handling for vehicle data endpoint
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from django.conf import settings

logger = logging.getLogger(__name__)


class EndpointClient:
    """
    HTTP client for consuming vehicle data from external endpoint
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize endpoint client.
        
        Args:
            base_url: Base URL for endpoint (defaults to settings.EXTERNAL_ENDPOINT_URL)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or getattr(settings, 'EXTERNAL_ENDPOINT_URL', '')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure session headers
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup common headers for requests"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Add authentication if configured
        api_key = getattr(settings, 'EXTERNAL_ENDPOINT_API_KEY', None)
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def get_vehicles(
        self,
        page: int = 1,
        page_size: int = 100,
        **filters
    ) -> Dict[str, Any]:
        """
        Fetch vehicles from endpoint with pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of records per page
            **filters: Additional filter parameters
            
        Returns:
            Response dict with structure:
            {
                "data": List[vehicle_data],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int
            }
            
        Raises:
            EndpointConnectionError: If connection fails
            EndpointResponseError: If response is invalid
        """
        try:
            url = urljoin(self.base_url, '/vehicles')
            
            params = {
                'page': page,
                'page_size': page_size,
                **filters
            }
            
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return self._validate_response(data)
        
        except requests.exceptions.Timeout:
            error_msg = f"Endpoint request timeout after {self.timeout} seconds"
            logger.error(error_msg)
            raise EndpointConnectionError(error_msg)
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to endpoint: {str(e)}"
            logger.error(error_msg)
            raise EndpointConnectionError(error_msg)
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from endpoint: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise EndpointResponseError(error_msg)
        
        except ValueError as e:
            error_msg = f"Invalid JSON response from endpoint: {str(e)}"
            logger.error(error_msg)
            raise EndpointResponseError(error_msg)
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Fetch a single vehicle by ID.
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle data dict
            
        Raises:
            EndpointConnectionError: If connection fails
            EndpointResponseError: If response is invalid
        """
        try:
            url = urljoin(self.base_url, f'/vehicles/{vehicle_id}')
            
            response = self.session.get(
                url,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict):
                raise EndpointResponseError("Expected object response for single vehicle")
            
            return data
        
        except requests.exceptions.Timeout:
            raise EndpointConnectionError(f"Endpoint timeout fetching vehicle {vehicle_id}")
        
        except requests.exceptions.ConnectionError as e:
            raise EndpointConnectionError(f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise EndpointResponseError(f"Vehicle {vehicle_id} not found")
            raise EndpointResponseError(f"HTTP error: {e.response.status_code}")
        
        except ValueError as e:
            raise EndpointResponseError(f"Invalid JSON response: {str(e)}")
    
    def _validate_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate endpoint response structure.
        
        Args:
            data: Response data
            
        Returns:
            Validated response dict
            
        Raises:
            EndpointResponseError: If validation fails
        """
        required_fields = ['data', 'total', 'page', 'page_size', 'total_pages']
        
        for field in required_fields:
            if field not in data:
                raise EndpointResponseError(f"Missing required field in response: {field}")
        
        if not isinstance(data['data'], list):
            raise EndpointResponseError("'data' field must be a list")
        
        return data
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class EndpointConnectionError(Exception):
    """Raised when connection to endpoint fails"""
    pass


class EndpointResponseError(Exception):
    """Raised when endpoint response is invalid"""
    pass
