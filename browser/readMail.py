from __future__ import print_function
import pickle
import os.path
import base64
import email
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

bills = 'Label_181438259144754670'
reciepts = 'Label_6181614655454590488'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
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
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API and looks at all emails that are unread in Bills or Receipts
    results = service.users().messages().list(userId='me',labelIds=['UNREAD'], q=['label: Bills OR label: Receipts']).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        print('Messages:')
        # Itterates through each message
        for message in messages :
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            # Finds the subject of each email
            headers=msg["payload"]["headers"]
            for subject in headers :
                if subject["name"] == "Subject":
                    print(subject['value'])
                    print(msg['payload']['mimeType'])
                    if re.search("Spectrum", subject['value']) :
                        for part in msg['payload']['parts'] :
                            print(part['mimeType'])
                            if part['mimeType'] == "text/plain" : # Spectrum
                                textBody = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII'))
                                print(textBody)
                    elif re.search("Utilities", subject['value']) :
                        if msg['payload']['mimeType'] == "text/html" : # Utilities
                            textBody = (base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('ASCII'))).decode('utf-8')
                            dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(Due Date:)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group())
                            amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(Total Amount Due:)(.*)([0-9]+\.[0-9]+)", textBody).group())
                            print(dateDue.group())
                            print(amountDue.group())


            # msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            # print(msg['labelIds'])
            #
            # print(msg['payload']['mimeType'])
            # print(len(msg['payload']['parts']))
            # for part in msg['payload']['parts'] :
            #     print(part['mimeType'])
                # if part['mimeType'] == "text/plain" : # Spectrum
                #     print(base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')))
                # elif part['mimeType'] == "multipart/alternative" : # Water bill
                #     print(base64.urlsafe_b64decode(part['parts'][0]['body']['data'].encode('ASCII')))

            #bodys = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            #bodys = email.message_from_bytes(bodys)

            #print(bodys)
            # payld = msg['payload'] # get payload of the message
            # print('Message snippet: %s' % msg['snippet'])
            # print(base64.b64decode(msg['payload']['parts'][0]['body']['data']))

if __name__ == '__main__':
    main()
