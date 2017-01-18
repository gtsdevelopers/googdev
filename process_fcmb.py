#!/usr/bin/env python
#
# Very simple Python script to process  emails file 
# in FCMB CREDIT folder.
#

from dateutil.parser import parse
import sys
import datetime
import imaplib
import getpass
import os
from tkFileDialog import Directory
from __builtin__ import file
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

path = '/var/goog_folders/FCMB'
format = '%d-%b-%Y %H:%M:%S'
BANK = 'FCMB'
SUBFOLDER = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
path = path + '/' + SUBFOLDER
# PASSWORD = getpass.getpass()

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False
    
def process_file():
    result = "Date,Description,Amount,Credit\n"
    for file in os.listdir(path):
        current_file = os.path.join(path,file)
        encoding = None
        
        if os.path.isfile(current_file):
                        
            soup = BeautifulSoup(open(current_file),'html.parser')
            
           
            k = 0
            stext = ""
            prt = ""
            process_nextline = 0
            for text in soup.stripped_strings:
                text = text.encode('ascii',errors='ignore')               
                
                if process_nextline == 1:
                    
                    # print text
                    if is_date(text):
                        textdt = datetime.strptime(text,format)
                        prt = prt + textdt.strftime("%d-%b-%Y") + ","
                    
                    elif ('Credit' in text):                        
                        prt = prt + text + ""
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
                        prt = prt + text + ","
                    process_nextline = 0
                if ('Date/time' in text) or ('Description' in text) or ('Amount' in text) or ('Credit/Debit' in text):
                    process_nextline = 1
                    
            prt = prt +',' + BANK
            print prt
            
                
def main():
    process_file()

if __name__ == "__main__":
    main()
