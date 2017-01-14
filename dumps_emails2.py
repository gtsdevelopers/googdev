#!/usr/bin/env python
#
# Very simple Python script to dump all emails in an IMAP folder to files.  
# This code is released into the public domain.
#
# RKI Nov 2013
#

import sys
import imaplib
import getpass
import email
import os
import datetime
from tkFileDialog import Directory
from __builtin__ import file

IMAP_SERVER = 'imap.gmail.com'
EMAIL_ACCOUNT = "filatei@gtsng.com"
EMAIL_FOLDER = "FCMB CREDIT"
detach_dir = '/tmp/imap'
if not os.path.exists(detach_dir):
    os.makedirs(detach_dir)

if 'fcmb' not in os.listdir(detach_dir):
    os.mkdir('/tmp/imap/fcmb')

OUTPUT_DIRECTORY = '/tmp/imap/fcmb'

PASSWORD = getpass.getpass()


def process_mailbox(M):
  rv, data = M.search(None, "ALL")
  if rv != 'OK':
      print "No messages found!"
      return

  for num in data[0].split():
    rv, data = M.fetch(num, '(RFC822)')
    if rv != 'OK':
        print "ERROR getting message", num
        return
    f = open('%s/%s.eml' %(OUTPUT_DIRECTORY, num), 'wb')
    
    
    
    msg = email.message_from_string(data[0][1])
 #   print 'Message %s: %s' % (num, msg['Subject'])
  #  print 'Raw Date:', msg['Date']
    ff = open('%s/%s.eml' %(OUTPUT_DIRECTORY, num), 'wb').write(msg['Subject'])
    f.write(msg['Date'])
    print "Subject", msg['Subject'], " - ", msg['Date']     
          
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        #print "Local Date:", \
        #    local_date.strftime("%a, %d %b %Y %H:%M:%S")
    if msg.is_multipart():
        for payload in msg.get_payload():
        # if payload.is_multipart(): ...
    #        print payload.get_payload(decode=1)
            f.write(payload.get_payload(decode=1))
    else:
        f.write(msg.get_payload(decode=1))
        
   #     f.write(data[0][1])
    f.close()

def main():
    M = imaplib.IMAP4_SSL(IMAP_SERVER)
    M.login(EMAIL_ACCOUNT, PASSWORD)
    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print "Processing mailbox: ", EMAIL_FOLDER
        process_mailbox(M)
        M.close()
    else:
        print "ERROR: Unable to open mailbox ", rv
    M.logout()
    

if __name__ == "__main__":
    main()
"""
# Authorize server-to-server interactions from Google Compute Engine.
from oauth2client.contrib import gce

credentials = gce.AppAssertionCredentials(
 scope='https://www.googleapis.com/auth/devstorage.read_write')
 http = credentials.authorize(httplib2.Http())
"""



"""
import oauth2
import json
import zope.interface

MY_GMAIL = "filatei@gtsng.com"
REFRESH_TOKEN_SECRET_FILE = '/home/filatei/googdev/refresh.json'
CLIENT_SECRET_FILE = '/home/filatei/googdev/client_secret.json'

class GmailOAuthAuthenticator():
    zope.interface.implements(imap4.IClientAuthentication)

    authName     = "XOAUTH2"
    tokenTimeout = 3300      # 5 mins short of the real timeout (1 hour)

    def __init__(self, reactr):
        self.token   = None
        self.reactor = reactr
        self.expire  = None

    @defer.inlineCallbacks
    def getToken(self):

        if ( (self.token==None) or (self.reactor.seconds() > self.expire) ):
            rt = None
            with open(REFRESH_TOKEN_SECRET_FILE) as f:
                rt = json.load(f)

            cl = None
            with open(CLIENT_SECRET_FILE) as f:
                cl = json.load(f)

            self.token = yield threads.deferToThread(
                oauth2.RefreshToken,
                client_id = cl['installed']['client_id'], 
                client_secret = cl['installed']['client_secret'],
                refresh_token = rt['Refresh Token'] )

            self.expire = self.reactor.seconds() + self.tokenTimeout


    def getName(self):
        return self.authName

    def challengeResponse(self, secret, chal):
        # we MUST already have the token
        # (allow an exception to be thrown if not)

        t = self.token['access_token']

        ret = oauth2.GenerateOAuth2String(MY_GMAIL, t, False)

        return ret
        
    def buildProtocol(self, addr):
        p = self.protocol(self.ctx)
        p.factory = self
        x = GmailOAuthAuthenticator(self.reactor)
        p.registerAuthenticator(x)
        return p
        
        
    @defer.inlineCallbacks
    def serverGreeting(self, caps):
        # log in
        try:
            # the line below no longer works for gmail
            # yield self.login(mailuser, mailpass)
            if GmailOAuthAuthenticator.authName in self.authenticators:
                yield self.authenticators[AriGmailOAuthAuthenticator.authName].getToken()

            yield self.authenticate("")

            try:
                yield self.uponAuthentication()
            except Exception as e:
                uponFail(e, "uponAuthentication")
        except Exception as e:
            uponFail(e, "logging in") 
        """