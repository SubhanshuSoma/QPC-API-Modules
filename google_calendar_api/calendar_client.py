"""
Google Calendar API Client

A comprehensive client for interacting with the Google Calendar API.
Provides calendar and event management with secure authentication
and error handling.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.auth import AuthManager
from utils.error_handling import (
    ErrorHandler, retry_on_failure, validate_input,
    APIError, AuthenticationError, RateLimitError
)


class GoogleCalendarClient:
    """
    Client for interacting with the Google Calendar API.
    
    Provides methods for managing calendars and events.
    Includes secure authentication, error handling, and retry logic.
    """
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize the Google Calendar API client.
        
        Args:
            credentials_file (Optional[str]): Path to credentials file. 
                                           If not provided, will be loaded from environment.
        """
        try:
            self.credentials = AuthManager.get_google_calendar_credentials()
            self.service = build('calendar', 'v3', credentials=self.credentials)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Google Calendar client: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars accessible to the authenticated user.
        
        Returns:
            List[Dict[str, Any]]: List of calendar objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> calendars = client.list_calendars()
            >>> for cal in calendars:
            ...     print(f"Calendar: {cal['summary']} (ID: {cal['id']})")
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.resp.status == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise APIError(f"Failed to list calendars: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error listing calendars: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_calendar(self, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Get detailed information about a specific calendar.
        
        Args:
            calendar_id (str): Calendar ID. Defaults to 'primary'
            
        Returns:
            Dict[str, Any]: Calendar information
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If calendar_id is invalid
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> calendar = client.get_calendar("primary")
            >>> print(f"Calendar: {calendar['summary']}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        
        try:
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            return calendar
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.resp.status == 404:
                raise APIError(f"Calendar not found: {calendar_id}")
            else:
                raise APIError(f"Failed to get calendar {calendar_id}: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error getting calendar: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def list_events(self, calendar_id: str = 'primary', 
                   time_min: Optional[datetime] = None,
                   time_max: Optional[datetime] = None,
                   max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List events from a calendar.
        
        Args:
            calendar_id (str): Calendar ID. Defaults to 'primary'
            time_min (Optional[datetime]): Start time for events
            time_max (Optional[datetime]): End time for events
            max_results (int): Maximum number of events to return
            
        Returns:
            List[Dict[str, Any]]: List of event objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If parameters are invalid
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> events = client.list_events(
            ...     time_min=datetime.now(),
            ...     time_max=datetime.now() + timedelta(days=7)
            ... )
            >>> for event in events:
            ...     print(f"Event: {event['summary']}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        if not isinstance(max_results, int) or max_results < 1:
            raise ValueError("max_results must be a positive integer")
        
        # Set default time range if not provided
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=7)
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.resp.status == 404:
                raise APIError(f"Calendar not found: {calendar_id}")
            else:
                raise APIError(f"Failed to list events: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error listing events: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific event.
        
        Args:
            calendar_id (str): Calendar ID
            event_id (str): Event ID
            
        Returns:
            Dict[str, Any]: Event information
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If calendar_id or event_id is invalid
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> event = client.get_event("primary", "event_123")
            >>> print(f"Event: {event['summary']}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        if not event_id or not isinstance(event_id, str):
            raise ValueError("Event ID must be a non-empty string")
        
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return event
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.resp.status == 404:
                raise APIError(f"Event not found: {event_id}")
            else:
                raise APIError(f"Failed to get event {event_id}: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error getting event: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def create_event(self, calendar_id: str = 'primary',
                    summary: str = None,
                    description: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    attendees: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new event in a calendar.
        
        Args:
            calendar_id (str): Calendar ID. Defaults to 'primary'
            summary (str): Event summary/title
            description (Optional[str]): Event description
            start_time (Optional[datetime]): Event start time
            end_time (Optional[datetime]): Event end time
            attendees (Optional[List[str]]): List of attendee email addresses
            
        Returns:
            Dict[str, Any]: The created event object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If required parameters are missing
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> event = client.create_event(
            ...     summary="Team Meeting",
            ...     description="Weekly team sync",
            ...     start_time=datetime.now() + timedelta(hours=1),
            ...     end_time=datetime.now() + timedelta(hours=2),
            ...     attendees=["team@example.com"]
            ... )
            >>> print(f"Created event: {event['id']}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        if not summary or not isinstance(summary, str):
            raise ValueError("Summary must be a non-empty string")
        
        # Set default times if not provided
        if not start_time:
            start_time = datetime.utcnow() + timedelta(hours=1)
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            }
        }
        
        if description:
            event['description'] = description
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            return event
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            else:
                raise APIError(f"Failed to create event: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error creating event: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def update_event(self, calendar_id: str, event_id: str,
                    summary: Optional[str] = None,
                    description: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Update an existing event.
        
        Args:
            calendar_id (str): Calendar ID
            event_id (str): Event ID
            summary (Optional[str]): New event summary
            description (Optional[str]): New event description
            start_time (Optional[datetime]): New start time
            end_time (Optional[datetime]): New end time
            
        Returns:
            Dict[str, Any]: The updated event object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If calendar_id or event_id is invalid
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> updated_event = client.update_event(
            ...     "primary", "event_123",
            ...     summary="Updated Meeting Title"
            ... )
            >>> print(f"Updated event: {updated_event['id']}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        if not event_id or not isinstance(event_id, str):
            raise ValueError("Event ID must be a non-empty string")
        
        # Get current event first
        try:
            event = self.get_event(calendar_id, event_id)
        except APIError as e:
            raise APIError(f"Could not get event for update: {e}")
        
        # Update fields if provided
        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if start_time:
            event['start']['dateTime'] = start_time.isoformat()
        if end_time:
            event['end']['dateTime'] = end_time.isoformat()
        
        try:
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            return updated_event
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            else:
                raise APIError(f"Failed to update event {event_id}: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error updating event: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """
        Delete an event from a calendar.
        
        Args:
            calendar_id (str): Calendar ID
            event_id (str): Event ID
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If calendar_id or event_id is invalid
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> success = client.delete_event("primary", "event_123")
            >>> print(f"Event deleted: {success}")
        """
        if not calendar_id or not isinstance(calendar_id, str):
            raise ValueError("Calendar ID must be a non-empty string")
        if not event_id or not isinstance(event_id, str):
            raise ValueError("Event ID must be a non-empty string")
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as e:
            if e.resp.status == 401 or e.resp.status == 403:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.resp.status == 404:
                raise APIError(f"Event not found: {event_id}")
            else:
                raise APIError(f"Failed to delete event {event_id}: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error deleting event: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Google Calendar API.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Example:
            >>> client = GoogleCalendarClient()
            >>> if client.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            # Try to list calendars as a connection test
            self.list_calendars()
            return True
        except Exception:
            return False 