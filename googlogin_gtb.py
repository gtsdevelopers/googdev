from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import base64
import email
import datetime
from apiclient import errors


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

EMAIL_FOLDER = "FIDO CREDIT"
detach_dir = '/var/goog_folders/GTB'
if not os.path.exists(detach_dir):
    os.makedirs(detach_dir)

OUTPUT_DIRECTORY = detach_dir 
MCOUNT = 1
""" DATEAFTER INCLUSIVE but DATEBEFORE not INCLUDED """
#DATEAFTER = '2017/1/12'
DATEAFTER = ''
# DATEBEFORE = '2017/1/13'
DATEBEFORE = ''
QUERYSTMT = 'label:fido-credit from:(GeNS@gtbank.com) (Credit transaction)'
# QUERYSTMT = QUERYSTMT + DATEAFTER +' before:' + DATEBEFORE 

# if 'fcmb' not in os.listdir(detach_dir):
#    os.mkdir(OUTPUT_DIRECTORY)



def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def GetMessage(service, user_id, msg_id,labelid,num):
    """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        print('Message snippet: %s' % message['snippet'])
        OUTDIR = OUTPUT_DIRECTORY + '/' + labelid
        if labelid not in os.listdir(OUTDIR):
            os.mkdir(OUTDIR)
        f = open('%s/%s.eml' %(OUTDIR, num), 'wb')
        f.write(message['snippet'])
        f.close()


        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def GetMimeMessage(service, user_id, msg_id,labelid,num):
    """Get a Message given id and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

        # print ('Message snippet: %s' % message['snippet'])
        """
        for m in message:
            print("Message content: %s" % m)
        """
        
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        OUTDIR = OUTPUT_DIRECTORY + '/' + labelid 
        if labelid not in os.listdir(OUTPUT_DIRECTORY):
            os.mkdir(OUTDIR)
        filename = OUTDIR + '/' + str(num) + '.eml'
        f = open('%s' % filename, 'wb')
        
        mime_msg = email.message_from_string(msg_str)
        payl = ""
        if mime_msg.is_multipart():
            nn = 0
            for payload in mime_msg.get_payload():
                nn = nn + 1
                print ('1 writing to file %s',filename)
                if nn == 2:
                    payl   = payl +  payload.get_payload(decode=1)
                    
                else:
                    nn = nn + 1
                    
                    
            f.write(payl)
        else:
            print ('2 writing to file %s',filename)
            f.write(mime_msg.get_payload(decode=1))
        f.close()

        return mime_msg
    except errors.HttpError, error:
        print ('An error occurred: %s' % error)
    
    
def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    num = 0
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            labelname= label['name']
            labelid = label['id']
            print(labelname, labelid)
                    
            if labelname == 'FIDO CREDIT':                
                response = service.users().messages().list(userId="me",labelIds=labelid,
                        q = QUERYSTMT).execute()
                print('Message Size Estimate for ', labelname)
                print(response['resultSizeEstimate'])
                messages = []
                if 'messages' in response:
                    messages.extend(response['messages'])
                while 'nextPageToken' in response:
                    page_token = response['nextPageToken']
                    response = service.users().messages().list(userId="me",labelIds=labelid,
                        q = QUERYSTMT,pageToken=page_token).execute()
                    messages.extend(response['messages'])
                print('Number of Messages in Label %s'% len(messages))
                for mesg in messages:
                    num = num + 1
                    print ('num is %s' % num)
                #   GetMessage(service, "me", mesg['id'],num)
                    GetMimeMessage(service, "me", mesg['id'],labelid,num)
            
if __name__ == '__main__':
    main()
