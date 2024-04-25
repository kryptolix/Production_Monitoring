import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# for logging
import csv
from datetime import datetime
from zoneinfo import ZoneInfo
utc = ZoneInfo('UTC')
localtz = ZoneInfo('localtime')

subject    = ""
date       = ""
stueckzahl = ""
wip        = ""

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = '******@gmail.com'

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()

def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages

def read_message(service, message):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Creates a folder for each email based on the subject
        - Downloads text/html content (if available) and saves it under the folder created as index.html
        - Downloads any file that is attached to the email and saves it in the folder created
    """
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
# parts can be the message body, or attachments
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    folder_name = "email"
    has_subject = False
    if headers:
# this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == "subject":
                subject = str(value)
                print("Subject:", value)
            if name.lower() == "date":
                # we print the date when the message was sent
                date = value
                print("Date:", value)
    print("="*50)
    return subject, date
    
def mark_as_read(messages_to_mark):
    return service.users().messages().batchModify(
      userId='me',
      body={
          'ids': [ msg['id']],
          'removeLabelIds': ['UNREAD']
      }
    ).execute()
    
def convert_subject_to_numbers(subject):
    str = subject.split()
    stueckzahl = str[1]
    if len(str) == 4:
        wip = str[3]
    else:
        wip = ""
    return stueckzahl, wip
    
def convert_date_format(date_str):
    utcdate = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
    localdate = utcdate.astimezone(localtz)
    return localdate
    
def write_to_csv(date, stueckzahl, wip):
    with open('monitoring.csv', 'a', newline='\n') as csvfile:
        fieldnames = ['Date', 'Stueckzahl', 'Wip']
        spamwriter = csv.DictWriter(csvfile, fieldnames = fieldnames)
        spamwriter.writerow({'Date': date, 'Stueckzahl': stueckzahl, 'Wip': wip})
        
def write_to_js(date, stueckzahl, wip):
    file = open('main.js', 'r')
    linelist = file.readlines()
    file.close()
    file = open('main.js', 'w')
    for line in linelist:
        if line.startswith("var dates"):
            line = f'{line[:-3]},"{date.strftime("%d.%m.%Y, %H:%M")}"];\n'        
        elif line.startswith("var stueckzahlen"):
            line = f'{line[:-3]},{str(stueckzahl)}];\n'
        elif line.startswith("var wip"):
            line = f'var wip = {str(wip)};\n'
        file.write(line)
    file.close()
	
    
# get emails that match the query you specify
results = search_messages(service, "Stückzahl AND is:unread")
print(f"Found {len(results)} results.")
# for each email matched, read the subject and save the timestamp and numbers to csv and js-file
for msg in reversed(results):
    result = read_message(service, msg)
    date = result[1]
    date = convert_date_format(date)
    subject = result[0]
    stueckzahl, wip = convert_subject_to_numbers(subject)
    write_to_csv(date, stueckzahl, wip)
    write_to_js(date, stueckzahl, wip)
    mark_as_read(msg)
