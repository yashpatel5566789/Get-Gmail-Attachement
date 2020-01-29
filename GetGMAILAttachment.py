from __future__ import print_function
import requests
import pprint
from apiclient import errors
import base64
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def GetAttachments(service, user_id, msg_id, store_dir):
  """Get and store attachment from Message with given id.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    store_dir: The directory used to store attachments.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    for part in message['payload']['parts']:
        if part['filename']:
            if 'data' in part['body']:
                data = part['body']['data']
            else:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(
                    userId=user_id, messageId=msg_id, id=att_id).execute()
                data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = part['filename']

            with open(path, 'wb') as f:
                f.write(file_data)

  except errors.HttpError():
      print('An error occurred: %s' % sys.exe_info()[0])


def GetMessageId(service, user_id, query):

    messageId = '16ff298d78e221d6'

    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        
        # print(response)
        # print(response['messages'][0]['id'])
        messageId = response['messages'][0]['id']

        return messageId

    except errors.HttpError():
        print('An error occurred: %s' % sys.exe_info()[0])


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    user_email_which_got_email = 'eexzon14@gmail.com'
    query_string = 'from:colabstuffs@gmail.com'

    message_id = GetMessageId(
        service, user_email_which_got_email, query_string)

    GetAttachments(service, user_email_which_got_email, message_id, os.getcwd())


if __name__ == '__main__':
    main()
