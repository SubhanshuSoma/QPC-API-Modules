"""
Error handling utilities for API modules.

This module provides retry logic, custom exceptions, and error handling
for all API clients.
"""

import time
import logging
import functools
from typing import Optional, Callable, Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(APIError):
    """Raised when input validation fails."""
    pass


class RetryableError(APIError):
    """Raised for errors that can be retried."""
    pass


class ErrorHandler:
    """Handles errors and provides retry logic for API calls."""
    
    @staticmethod
    def handle_response(response: requests.Response, service: str) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response (requests.Response): The HTTP response
            service (str): The service name for error context
            
        Returns:
            Dict[str, Any]: The response data
            
        Raises:
            AuthenticationError: For 401/403 errors
            RateLimitError: For 429 errors
            APIError: For other HTTP errors
        """
        if response.status_code == 200:
            return response.json()
        
        error_message = f"{service} API error: {response.status_code}"
        
        try:
            error_data = response.json()
            if 'message' in error_data:
                error_message += f" - {error_data['message']}"
        except ValueError:
            error_message += f" - {response.text}"
        
        if response.status_code in [401, 403]:
            raise AuthenticationError(error_message, response.status_code, response.json())
        elif response.status_code == 429:
            raise RateLimitError(error_message, response.status_code, response.json())
        else:
            raise APIError(error_message, response.status_code, response.json())
    
    @staticmethod
    def is_retryable_error(exception: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            exception (Exception): The exception to check
            
        Returns:
            bool: True if the error is retryable
        """
        retryable_exceptions = (
            ConnectionError,
            Timeout,
            RetryableError,
            requests.exceptions.HTTPError
        )
        
        return isinstance(exception, retryable_exceptions)
    
    @staticmethod
    def get_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """
        Calculate retry delay using exponential backoff.
        
        Args:
            attempt (int): The current attempt number
            base_delay (float): Base delay in seconds
            max_delay (float): Maximum delay in seconds
            
        Returns:
            float: Delay in seconds
        """
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        # Add jitter to prevent thundering herd
        jitter = delay * 0.1 * (1 + time.time() % 1)
        return delay + jitter


def retry_on_failure(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Callable:
    """
    Decorator for retrying API calls on failure.
    
    Args:
        max_attempts (int): Maximum number of retry attempts
        base_delay (float): Base delay between retries
        max_delay (float): Maximum delay between retries
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=base_delay, max=max_delay),
            retry=retry_if_exception_type((ConnectionError, Timeout, RetryableError)),
            before_sleep=lambda retry_state: logger.warning(
                f"Retrying {func.__name__} after error: {retry_state.outcome.exception()}"
            )
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_input(data: Any, required_fields: list, data_type: str = "input") -> None:
    """
    Validate input data for required fields.
    
    Args:
        data (Any): The data to validate
        required_fields (list): List of required field names
        data_type (str): Type of data for error messages
        
    Raises:
        ValidationError: If required fields are missing
    """
    if not isinstance(data, dict):
        raise ValidationError(f"{data_type} must be a dictionary")
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields in {data_type}: {missing_fields}")


def handle_rate_limit(response: requests.Response, service: str) -> None:
    """
    Handle rate limiting by waiting for the specified time.
    
    Args:
        response (requests.Response): The HTTP response
        service (str): The service name
        
    Raises:
        RateLimitError: If rate limit is exceeded
    """
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            wait_time = int(retry_after)
            logger.warning(f"{service} rate limit exceeded. Waiting {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            # Default wait time if Retry-After header is not provided
            logger.warning(f"{service} rate limit exceeded. Waiting 60 seconds.")
            time.sleep(60)
        
        raise RateLimitError(f"{service} rate limit exceeded", 429, response.json()) 