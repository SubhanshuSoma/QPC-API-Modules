"""
Coda API Client

A comprehensive client for interacting with the Coda API.
Provides document and database management with secure authentication
and error handling.
"""

import requests
from typing import Dict, List, Optional, Any
from utils.auth import AuthManager
from utils.error_handling import (
    ErrorHandler, retry_on_failure, validate_input,
    APIError, AuthenticationError, RateLimitError
)


class CodaClient:
    """
    Client for interacting with the Coda API.
    
    Provides methods for managing documents, tables, and data in Coda.
    Includes secure authentication, error handling, and retry logic.
    """
    
    def __init__(self, api_token: Optional[str] = None, base_url: str = "https://coda.io/apis/v1"):
        """
        Initialize the Coda API client.
        
        Args:
            api_token (Optional[str]): Coda API token. If not provided, 
                                     will be loaded from environment variables.
            base_url (str): Base URL for the Coda API
        """
        self.base_url = base_url
        self.api_token = api_token or AuthManager.get_coda_token()
        
        # Validate token format
        if not AuthManager.validate_token_format(self.api_token, 'coda'):
            raise ValueError("Invalid Coda API token format")
        
        # Set up headers
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    @retry_on_failure(max_attempts=3)
    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents accessible to the authenticated user.
        
        Args:
            limit (int): Maximum number of documents to return (default: 100)
            
        Returns:
            List[Dict[str, Any]]: List of document objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
            
        Example:
            >>> client = CodaClient()
            >>> documents = client.list_documents(limit=50)
            >>> for doc in documents:
            ...     print(f"Document: {doc['name']} (ID: {doc['id']})")
        """
        url = f"{self.base_url}/docs"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            data = ErrorHandler.handle_response(response, "Coda")
            return data.get('items', [])
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to list documents: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific document.
        
        Args:
            doc_id (str): The ID of the document to retrieve
            
        Returns:
            Dict[str, Any]: Document information
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If doc_id is invalid
            
        Example:
            >>> client = CodaClient()
            >>> doc = client.get_document("doc_123456")
            >>> print(f"Document: {doc['name']}")
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("Document ID must be a non-empty string")
        
        url = f"{self.base_url}/docs/{doc_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            return ErrorHandler.handle_response(response, "Coda")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get document {doc_id}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def list_tables(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        List all tables in a specific document.
        
        Args:
            doc_id (str): The ID of the document
            
        Returns:
            List[Dict[str, Any]]: List of table objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If doc_id is invalid
            
        Example:
            >>> client = CodaClient()
            >>> tables = client.list_tables("doc_123456")
            >>> for table in tables:
            ...     print(f"Table: {table['name']} (ID: {table['id']})")
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("Document ID must be a non-empty string")
        
        url = f"{self.base_url}/docs/{doc_id}/tables"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            data = ErrorHandler.handle_response(response, "Coda")
            return data.get('items', [])
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to list tables for document {doc_id}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_table_data(self, doc_id: str, table_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get data from a specific table in a document.
        
        Args:
            doc_id (str): The ID of the document
            table_id (str): The ID of the table
            limit (int): Maximum number of rows to return (default: 100)
            
        Returns:
            List[Dict[str, Any]]: List of row objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If doc_id or table_id is invalid
            
        Example:
            >>> client = CodaClient()
            >>> rows = client.get_table_data("doc_123456", "table_789")
            >>> for row in rows:
            ...     print(f"Row: {row['values']}")
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("Document ID must be a non-empty string")
        if not table_id or not isinstance(table_id, str):
            raise ValueError("Table ID must be a non-empty string")
        
        url = f"{self.base_url}/docs/{doc_id}/tables/{table_id}/rows"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            data = ErrorHandler.handle_response(response, "Coda")
            return data.get('items', [])
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get table data for {doc_id}/{table_id}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def create_row(self, doc_id: str, table_id: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new row in a table.
        
        Args:
            doc_id (str): The ID of the document
            table_id (str): The ID of the table
            row_data (Dict[str, Any]): The row data to insert
            
        Returns:
            Dict[str, Any]: The created row object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If required parameters are missing
            
        Example:
            >>> client = CodaClient()
            >>> new_row = client.create_row("doc_123456", "table_789", {
            ...     "Name": "John Doe",
            ...     "Email": "john@example.com",
            ...     "Status": "Active"
            ... })
            >>> print(f"Created row with ID: {new_row['id']}")
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("Document ID must be a non-empty string")
        if not table_id or not isinstance(table_id, str):
            raise ValueError("Table ID must be a non-empty string")
        
        validate_input(row_data, [], "row_data")
        
        url = f"{self.base_url}/docs/{doc_id}/tables/{table_id}/rows"
        payload = {"rows": [{"values": row_data}]}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            data = ErrorHandler.handle_response(response, "Coda")
            return data.get('rows', [{}])[0] if data.get('rows') else {}
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create row in {doc_id}/{table_id}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def update_row(self, doc_id: str, table_id: str, row_id: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing row in a table.
        
        Args:
            doc_id (str): The ID of the document
            table_id (str): The ID of the table
            row_id (str): The ID of the row to update
            row_data (Dict[str, Any]): The updated row data
            
        Returns:
            Dict[str, Any]: The updated row object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If required parameters are missing
            
        Example:
            >>> client = CodaClient()
            >>> updated_row = client.update_row("doc_123456", "table_789", "row_123", {
            ...     "Status": "Inactive"
            ... })
            >>> print(f"Updated row: {updated_row['id']}")
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("Document ID must be a non-empty string")
        if not table_id or not isinstance(table_id, str):
            raise ValueError("Table ID must be a non-empty string")
        if not row_id or not isinstance(row_id, str):
            raise ValueError("Row ID must be a non-empty string")
        
        validate_input(row_data, [], "row_data")
        
        url = f"{self.base_url}/docs/{doc_id}/tables/{table_id}/rows/{row_id}"
        payload = {"values": row_data}
        
        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=30)
            ErrorHandler.handle_rate_limit(response, "Coda")
            return ErrorHandler.handle_response(response, "Coda")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to update row {row_id} in {doc_id}/{table_id}: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Coda API.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Example:
            >>> client = CodaClient()
            >>> if client.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            # Try to list documents as a connection test
            self.list_documents(limit=1)
            return True
        except Exception:
            return False 