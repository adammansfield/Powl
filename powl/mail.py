#!/usr/bin/env python
"""To get email from a mailbox and to send emails."""
#import ConfigParser
#import email
import errno
import imaplib
#import logging
#import optparse
#import os
#import re
#import shutil
import socket
import sys
#import textwrap
#import time
import powl.logger as logger
#import powl.output as output
#from powl.config import Config
#from powl.processors.transaction import Transaction



class Mail:
    """To get email from a mailbox and to send emails."""

    # CONSTANTS
    _timeout = 5

    # EXCEPTIONS
    class MailError(Exception): pass
    class EmptyServer(MailError): pass
    class EmptyAddress(MailError): pass
    class EmptyPassword(MailError): pass
    class ServerUnknownError(MailError): pass
    class ServerTimedOutError(MailError): pass
    class LoginFailure(MailError): pass


    def get_messages(self):
        """Get a list of unread email messages."""


    # FETCHING
    def process(self):
        """Parse through an inbox of emails."""
        search_response, email_ids = self.imap.search(None, "(Unseen)")
        logger.info("PROCESSING INBOX")
        for email_id in email_ids[0].split():
            fetch_response, data = self.imap.fetch(email_id, "(RFC822)")
            mail = email.message_from_string(data[0][1])
            date = email.utils.parsedate(mail['Date'])
            for part in mail.walk():
                if part.get_content_type() == 'text/html':
                    body = part.get_payload()
                    message = self.strip_message_markup(body)
                    logger.debug('EMAIL   %s', message.strip())
                    self.parse_message(message, date)

    def _strip_message_markup(self, message):
        """Return message striped of markup."""
        retval = message
        retval = retval.replace('<P>','')
        retval = retval.replace('</P>','')
        retval = retval.replace('=0A',' ')
        retval = retval.replace('&amp;','&')
        return retval

    # SETUP
    def setup(self):
        """Get imap server, login and select mailbox."""
        try:
            self._get_imap()
            self._login()
        except MailError as e:
            logger.error(e)
            sys.exit(e)

    def _login(self):
        """Login to imap server and select mailbox."""
        if not self._address:
            raise self.EmptyAddress("Empty Address.")
        elif not self._password:
            raise self.EmptyPassword("Empty Password.")
        else:
            try:    
                self._imap.login(self._address, self._password)
            except imaplib.IMAP4.error as e:
                if "Invalid credentials" in str(e):
                    message = (
                        "{0} {1} are invalid creditials.".format(self._address,
                                                                 self._password)
                    )
                    raise self.LoginFailure(message)

    def _get_imap(self):
        """Attempt to get imap object."""
        if not self._server:
            raise self.EmptyServer("Imap server has not been set.")
        else:
            try:
                self._imap = imaplib.IMAP4_SSL(self._server)
            except socket.gaierror as (code, message):
                if code == socket.EAI_NONAME:
                    message = self._server + " not found."
                    raise self.ServerUnknownError(message)
            except socket.timeout:
                message = self._server + " has timed out."
                raise self.ServerTimedOutError(message)

    # INTIALIZATION
    def __init__(self, server, address, password):
        self._server = server
        self._address = address
        self._password = password
        socket.setdefaulttimeout(self._timeout)
#
#
#        self.imap.select(self.config.mailbox)
