from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import base64
import email
import datetime
from datetime import datetime, timedelta

from apiclient import errors
from sys import argv

from dateutil.parser import parse
from bs4 import BeautifulSoup


"""
 This program will process a mailbox named 'FIDO CREDIT'
 Extract all credit mails from Banks
 Create a csv file or output of transactions for each bank
 

"""
def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

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

format = '%d-%b-%Y %H:%M:%S'
EMAIL_FOLDER = "FIDO CREDIT"
detach_dir = '/var/goog_folders'

if not os.path.exists(detach_dir):
    os.makedirs(detach_dir)

#BANKNAME = 'GTBANK'
#BANKNAME = 'FCMB'
BANKNAME = 'GTBANK'

OUTPUT_DIRECTORY = detach_dir
SUBFOLDER = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d") 
MCOUNT = 1
DATEAFTER = datetime.today() - timedelta(days=1)
DATEAFTER = DATEAFTER.strftime("%Y/%m/%d")
DATEAFTER = ' after:' + DATEAFTER
print('Date after is %s' % DATEAFTER)
# DATEBEFORE = '2017/1/13'
DATEBEFORE = datetime.today() + timedelta(days=1)
DATEBEFORE = DATEBEFORE.strftime("%Y/%m/%d")
DATEBEFORE = ' before:' + DATEBEFORE
print('Date Before is %s' % DATEBEFORE)
QUERYSTMT = ""
if BANKNAME == 'GTBANK':    
    QUERYSTMT = 'label:fido-credit from:(GeNS@gtbank.com) (Credit transaction)'
    QUERYSTMT = QUERYSTMT + DATEAFTER + DATEBEFORE
elif BANKNAME == 'FCMB':
    QUERYSTMT = 'label:fido-credit subject:(Credit Alert: XXXXXX0016) '
    QUERYSTMT = QUERYSTMT + DATEAFTER + DATEBEFORE
 
elif BANKNAME == 'STANBIC':
    QUERYSTMT = 'label:fido-credit from:(StanbicIBTC-E-Alert@stanbic.com) (Transaction Type Credit) -Debit '
    QUERYSTMT = QUERYSTMT + DATEAFTER + DATEBEFORE 


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
        OUTDIR = OUTPUT_DIRECTORY + '/' + SUBFOLDER
        if SUBFOLDER not in os.listdir(OUTDIR):
            os.mkdir(OUTDIR)
        f = open('%s/%s.eml' %(OUTDIR, num), 'wb')
        f.write(message['snippet'])
        f.close()


        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def process_gtb(message):
    bankname = 'GTBANK'
    result = "Date,Description,Amount,Credit,BANK\n"
    prt = {}
    prt['Date'] = ""
    prt['Amount'] = ""
    prt['Name'] = ""    
    prt['Credit'] = ""
    prtt = ""    
    encoding = None
    soup = BeautifulSoup(message,'html.parser')
                    
    soups='<html>' +str(soup.body)+'</html>'
    soup = BeautifulSoup(soups,'html.parser')
    process_nextline = 0
    for text in soup.stripped_strings:
        text = text.encode('ascii',errors='ignore')
        if process_nextline == 1 and (text == ':'):
            process_nextline = 2
            continue
        if process_nextline == 2:
            text = text.replace("NGN ","")
            text = text.replace(",","")
            text = text.replace('CASH DEPOSIT',"CREDIT")
            text = text.replace('TRANSFER (CSH DEPOSIT BY ',"")
            text = text.replace('CASH LODGEMENT (CDP ',"")
                         
            text = text.replace(")","")
            prt[data] = text + ","                          
            process_nextline = 0
                    
        if ('Description' in text):
            process_nextline = 1
            data = 'Credit' 
                
        if ('Amount' in text):
            process_nextline = 1
            data = 'Amount' 
                        
        if ('Value Date' in text): 
            process_nextline = 1
            data = 'Date'
                    
        if ('Remarks' in text):
            process_nextline = 1
            data = 'Name'
                      
    if prt:
        prtt = prt['Date']  + prt['Name'] + prt['Amount'] + prt['Credit'] + bankname 
        print (prtt)

def process_fcmb(message):
    bankname = 'FCMB'
    result = "Date,Description,Amount,Credit,BANK\n"
    prt = {}
    prt['Date'] = ""
    prt['Amount'] = ""
    prt['Name'] = ""    
    prt['Credit'] = ""
    prtt = ""    
    soup = BeautifulSoup(message,'html.parser')
            
    process_nextline = 0
    for text in soup.stripped_strings:
        text = text.encode('ascii',errors='ignore')
                       
        if ('Date/time' in text):
            process_nextline = 1
            data = 'Date'
            continue 
        
        if ('Description' in text):
            process_nextline = 1
            data = 'Name'
            continue
        
        if ('Amount' in text):
            process_nextline = 1
            data = 'Amount'
            continue 
        
        if ('Credit/Debit' in text):
            process_nextline = 1
            data = 'Credit'
            continue

        if process_nextline == 1:
            if is_date(text):
                textdt = datetime.strptime(text,format)
                prt[data] = textdt.strftime("%d-%b-%Y") + ","
            else:
                text = text.replace(" (NGN)","")
                text = text.replace(",","")
                text = text.replace('TRANSFER (CSH DEPOSIT BY : ',"")
                text = text.replace('TRANSFER (CSH DEPOSIT BY ',"")
                text = text.replace('CASH LODGEMENT (CDP ',"")
                text = text.replace('CASH LODGEMENT (CDB ',"")
                text = text.replace('CASH LODGEMENT (CDP BY ',"")
                text = text.replace('CASH LODGEMENT (CDB BY ',"")
                text = text.replace(")","")                          
                prt[data] =  text + ","
            process_nextline = 0
    if prt:
        prtt = prt['Date']  + prt['Name'] + prt['Amount'] + prt['Credit'] + bankname 
        print (prtt)
                            
def process_stanbic(message):
    bankname = 'STANBIC'
    result = "Date,Description,Amount,Credit\n"
    prt = {}
    prt['Date'] = ""
    prt['Amount'] = ""
    prt['Name'] = ""
    prt['Ref'] = ""
    prt['Credit'] = ""
    prtt = ""
    encoding = None
    soup = BeautifulSoup(message,'html.parser')
            
    process_nextline = 0
    for text in soup.stripped_strings:
        text = text.encode('ascii',errors='ignore')
        
        if ('Transaction Type' in text):
            process_nextline = 1
            data = 'Credit'
            continue
        
        if ('Ref. Number' in text):
            process_nextline = 1
            data = 'Ref'
            continue
        
        if ('Amount' in text):
            process_nextline = 1
            data = 'Amount'
            continue
        
        if ('Description' in text):
            process_nextline = 1
            data = 'Name'
            continue
        
        if 'The following transaction took place on your account XXXXXX5014 on' in text:
            data = 'Date'
            text = text.replace("The following transaction took place on your account XXXXXX5014 on","")
            text = text.replace("M:","M")
            prt[data] = text + ","
            process_nextline = 0
            continue
                
        if process_nextline == 1:
            text = text.replace("NGN ","")
            text = text.replace(",","")
            text = text.replace('TRANSFER (CSH DEPOSIT BY : ',"")
            text = text.replace('TRANSFER (CSH DEPOSIT BY ',"")
            text = text.replace('CASH LODGEMENT (CDP ',"")
            text = text.replace('CASH LODGEMENT (CDB ',"")
            text = text.replace('CASH LODGEMENT (CDP BY ',"")
            text = text.replace('CASH LODGEMENT (CDB BY ',"")
                         
            text = text.replace(")","")                          
            prt[data] = text + ","
            process_nextline = 0
    if prt:
        prtt = prt['Date']  + prt['Name'] + prt['Amount'] + prt['Credit'] + bankname + ',' + prt['Ref'] 
        print (prtt)
    
def process_bank(message,bankname):
    if bankname == 'GTBANK':
        process_gtb(message)
    elif bankname == 'FCMB':
        process_fcmb(message)
    elif bankname == 'STANBIC':
        process_stanbic(message)
    else:
        print ('WRONG BANK NAME')
        return
    
    
def GetMimeMessage(service, user_id, msg_id,labelid,num,bankname):
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
        OUTDIR = OUTPUT_DIRECTORY + '/' + SUBFOLDER 
        #if SUBFOLDER not in os.listdir(OUTPUT_DIRECTORY):
         #   os.mkdir(OUTDIR)
        #filename = OUTDIR + '/' + str(num) + '.eml'
        #f = open('%s' % filename, 'wb')
        
        mime_msg = email.message_from_string(msg_str)
        if mime_msg.is_multipart():
            for payload in mime_msg.get_payload():
             #   print ('1 processing message %s',filename)        
                # f.write(payload.get_payload(decode=1))
                process_bank(payload.get_payload(decode=1),bankname)
        else:
        #    print ('2. processing Message %s',filename)            
            process_bank(mime_msg.get_payload(decode=1), bankname)
            
        #f.close()

        return mime_msg
    except errors.HttpError, error:
        print ('An error occurred: %s' % error)

""" PROCES GTB MESSAGE """

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False
    

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
        for label in labels:
            labelname= label['name']
            labelid = label['id']
                    
            if labelname == 'FIDO CREDIT':                
                response = service.users().messages().list(userId="me",labelIds=labelid,
                        q = QUERYSTMT).execute()
          #      print('Message Size Estimate for ', labelname)
          #      print(response['resultSizeEstimate'])
                messages = []
                if 'messages' in response:
                    messages.extend(response['messages'])
                while 'nextPageToken' in response:
                    page_token = response['nextPageToken']
                    response = service.users().messages().list(userId="me",labelIds=labelid,
                        q = QUERYSTMT,pageToken=page_token).execute()
                    messages.extend(response['messages'])
         #       print('Number of Messages in Label %s'% len(messages))
                for mesg in messages:
                    num = num + 1
                #   GetMessage(service, "me", mesg['id'],num)
                    GetMimeMessage(service, "me", mesg['id'],labelid,num,BANKNAME)
            
if __name__ == '__main__':
    main()
