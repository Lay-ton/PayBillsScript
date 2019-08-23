from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
import re

bills = 'Label_181438259144754670'
reciepts = 'Label_6181614655454590488'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def verifyCreds() :
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
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def getSpectrumBill() :
    # Call the Gmail API and looks at all emails that have Spectrum in the subject
    service = build('gmail', 'v1', credentials=verifyCreds())
    results = service.users().messages().list(userId='me',labelIds=['UNREAD'], q=['subject: Spectrum']).execute()
    messages = results.get('messages', [])

    for message in messages :
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers=msg["payload"]["headers"]
        for subject in headers :
            if subject["name"] == "Subject":
                #print(subject['value'])
                if re.search("Spectrum", subject['value']) : # Spectrum (internet bill)
                    for part in msg['payload']['parts'] :
                        if part['mimeType'] == "text/plain" :
                            textBody = (base64.urlsafe_b64decode(part['body']['data'].encode('ASCII'))).decode('utf-8')
                            dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(Debit Date)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group()).group()
                            amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(Amount Due)(.*)([0-9]+\.[0-9]+)", textBody).group()).group()
                            #print(dateDue + '\n' + amountDue)
                            #service.users().messages().modify(userId='me', id=message['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()
                            return (dateDue, amountDue)
    return None

def getWaterBill() :
    # Call the Gmail API and looks at all emails that have Current Bill Period in the subject
    service = build('gmail', 'v1', credentials=verifyCreds())
    results = service.users().messages().list(userId='me',labelIds=['UNREAD'], q=['subject: Current Bill Period']).execute()
    messages = results.get('messages', [])

    for message in messages :
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers=msg["payload"]["headers"]
        for subject in headers :
            if subject["name"] == "Subject":
                #print(subject['value'])
                if re.search("(Current Bill Period)", subject['value']) : # Utilities (water bill)
                    for part in msg['payload']['parts'] :
                        if part['mimeType'] == "multipart/alternative" :
                            textBody = (base64.urlsafe_b64decode(part["parts"][0]["body"]["data"].encode('ASCII'))).decode('utf-8')
                            dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(DUE DATE:)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group()).group()
                            amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(AMOUNT DUE:)(.*)([0-9]+\.[0-9]+)", textBody).group()).group()
                            #print(dateDue + '\n' + amountDue)
                            #service.users().messages().modify(userId='me', id=message['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()
                            return (dateDue, amountDue)
    return None

def getElectricBill() :
    # Call the Gmail API and looks at all emails that have Utilities in the subject
    service = build('gmail', 'v1', credentials=verifyCreds())
    results = service.users().messages().list(userId='me',labelIds=['UNREAD'], q=['subject: Utilities']).execute()
    messages = results.get('messages', [])
    for message in messages :
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers=msg["payload"]["headers"]
        for subject in headers :
            if subject["name"] == "Subject":
                #print(subject['value'])
                if re.search("Utilities", subject['value']) :
                    if msg['payload']['mimeType'] == "text/html" : # Utilities (electric bill)
                        textBody = (base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('ASCII'))).decode('utf-8')
                        dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(Due Date:)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group()).group()
                        amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(Total Amount Due:)(.*)([0-9]+\.[0-9]+)", textBody).group()).group()
                        #print(dateDue + '\n' + amountDue)
                        #service.users().messages().modify(userId='me', id=message['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()
                        return (dateDue, amountDue)
    return None

# A sort of useless function just for testing and learning gmail API
def getAllBills() :
    # Call the Gmail API and looks at all emails that are unread in Bills or Receipts
    service = build('gmail', 'v1', credentials=verifyCreds())
    results = service.users().messages().list(userId='me',labelIds=['UNREAD'], q=['label: Bills OR label: Receipts']).execute()
    messages = results.get('messages', [])

    if messages:
        # Itterates through each message
        for message in messages :
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            # Finds the subject of each email
            headers=msg["payload"]["headers"]
            for subject in headers :
                if subject["name"] == "Subject":
                    print(subject['value'])
                    print(msg['payload']['mimeType'])
                    if re.search("Spectrum", subject['value']) : # Spectrum (internet bill)
                        for part in msg['payload']['parts'] :
                            print(part['mimeType'])
                            if part['mimeType'] == "text/plain" :
                                textBody = (base64.urlsafe_b64decode(part['body']['data'].encode('ASCII'))).decode('utf-8')
                                dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(Debit Date)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group())
                                amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(Amount Due)(.*)([0-9]+\.[0-9]+)", textBody).group())
                                print(dateDue.group())
                                print(amountDue.group())
                                break

                    elif re.search("(Current Bill Period)", subject['value']) : # Utilities (water bill)
                        for part in msg['payload']['parts'] :
                            print(part['mimeType'])
                            if part['mimeType'] == "multipart/alternative" :
                                textBody = (base64.urlsafe_b64decode(part["parts"][0]["body"]["data"].encode('ASCII'))).decode('utf-8')
                                dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(DUE DATE:)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group())
                                amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(AMOUNT DUE:)(.*)([0-9]+\.[0-9]+)", textBody).group())
                                print(dateDue.group())
                                print(amountDue.group())
                                break

                    elif re.search("Utilities", subject['value']) :
                        if msg['payload']['mimeType'] == "text/html" : # Utilities (electric bill)
                            textBody = (base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('ASCII'))).decode('utf-8')
                            dateDue = re.search("([0-9]+\/[0-9]+\/[0-9]+)", re.search("(Due Date:)(.*)([0-9]+\/[0-9]+\/[0-9]+)", textBody).group())
                            amountDue = re.search("([0-9]+\.[0-9]+)", re.search("(Total Amount Due:)(.*)([0-9]+\.[0-9]+)", textBody).group())
                            print(dateDue.group())
                            print(amountDue.group())

# TODO ----------------------------------------
# Need to write a funciton to get the paylease reciept confirm that the bill was paid in db
# TODO ----------------------------------------
