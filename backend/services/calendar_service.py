from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import pickle

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates and returns Google Calendar service
    First time: Opens browser for login
    After: Uses saved credentials
    """
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This will open browser for Google login
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return calendar service
    service = build('calendar', 'v3', credentials=creds)
    return service

def check_availability(meeting_details):
    """
    Check if the requested time slot is free
    If busy, suggest 3 nearby alternative times
    """
    try:
        service = get_calendar_service()
        
        # Parse the meeting time
        meeting_datetime = datetime.strptime(
            f"{meeting_details['date']} {meeting_details['time']}", 
            "%Y-%m-%d %H:%M"
        )
        duration = meeting_details.get('duration', 30)
        end_datetime = meeting_datetime + timedelta(minutes=duration)
        
        # Query a wider time range - just the day of the meeting
        day_start = meeting_datetime.replace(hour=0, minute=0, second=0)
        day_end = meeting_datetime.replace(hour=23, minute=59, second=59)
        
        # Format with RFC3339 format (add Z for UTC)
        events_result = service.events().list(
            calendarId='primary',
            timeMin=day_start.strftime('%Y-%m-%dT%H:%M:%S') + 'Z',
            timeMax=day_end.strftime('%Y-%m-%dT%H:%M:%S') + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Check for actual overlaps
        conflicts = []
        print(f"Checking for conflicts. Requested time: {meeting_datetime} to {end_datetime}")
        print(f"Found {len(events)} events on this day")
        
        for event in events:
            # Get event times
            start_str = event['start'].get('dateTime', event['start'].get('date'))
            end_str = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse event times (remove timezone for comparison)
            if 'T' in start_str:
                event_start = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                event_end = datetime.fromisoformat(end_str.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                continue  # Skip all-day events
            
            print(f"Event: {event.get('summary')} from {event_start} to {event_end}")
            
            # Check if events overlap
            if (meeting_datetime < event_end) and (end_datetime > event_start):
                print(f"CONFLICT DETECTED with {event.get('summary')}")
                conflicts.append({
                    'summary': event.get('summary', 'Busy'),
                    'start': event_start.strftime('%Y-%m-%d %H:%M'),
                    'end': event_end.strftime('%Y-%m-%d %H:%M')
                })
        
        # If no conflicts, slot is available
        if not conflicts:
            print("No conflicts found - slot is available")
            return {
                'available': True,
                'conflicts': [],
                'suggested_times': []
            }
        
        # If conflicts exist, find alternative times
        print(f"Total conflicts found: {len(conflicts)}")
        
        suggested_times = find_alternative_slots(
            service, 
            meeting_datetime, 
            duration
        )
        
        return {
            'available': False,
            'conflicts': conflicts,
            'suggested_times': suggested_times
        }
        
    except Exception as e:
        print(f"Error checking availability: {e}")
        raise Exception(f"Calendar check failed: {str(e)}")

def find_alternative_slots(service, original_time, duration):
    """
    Find 3 nearby free time slots
    Search: 30 min before and after the requested time
    """
    suggestions = []
    search_intervals = [-60, -30, 30, 60, 90, 120]  # minutes before/after
    
    for offset in search_intervals:
        if len(suggestions) >= 3:
            break
        
        # Calculate alternative time
        alt_time = original_time + timedelta(minutes=offset)
        alt_end = alt_time + timedelta(minutes=duration)
        
        # Check if this slot is free
        events_result = service.events().list(
            calendarId='primary',
            timeMin=alt_time.isoformat() + 'Z',
            timeMax=alt_end.isoformat() + 'Z',
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        
        # If free, add to suggestions
        if not events:
            suggestions.append({
                'date': alt_time.strftime('%Y-%m-%d'),
                'time': alt_time.strftime('%H:%M'),
                'formatted': alt_time.strftime('%I:%M %p on %B %d, %Y')
            })
    
    return suggestions

def create_meeting(meeting_details):
    """
    Creates the meeting in Google Calendar
    Returns the calendar event link
    """
    try:
        service = get_calendar_service()
        
        # Parse datetime
        start_datetime = datetime.strptime(
            f"{meeting_details['date']} {meeting_details['time']}", 
            "%Y-%m-%d %H:%M"
        )
        duration = meeting_details.get('duration', 30)
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Create event object
        event = {
            'summary': meeting_details.get('title', 'Meeting'),
            'description': f"Scheduled via AI Meeting Scheduler",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/New_York',  # Change to your timezone
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/New_York',
            },
            'attendees': [
                {'email': meeting_details.get('attendee')}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        # Insert event into calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        print(f"Meeting created: {event.get('htmlLink')}")
        return event.get('htmlLink')
        
    except Exception as e:
        print(f"Error creating meeting: {e}")
        raise Exception(f"Failed to create meeting: {str(e)}")