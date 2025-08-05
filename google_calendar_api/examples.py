"""
Google Calendar API Examples

This module provides comprehensive examples of how to use the Google Calendar API client.
All examples include error handling and best practices.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from calendar_client import GoogleCalendarClient
from utils.error_handling import APIError, AuthenticationError, RateLimitError


def basic_usage_example():
    """
    Basic usage example showing how to initialize and use the Google Calendar client.
    """
    print("=== Google Calendar API Basic Usage Example ===\n")
    
    try:
        # Initialize the client
        client = GoogleCalendarClient()
        print("✓ Google Calendar client initialized successfully")
        
        # Test connection
        if client.test_connection():
            print("✓ Connection to Google Calendar API successful")
        else:
            print("✗ Connection to Google Calendar API failed")
            return
        
        # List calendars
        print("\n--- Listing Calendars ---")
        calendars = client.list_calendars()
        print(f"Found {len(calendars)} calendars:")
        for cal in calendars:
            print(f"  - {cal.get('summary', 'Unknown')} (ID: {cal.get('id', 'Unknown')})")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def calendar_management_example():
    """
    Example showing calendar management operations.
    """
    print("\n=== Calendar Management Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        # Get primary calendar details
        print("--- Getting Primary Calendar Details ---")
        try:
            calendar = client.get_calendar("primary")
            print(f"Calendar: {calendar.get('summary', 'Unknown')}")
            print(f"Description: {calendar.get('description', 'No description')}")
            print(f"Time Zone: {calendar.get('timeZone', 'Unknown')}")
            print(f"Access Role: {calendar.get('accessRole', 'Unknown')}")
        except APIError as e:
            print(f"Could not get calendar details: {e}")
        
        # List all calendars with details
        print(f"\n--- All Available Calendars ---")
        try:
            calendars = client.list_calendars()
            for cal in calendars:
                print(f"Calendar: {cal.get('summary', 'Unknown')}")
                print(f"  ID: {cal.get('id', 'Unknown')}")
                print(f"  Description: {cal.get('description', 'No description')}")
                print(f"  Access Role: {cal.get('accessRole', 'Unknown')}")
                print(f"  Primary: {cal.get('primary', False)}")
                print()
        except APIError as e:
            print(f"Could not list calendars: {e}")
        
    except Exception as e:
        print(f"✗ Error in calendar management: {e}")


def event_management_example():
    """
    Example showing event management operations.
    """
    print("\n=== Event Management Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        # List upcoming events
        print("--- Listing Upcoming Events ---")
        try:
            # Get events for the next 7 days
            time_min = datetime.utcnow()
            time_max = time_min + timedelta(days=7)
            
            events = client.list_events(
                calendar_id="primary",
                time_min=time_min,
                time_max=time_max,
                max_results=10
            )
            
            print(f"Found {len(events)} upcoming events:")
            for event in events:
                summary = event.get('summary', 'No title')
                start = event.get('start', {}).get('dateTime', 'No start time')
                print(f"  - {summary} (Start: {start})")
        except APIError as e:
            print(f"Could not list events: {e}")
        
        # Create a new event (commented out to avoid actual creation)
        print(f"\n--- Event Creation Example ---")
        print("Note: Event creation is commented out to avoid actual creation")
        """
        try:
            new_event = client.create_event(
                calendar_id="primary",
                summary="Test Meeting",
                description="This is a test event created via API",
                start_time=datetime.utcnow() + timedelta(hours=1),
                end_time=datetime.utcnow() + timedelta(hours=2),
                attendees=["test@example.com"]
            )
            print(f"Created event: {new_event.get('id', 'Unknown')}")
            print(f"Event URL: {new_event.get('htmlLink', 'No URL')}")
        except APIError as e:
            print(f"Could not create event: {e}")
        """
        
    except Exception as e:
        print(f"✗ Error in event management: {e}")


def event_crud_example():
    """
    Example showing complete CRUD operations for events.
    """
    print("\n=== Event CRUD Operations Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        # Create event
        print("--- Creating Event ---")
        print("Note: Event creation is commented out to avoid actual creation")
        """
        try:
            event = client.create_event(
                calendar_id="primary",
                summary="Team Meeting",
                description="Weekly team sync meeting",
                start_time=datetime.utcnow() + timedelta(hours=1),
                end_time=datetime.utcnow() + timedelta(hours=2),
                attendees=["team@example.com", "manager@example.com"]
            )
            event_id = event.get('id')
            print(f"Created event with ID: {event_id}")
            
            # Read event
            print(f"\n--- Reading Event ---")
            retrieved_event = client.get_event("primary", event_id)
            print(f"Event: {retrieved_event.get('summary', 'Unknown')}")
            print(f"Description: {retrieved_event.get('description', 'No description')}")
            print(f"Start: {retrieved_event.get('start', {}).get('dateTime', 'Unknown')}")
            print(f"End: {retrieved_event.get('end', {}).get('dateTime', 'Unknown')}")
            
            # Update event
            print(f"\n--- Updating Event ---")
            updated_event = client.update_event(
                calendar_id="primary",
                event_id=event_id,
                summary="Updated Team Meeting",
                description="Updated weekly team sync meeting"
            )
            print(f"Updated event: {updated_event.get('summary', 'Unknown')}")
            
            # Delete event
            print(f"\n--- Deleting Event ---")
            success = client.delete_event("primary", event_id)
            print(f"Event deleted: {success}")
            
        except APIError as e:
            print(f"Error in CRUD operations: {e}")
        """
        
    except Exception as e:
        print(f"✗ Error in event CRUD operations: {e}")


def time_range_queries_example():
    """
    Example showing how to query events in different time ranges.
    """
    print("\n=== Time Range Queries Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        # Today's events
        print("--- Today's Events ---")
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            events = client.list_events(
                calendar_id="primary",
                time_min=today_start,
                time_max=today_end,
                max_results=5
            )
            
            print(f"Found {len(events)} events today:")
            for event in events:
                summary = event.get('summary', 'No title')
                start = event.get('start', {}).get('dateTime', 'No start time')
                print(f"  - {summary} (Start: {start})")
        except APIError as e:
            print(f"Could not get today's events: {e}")
        
        # This week's events
        print(f"\n--- This Week's Events ---")
        try:
            week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = week_start - timedelta(days=week_start.weekday())  # Monday
            week_end = week_start + timedelta(days=7)
            
            events = client.list_events(
                calendar_id="primary",
                time_min=week_start,
                time_max=week_end,
                max_results=10
            )
            
            print(f"Found {len(events)} events this week:")
            for event in events:
                summary = event.get('summary', 'No title')
                start = event.get('start', {}).get('dateTime', 'No start time')
                print(f"  - {summary} (Start: {start})")
        except APIError as e:
            print(f"Could not get this week's events: {e}")
        
    except Exception as e:
        print(f"✗ Error in time range queries: {e}")


def error_handling_example():
    """
    Example showing proper error handling for different scenarios.
    """
    print("\n=== Error Handling Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        # Test with invalid calendar ID
        print("--- Testing with Invalid Calendar ID ---")
        try:
            client.get_calendar("invalid_calendar_id_12345")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid event ID
        print("\n--- Testing with Invalid Event ID ---")
        try:
            client.get_event("primary", "invalid_event_id_12345")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid parameters
        print("\n--- Testing with Invalid Parameters ---")
        try:
            client.list_events(calendar_id="primary", max_results=0)
        except ValueError as e:
            print(f"✓ Properly caught validation error: {e}")
        
        # Test with invalid calendar ID for events
        print("\n--- Testing with Invalid Calendar ID for Events ---")
        try:
            client.list_events(calendar_id="invalid_calendar_id_12345")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def rate_limiting_example():
    """
    Example showing how the client handles rate limiting.
    """
    print("\n=== Rate Limiting Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        print("--- Testing Rate Limit Handling ---")
        print("Making multiple requests to test rate limiting...")
        
        # Make multiple requests to potentially trigger rate limiting
        for i in range(5):
            try:
                calendars = client.list_calendars()
                print(f"  Request {i+1}: Success - Found {len(calendars)} calendars")
            except RateLimitError as e:
                print(f"  Request {i+1}: Rate limited - {e}")
                break
            except APIError as e:
                print(f"  Request {i+1}: API error - {e}")
                break
        
    except Exception as e:
        print(f"✗ Error in rate limiting test: {e}")


def advanced_event_example():
    """
    Example showing advanced event features like recurring events and attendees.
    """
    print("\n=== Advanced Event Features Example ===\n")
    
    try:
        client = GoogleCalendarClient()
        
        print("--- Advanced Event Creation Example ---")
        print("Note: Advanced event creation is commented out to avoid actual creation")
        """
        try:
            # Create event with multiple attendees
            event = client.create_event(
                calendar_id="primary",
                summary="Project Review Meeting",
                description="Monthly project review with stakeholders",
                start_time=datetime.utcnow() + timedelta(days=1, hours=10),
                end_time=datetime.utcnow() + timedelta(days=1, hours=11),
                attendees=[
                    "stakeholder1@example.com",
                    "stakeholder2@example.com",
                    "team@example.com"
                ]
            )
            print(f"Created advanced event: {event.get('summary', 'Unknown')}")
            print(f"Event ID: {event.get('id', 'Unknown')}")
            print(f"Event URL: {event.get('htmlLink', 'No URL')}")
            
            # Show attendee information
            attendees = event.get('attendees', [])
            print(f"Attendees ({len(attendees)}):")
            for attendee in attendees:
                email = attendee.get('email', 'Unknown')
                response_status = attendee.get('responseStatus', 'Unknown')
                print(f"  - {email} ({response_status})")
                
        except APIError as e:
            print(f"Could not create advanced event: {e}")
        """
        
    except Exception as e:
        print(f"✗ Error in advanced event example: {e}")


def main():
    """
    Run all examples.
    """
    print("Google Calendar API Examples")
    print("=" * 50)
    
    # Run all examples
    basic_usage_example()
    calendar_management_example()
    event_management_example()
    event_crud_example()
    time_range_queries_example()
    error_handling_example()
    rate_limiting_example()
    advanced_event_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main() 