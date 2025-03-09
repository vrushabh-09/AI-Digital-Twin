"""
Google Calendar integration module
Handles authentication and event fetching from Google Calendar API
"""

import os
import logging
from datetime import datetime
from typing import List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pytz

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarService:
    """Singleton class for Google Calendar integration"""
    _instance = None
    _service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GoogleCalendarService, cls).__new__(cls)
            cls._timezone = pytz.timezone(
                os.getenv("TIMEZONE", "Asia/Kolkata"))
        return cls._instance

    @property
    def service(self):
        """Lazy-loaded calendar service"""
        if not self._service:
            self._service = self._authenticate()
        return self._service

    def _authenticate(self):
        """Handle OAuth2 authentication flow"""
        creds = None
        token_file = 'token.json'
        credentials_file = os.getenv('GOOGLE_CREDENTIALS', 'credentials.json')

        try:
            if os.path.exists(token_file):
                with open(token_file, 'r', encoding='utf-8') as token:
                    creds = Credentials.from_authorized_user_file(
                        token_file, SCOPES)
                logger.info("Loaded existing credentials from token file")

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logger.info("Refreshed expired credentials")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file,
                        SCOPES,
                        redirect_uri='http://localhost:8501'
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Created new credentials via OAuth flow")

                with open(token_file, 'w', encoding='utf-8') as token:
                    token.write(creds.to_json())

            return build('calendar', 'v3', credentials=creds, cache_discovery=False)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Authentication failed: %s", str(e))
            raise RuntimeError("Calendar authentication failed") from e

    def get_meetings(self, max_results: int = 10) -> List[Dict]:
        """Fetch upcoming meetings with proper timezone handling"""
        try:
            now = datetime.now(self._timezone).isoformat()
            # pylint: disable=no-member
            result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                timeZone=str(self._timezone)
            ).execute()

            return [self._parse_event(event) for event in result.get('items', [])]

        except HttpError as e:
            logger.error("Calendar API Error: %s", str(e))
            raise RuntimeError("Failed to fetch calendar events") from e
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Unexpected error: %s", str(e))
            raise

    def _parse_event(self, event: Dict) -> Dict:
        """Normalize event data structure with timezone awareness"""
        def get_datetime(time_obj):
            if 'dateTime' in time_obj:
                return {
                    'datetime': datetime.fromisoformat(time_obj['dateTime']).astimezone(self._timezone),
                    'is_all_day': False
                }
            if 'date' in time_obj:
                return {
                    'date': datetime.fromisoformat(time_obj['date']).date(),
                    'is_all_day': True
                }
            return None

        return {
            'id': event.get('id', ''),
            'summary': event.get('summary', 'Untitled Meeting'),
            'start': get_datetime(event.get('start', {})),
            'end': get_datetime(event.get('end', {})),
            'description': event.get('description', ''),
            'attendees': [a.get('email', '') for a in event.get('attendees', [])],
            'hangoutLink': event.get('hangoutLink', '')
        }


def get_meetings(max_results: int = 10) -> List[Dict]:
    """Public interface for fetching meetings"""
    return GoogleCalendarService().get_meetings(max_results)
