from __future__ import print_function
import datetime
from tzlocal import get_localzone
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_creds():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_events(creds):

    service = build('calendar', 'v3', credentials=creds)

    #get today's date
    today = datetime.date.today()
    #tmrw = (today + datetime.timedelta(1))

    #hack to get local timezone
    '''
    local_t = datetime.datetime.fromtimestamp(0)
    utc_t = datetime.datetime.utcfromtimestamp(0)
    local_tz = datetime.timezone(local_t - utc_t)
    '''

    local_tz = get_localzone()

    #turn today's date into a datetime set at midnight in local timezone
    today_dt = datetime.datetime.combine(today, datetime.time(0, tzinfo=local_tz))
    #tmrw_dt = today_dt + datetime.timedelta(1)
    day_after_tmrw_dt = today_dt + datetime.timedelta(2)
    
    events_result = service.events().list(calendarId='primary', timeMin=today_dt.isoformat(), timeMax=day_after_tmrw_dt.isoformat(), maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    events_list = []
    if not events:
        pass
    for event in events:
        #if(event['summary'] == 'Work'):
        start = event['start']['dateTime']
        end = event['end']['dateTime']
        events_list.append((event['summary'], start, end))
            #print(event['summary'], start, end)

    return events_list

'''
    print('Getting Tomorrow\'s Work Schedule')
    events_result = service.events().list(calendarId='primary', timeMin=tmrw_dt.isoformat(), timeMax=day_after_tmrw_dt.isoformat(), maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No Work Tomorrow!')
    for event in events:
        if(event['summary'] == 'Work'):
            start = event['start']['dateTime']
            end = event['end']['dateTime']
            events_list.append((event['summary'], start, end))
            print(event['summary'], start, end)
'''

if __name__ == '__main__':
    creds = get_creds()
    print(get_events(creds))