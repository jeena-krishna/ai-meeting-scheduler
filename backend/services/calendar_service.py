from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates using environment variables (production)
    or falls back to token.pickle (local development)
    """
    creds = None
    
    # Production: Use environment variables
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if refresh_token and client_id and client_secret:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token',
            scopes=SCOPES
        )
        # Refresh to get valid access token
        creds.refresh(Request())
    else:
        # Local development: Use token.pickle
        import pickle
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def check_availability(meeting_details):
    """Check if requested time slot is free, suggest alternatives if busy"""
    try:
        service = get_calendar_service()
        
        meeting_datetime = datetime.strptime(
            f"{meeting_details['date']} {meeting_details['time']}", 
            "%Y-%m-%d %H:%M"
        )
        duration = meeting_details.get('duration', 30)
        end_datetime = meeting_datetime + timedelta(minutes=duration)
        
        # Use timezone-aware format for America/Chicago
        time_min = meeting_datetime.isoformat() + '-05:00'
        time_max = end_datetime.isoformat() + '-05:00'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {'available': True, 'conflicts': [], 'suggested_times': []}
        
        suggested = find_alternative_times(service, meeting_datetime, duration)
        return {
            'available': False,
            'conflicts': [e.get('summary', 'Busy') for e in events],
            'suggested_times': suggested
        }
    except Exception as e:
        print(f"Error checking availability: {e}")
        return {'available': True, 'conflicts': [], 'suggested_times': []}

def find_alternative_times(service, original_time, duration):
    """Find 3 available time slots near the requested time"""
    suggestions = []
    check_time = original_time
    
    for _ in range(10):
        check_time += timedelta(minutes=30)
        end_time = check_time + timedelta(minutes=duration)
        
        time_min = check_time.isoformat() + '-05:00'
        time_max = end_time.isoformat() + '-05:00'
        
        events = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True
        ).execute().get('items', [])
        
        if not events:
            suggestions.append(check_time.strftime("%Y-%m-%d %H:%M"))
            if len(suggestions) >= 3:
                break
    
    return suggestions

def create_calendar_event(meeting_details):
    """Create a Google Calendar event"""
    try:
        service = get_calendar_service()
        
        start_datetime = datetime.strptime(
            f"{meeting_details['date']} {meeting_details['time']}", 
            "%Y-%m-%d %H:%M"
        )
        duration = meeting_details.get('duration', 30)
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        event = {
            'summary': meeting_details.get('title', 'Meeting'),
            'description': meeting_details.get('description', ''),
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'America/Chicago'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'America/Chicago'},
        }
        
        if meeting_details.get('attendees'):
            event['attendees'] = [{'email': e.strip()} for e in meeting_details['attendees'].split(',')]
        
        created = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        
        return {
            'success': True,
            'event_id': created.get('id'),
            'event_link': created.get('htmlLink'),
            'message': f"Meeting '{meeting_details.get('title')}' scheduled for {meeting_details['date']} at {meeting_details['time']}"
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}