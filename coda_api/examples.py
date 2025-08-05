"""
Coda API Examples

This module provides comprehensive examples of how to use the Coda API client.
All examples include error handling and best practices.
"""

import os
from typing import Dict, List, Any
from coda_client import CodaClient
from utils.error_handling import APIError, AuthenticationError, RateLimitError


def basic_usage_example():
    """
    Basic usage example showing how to initialize and use the Coda client.
    """
    print("=== Coda API Basic Usage Example ===\n")
    
    try:
        # Initialize the client
        client = CodaClient()
        print("✓ Coda client initialized successfully")
        
        # Test connection
        if client.test_connection():
            print("✓ Connection to Coda API successful")
        else:
            print("✗ Connection to Coda API failed")
            return
        
        # List documents
        print("\n--- Listing Documents ---")
        documents = client.list_documents(limit=5)
        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"  - {doc.get('name', 'Unknown')} (ID: {doc.get('id', 'Unknown')})")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def document_management_example():
    """
    Example showing document management operations.
    """
    print("\n=== Document Management Example ===\n")
    
    try:
        client = CodaClient()
        
        # Get a specific document (replace with actual document ID)
        doc_id = "doc_example123"
        print(f"--- Getting Document Details ---")
        print(f"Attempting to get document: {doc_id}")
        
        # Note: This will fail with a real API call since we don't have actual credentials
        # but demonstrates the usage pattern
        try:
            document = client.get_document(doc_id)
            print(f"Document: {document.get('name', 'Unknown')}")
            print(f"Owner: {document.get('owner', 'Unknown')}")
            print(f"Created: {document.get('createdAt', 'Unknown')}")
        except APIError as e:
            print(f"Document not found or access denied: {e}")
        
    except Exception as e:
        print(f"✗ Error in document management: {e}")


def table_operations_example():
    """
    Example showing table operations including listing tables and managing data.
    """
    print("\n=== Table Operations Example ===\n")
    
    try:
        client = CodaClient()
        doc_id = "doc_example123"
        
        # List tables in a document
        print(f"--- Listing Tables in Document ---")
        print(f"Document ID: {doc_id}")
        
        try:
            tables = client.list_tables(doc_id)
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table.get('name', 'Unknown')} (ID: {table.get('id', 'Unknown')})")
        except APIError as e:
            print(f"Could not list tables: {e}")
        
        # Get table data
        table_id = "table_example456"
        print(f"\n--- Getting Table Data ---")
        print(f"Table ID: {table_id}")
        
        try:
            rows = client.get_table_data(doc_id, table_id, limit=10)
            print(f"Found {len(rows)} rows:")
            for i, row in enumerate(rows, 1):
                values = row.get('values', {})
                print(f"  Row {i}: {values}")
        except APIError as e:
            print(f"Could not get table data: {e}")
        
    except Exception as e:
        print(f"✗ Error in table operations: {e}")


def data_management_example():
    """
    Example showing how to create and update data in tables.
    """
    print("\n=== Data Management Example ===\n")
    
    try:
        client = CodaClient()
        doc_id = "doc_example123"
        table_id = "table_example456"
        
        # Example row data
        new_row_data = {
            "Name": "John Doe",
            "Email": "john.doe@example.com",
            "Department": "Engineering",
            "Status": "Active"
        }
        
        print(f"--- Creating New Row ---")
        print(f"Document ID: {doc_id}")
        print(f"Table ID: {table_id}")
        print(f"Row data: {new_row_data}")
        
        try:
            # Create a new row
            new_row = client.create_row(doc_id, table_id, new_row_data)
            print(f"✓ Created row with ID: {new_row.get('id', 'Unknown')}")
            
            # Update the row
            row_id = new_row.get('id')
            if row_id:
                print(f"\n--- Updating Row ---")
                update_data = {"Status": "Inactive"}
                updated_row = client.update_row(doc_id, table_id, row_id, update_data)
                print(f"✓ Updated row: {updated_row.get('id', 'Unknown')}")
                
        except APIError as e:
            print(f"Could not manage data: {e}")
        
    except Exception as e:
        print(f"✗ Error in data management: {e}")


def error_handling_example():
    """
    Example showing proper error handling for different scenarios.
    """
    print("\n=== Error Handling Example ===\n")
    
    try:
        client = CodaClient()
        
        # Test with invalid document ID
        print("--- Testing with Invalid Document ID ---")
        try:
            client.get_document("invalid_doc_id")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid table ID
        print("\n--- Testing with Invalid Table ID ---")
        try:
            client.get_table_data("doc_123", "invalid_table_id")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid row data
        print("\n--- Testing with Invalid Row Data ---")
        try:
            client.create_row("doc_123", "table_456", None)
        except ValueError as e:
            print(f"✓ Properly caught validation error: {e}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def rate_limiting_example():
    """
    Example showing how the client handles rate limiting.
    """
    print("\n=== Rate Limiting Example ===\n")
    
    try:
        client = CodaClient()
        
        print("--- Testing Rate Limit Handling ---")
        print("Making multiple requests to test rate limiting...")
        
        # Make multiple requests to potentially trigger rate limiting
        for i in range(5):
            try:
                documents = client.list_documents(limit=1)
                print(f"  Request {i+1}: Success")
            except RateLimitError as e:
                print(f"  Request {i+1}: Rate limited - {e}")
                break
            except APIError as e:
                print(f"  Request {i+1}: API error - {e}")
                break
        
    except Exception as e:
        print(f"✗ Error in rate limiting test: {e}")


def main():
    """
    Run all examples.
    """
    print("Coda API Examples")
    print("=" * 50)
    
    # Run all examples
    basic_usage_example()
    document_management_example()
    table_operations_example()
    data_management_example()
    error_handling_example()
    rate_limiting_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main() 