"""
Authentication utilities for API modules.

This module provides secure token loading and validation for all API clients.
"""

import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
load_dotenv()

# Google Calendar API scopes
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']


class AuthManager:
    """Manages authentication for all API clients."""
    
    @staticmethod
    def get_coda_token() -> Optional[str]:
        """
        Get Coda API token from environment variables.
        
        Returns:
            Optional[str]: The Coda API token or None if not found
            
        Raises:
            ValueError: If CODA_API_TOKEN is not set in environment
        """
        token = os.getenv('CODA_API_TOKEN')
        if not token:
            raise ValueError(
                "CODA_API_TOKEN not found in environment variables. "
                "Please set it in your .env file."
            )
        return token
    
    @staticmethod
    def get_github_token() -> Optional[str]:
        """
        Get GitHub API token from environment variables.
        
        Returns:
            Optional[str]: The GitHub API token or None if not found
            
        Raises:
            ValueError: If GITHUB_TOKEN is not set in environment
        """
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError(
                "GITHUB_TOKEN not found in environment variables. "
                "Please set it in your .env file."
            )
        return token
    
    @staticmethod
    def get_google_calendar_credentials() -> Credentials:
        """
        Get Google Calendar API credentials.
        
        Returns:
            Credentials: Google API credentials object
            
        Raises:
            ValueError: If credentials file path is not set or file doesn't exist
        """
        credentials_file = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE')
        token_file = os.getenv('GOOGLE_CALENDAR_TOKEN_FILE', 'token.json')
        
        if not credentials_file:
            raise ValueError(
                "GOOGLE_CALENDAR_CREDENTIALS_FILE not found in environment variables. "
                "Please set it in your .env file."
            )
        
        if not os.path.exists(credentials_file):
            raise ValueError(f"Credentials file not found: {credentials_file}")
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, GOOGLE_CALENDAR_SCOPES)
        
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, GOOGLE_CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    @staticmethod
    def validate_token_format(token: str, service: str) -> bool:
        """
        Validate token format for different services.
        
        Args:
            token (str): The token to validate
            service (str): The service name ('coda', 'github', 'google')
            
        Returns:
            bool: True if token format is valid, False otherwise
        """
        if not token or not isinstance(token, str):
            return False
        
        if service == 'coda':
            # Coda tokens are typically alphanumeric
            return len(token) >= 20 and token.isalnum()
        elif service == 'github':
            # GitHub tokens are typically 40 character hex strings
            return len(token) == 40 and all(c in '0123456789abcdef' for c in token.lower())
        elif service == 'google':
            # Google tokens are typically longer and contain various characters
            return len(token) >= 50
        
        return True 