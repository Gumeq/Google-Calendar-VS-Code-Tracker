import time
import datetime
import os
import pickle
import psutil
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from plyer import notification

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def format_duration(start_time, end_time):
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    
    if hours > 0:
        return f'Coding time: {int(hours)}h {int(minutes)}m'
    else:
        return f'Coding time: {int(minutes)}m'

def create_event(service, start_time, end_time):
    event_title = format_duration(start_time, end_time)
    
    event = {
        'summary': event_title,
        'description': 'Time spent using VS Code',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'colorId': '7',  # Set the color to Peacock
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    log_message(f'Event created: {event.get("htmlLink")}')
    show_notification("VS Code Tracker", f"Event created: {event_title} from {start_time} to {end_time}")

def is_vscode_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'code' in process.info['name'].lower():
            return True
    return False

def log_message(message):
    with open("vscode_tracker.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now(datetime.timezone.utc)} - {message}\n")

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=3  # Duration in seconds
    )

def main():
    service = authenticate_google_calendar()
    vscode_open = False
    start_time = None

    show_notification("VS Code Tracker", "VS Code usage tracking has started.")
    log_message("Script started and notification sent")

    while True:
        vscode_running = is_vscode_running()
        log_message(f"VS Code running: {vscode_running}")

        if vscode_running and not vscode_open:
            vscode_open = True
            start_time = datetime.datetime.now(datetime.timezone.utc)
            log_message(f"VS Code opened at {start_time}")

        elif not vscode_running and vscode_open:
            vscode_open = False
            end_time = datetime.datetime.now(datetime.timezone.utc)
            log_message(f"VS Code closed at {end_time}")
            create_event(service, start_time, end_time)
            start_time = None

        time.sleep(60)  # Check every 60 seconds

if __name__ == '__main__':
    main()
