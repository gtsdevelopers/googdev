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

import dateutil.parser
from dateutil.parser import parse
from bs4 import BeautifulSoup
import argparse
import numpy
from docutils.parsers import null
from time import strftime

"""
 This program will process a mailbox named 'FIDO CREDIT'
 Extract all credit mails from Banks
 Create a csv file or output of transactions for each bank
 

"""
try:
    import argparse
    parser = argparse.ArgumentParser(description='Mailbox2csv for Transactions from Banks in Mailbox')
    parser.add_argument('-b','--bank', help='Bank Name eg GTBANK or STANBIC or FCMB or STERLING', required=True)
    parser.add_argument('-e','--extended', help='-e 1 is optional and allows to process not only today transactions', required=False)
    
    args = vars(parser.parse_args())
except ImportError:
    parser = None

if args['extended'] == '1':
    EXTENDED = True
else:
    EXTENDED = False
    
if args['bank'].upper() == 'GTBANK':
    BANKNAME = 'GTBANK'
    
    print ('processing ... ',args['bank'])
    
elif args['bank'].upper() == 'STANBIC':
    BANKNAME = 'STANBIC'
    print ('processing ... ',args['bank'])
    
elif args['bank'].upper() == 'FCMB':
    BANKNAME = 'FCMB'
    print ('processing ... ',args['bank'])
    
elif args['bank'].upper() == 'STERLING':
    BANKNAME = 'STERLING'
    print ('processing ... ',args['bank'])

else:
    print ('NOT YET SUPPORTED ',args['bank'])
    raise SystemExit

FILENAME = BANKNAME + '_' + (datetime.today() ).strftime("%Y%m%d") +'.csv'
FILETXT = BANKNAME + '_' + (datetime.today() ).strftime("%Y%m%d") +'.txt'
# FILENAME = BANKNAME + '_' + (datetime.today() - timedelta(days=1)).strftime("%Y%m%d") +'.csv'
ALLTXT = BANKNAME + '_'  +'ALL.txt'

TOTAMT = 0.0
TITLE = 'SN,DATE,NAME,AMOUNT,CREDIT,BANK,REFNO'
def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

format = '%d-%b-%Y %H:%M:%S'
EMAIL_FOLDER = "FIDO CREDIT"
# EMAIL_FOLDER = "Inbox"
detach_dir = '/var/www/tellers/BANKS'
detach_dir_txt = '/var/www/tellers/BANKS/TXT'

if not os.path.exists(detach_dir):
    os.makedirs(detach_dir)
if not os.path.exists(detach_dir_txt):
    os.makedirs(detach_dir_txt)


OUTDIR = detach_dir
OUTDIRTXT = detach_dir_txt

MCOUNT = 1
TOD = datetime.today()
STODAY = TOD.strftime('%d-%b-%Y')
TODAY = datetime.strptime(STODAY,'%d-%b-%Y')
DAY = TODAY.strftime('%d')
DATEAFTER = datetime.today() - timedelta(days=3)
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
    QUERYSTMT = 'from:(StanbicIBTC-E-Alert@stanbic.com) Credit Alert'
    QUERYSTMT = QUERYSTMT + DATEAFTER + DATEBEFORE 

elif BANKNAME == 'STERLING':
    QUERYSTMT = 'label:fido-credit subject:(CREDIT ALERT ON (00632XXXX4))'
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


def process_gtb(message,num):
    bankname = 'GTBANK'
    global TOTAMT
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
        if process_nextline == 2:
            text = text.replace("NGN ","")
            text = text.replace(",","")
            text = text.replace('CASH DEPOSIT',"CREDIT")
            text = text.replace('TRANSFER (CSH DEPOSIT BY ',"")
            text = text.replace('CASH LODGEMENT (CDP ',"")
                         
            text = text.replace(")","")
            prt[data] = text                           
            process_nextline = 0
        
                      
    if is_date(prt['Date']) and prt['Date'] != "": 
        
        prtr = datetime.strptime(prt['Date'],'%d-%b-%Y')
        
        if EXTENDED:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        
        
        if prtr == TODAY:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        else:
            return None
    else:
        return None

def process_fcmb(message,num):
    bankname = 'FCMB'
    global TOTAMT
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
                prt[data] = textdt.strftime("%d-%b-%Y") 
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
                prt[data] =  text 
            process_nextline = 0
    if prt['Date'] != "":
        
        prtr = datetime.strptime(prt['Date'],'%d-%b-%Y')
        
        if EXTENDED:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
            
        if prtr == TODAY:
           
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        else:
            return None
    else:
        return None
                            
def process_stanbic(message,num):
    bankname = 'STANBIC'
    global TOTAMT
    result = "Date,Description,Amount,Credit,Bank,Refno\n"
    prt = {}
    prt['Date'] = ""
    prt['Amount'] = ""
    prt['Name'] = ""
    prt['Ref'] = ""
    prt['Credit'] = ""
    prtt = ""
    encoding = None
    # print (message)
    message = '<html>' + message + '</html>'
    soup = BeautifulSoup(message,'html.parser')
     
    process_nextline = 0
    for text in soup.stripped_strings:
        text = text.encode('ascii',errors='ignore')
        
        if ('Debit Alert' in text):
            return None
        
        if ('Credit alert' in text):
            data = 'Credit'
            text = text.replace(" alert on XXXXXX5014","")
            
            prt[data] = text
            data = 'Name'
            process_nextline = 1
            continue
            
        if ('Dear FIDO PRODUCING' in text):
            data = 'Amount'
            process_nextline = 1
            continue
        
        if 'This transaction took' in text:
            data = 'Date'
            process_nextline = 1
            continue
        
        if 'Transaction Reference' in text:
            data = 'Ref'
            process_nextline = 1
            continue
                
        if process_nextline == 1:
            if data == 'Name':
                text = text.replace('Description: ',"")
                prt[data] = text
    
            if data == 'Date':
                prt[data] = text
            if data == 'Ref':
                prt[data] = text
            if data == 'Amount':
                text = text.replace("NGN ","")
                text = text.replace(",","")
                prt[data] = text
                
            process_nextline = 0
    
    if prt['Date'] != "":
    
        if ('FIDO PRODUCING'.lower() in prt['Name'].lower()) or ('REV' in prt['Name']) or ('INTERSWITCHNG' in prt['Name']):
            prt['Amount'] = '0'
        
        
        prtd = prt['Date']
        prta = dateutil.parser.parse(prtd)
        prtd = prta.strftime('%d-%b-%Y')
        prtr = datetime.strptime(prtd,'%d-%b-%Y')
        
        prt['Date'] = prtd
        
        if EXTENDED:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ','  +bankname+ ',' +prt['Ref'] 
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        if prtr == TODAY:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit']  +',' + bankname+ ','+ prt['Ref']
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        else:
            return None
    else:
        return None

def process_sterling(message,num):
    bankname = 'STERLING'
    global TOTAMT
    prt = {}
    prt['Date'] = ""
    prt['Amount'] = ""
    prt['Name'] = ""    
    prt['Credit'] = ""
    prtt = ""    
    encoding = None
    soup = BeautifulSoup(message,'html.parser')
                    
    process_nextline = 0
    for text in soup.stripped_strings:
        text = text.encode('ascii',errors='ignore')
        
        if ('Deposit Cash (Local Currency)' in text) or  ('Transfer In' in text):
            process_nextline = 1
            data = 'Name'
            continue
        if ('Transaction Date' in text):
            process_nextline = 1
            data = 'Date'
            continue
        
        if ('Amount' in text):
            process_nextline = 1
            data = 'Amount'
            continue
        
        if ('Remarks' in text):
            process_nextline = 0
            data = 'Name'
            
            continue
                
        if process_nextline == 1:            
            text = text.replace("NGN ","")
            text = text.replace(",","")
            text = text.replace('TRANSFER (CSH DEPOSIT BY : ',"")
            text = text.replace('DEP BY ',"")
            text = text.replace('CASH LODGEMENT (CDP ',"")
            text = text.replace('CASH LODGEMENT (CDB ',"")
            text = text.replace('CASH LODGEMENT (CDP BY ',"")
            text = text.replace('CASH LODGEMENT (CDB BY ',"")
                         
            text = text.replace(")","")
            prt[data] = text 
            process_nextline = 0
    if prt['Date'] != "":
            
        prtdd = prt['Date'].lstrip()
        prtd = dateutil.parser.parse(prtdd)
        
        prtdd = prtd.strftime('%d-%b-%Y')
        prtr = datetime.strptime(prtdd,'%d-%b-%Y')
        prt['Date'] = prtdd
        
        """
        for Historical Data not just today        
     
        prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
        TOTAMT = TOTAMT + float(prt['Amount'])        
        print (prtt)
        return prtt
        """
        if EXTENDED:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        
        if prtr == TODAY:
            prtt = str(num) + ','+  prt['Date'] + ','  + prt['Name'] + ',' + prt['Amount'] + ',' + prt['Credit'] + ',' + bankname
            TOTAMT = TOTAMT + float(prt['Amount'])        
            print (prtt)
            return prtt
        else:
            return None
    else:
        return None



def process_bank(message,bankname,num):
    if bankname == 'GTBANK':
        prtt = process_gtb(message,num)
        return prtt
    elif bankname == 'FCMB':
        prtt = process_fcmb(message,num)
        return prtt
    elif bankname == 'STANBIC':
        prtt = process_stanbic(message,num)
        return prtt
    elif bankname == 'STERLING':
        prtt = process_sterling(message,num)
        return prtt

    else:
        print ('WRONG BANK NAME')
        return ""
    
    
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
        # OUTDIR = OUTPUT_DIRECTORY + '/' + SUBFOLDER 
        #if SUBFOLDER not in os.listdir(OUTPUT_DIRECTORY):
         #   os.mkdir(OUTDIR)
        #filename = OUTDIR + '/' + str(num) + '.eml'
        #f = open('%s' % filename, 'wb')
        
        mime_msg = email.message_from_string(msg_str)
        if mime_msg.is_multipart():
            for payload in mime_msg.get_payload():
             #   print ('1 processing message %s',filename)        
                # f.write(payload.get_payload(decode=1))
                prtt = process_bank(payload.get_payload(decode=1),bankname,num)
        else:
        #    print ('2. processing Message %s',filename)            
            prtt = process_bank(mime_msg.get_payload(decode=1), bankname,num)
            
        #f.close()

        return prtt
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
    f = open('%s/%s' %(OUTDIR, FILENAME), 'wb')
    ft = open('%s/%s' %(OUTDIRTXT, FILETXT), 'wb')
    fall = open('%s/%s' % (OUTDIRTXT, ALLTXT), 'a')

    f.write(TITLE + "\n")
    ft.write(TITLE + "\n")
    print(TITLE)
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
                    prtt = GetMimeMessage(service, "me", mesg['id'],labelid,num,BANKNAME)
                    if prtt != None:
                        f.write(prtt + "\n")
                        ft.write(prtt + "\n")
                        fall.write(prtt + "\n")
    f.close()
    ft.close()
    fall.close()
    print('TOTAL AMOUNT',TOTAMT)        
if __name__ == '__main__':
    main()
