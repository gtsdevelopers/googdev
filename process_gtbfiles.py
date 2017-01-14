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
from bs4 import BeautifulSoup

path = '/var/goog_folders/GTB/Label_18'
format = '%m-%d-%Y %H:%M:%S %p'
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
                if ('We wish to inform you that a Credit transaction occurred' in text):
                    text = text.replace("We wish to inform you that a ","")
                    text = text.replace(" transaction occurred","")
                    prt = prt + text + ","
                                
                if process_nextline == 1:
                    text = text.replace(")","")                          
                    prt = prt + text + ","
                    process_nextline = 0
                if ('Value Date' in text) or ('Remarks' in text) or ('Amount' in text) or ('Account Number' in text):
                    process_nextline = 1
                    
            print prt
            
                
def main():
    process_file()

if __name__ == "__main__":
    main()
