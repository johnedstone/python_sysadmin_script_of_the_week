#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

'''
Template script for sending mail
'''

import argparse
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pprint import pprint

def get_args():
 
    parser = argparse.ArgumentParser(
        description='''

Template for sending mail
Stolen shamelessly from https://docs.python.org/2/library/email-examples.html
''',

        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog =  '''

Example: %(prog)s --msg 'boo hoo'
    ''')

    parser.add_argument('-r', '--recipient', nargs='+', default=['yourname@yourcompany.com',])
    parser.add_argument('-s', '--sender', default='yourname@yourcompany.com')
    parser.add_argument('-m', '--msg', default='hello world')
    parser.add_argument('-l', '--link', default='www.google.com')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    return args

def main(**kwargs):
    args = get_args()
    if args.debug:
        pprint(args)

    for recipient in args.recipient:
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'sample email'
        msg['From'] = args.sender
        msg['To'] = recipient
    
        # Create the body of the message (a plain-text and an HTML version).
        text = '''Hi!
How are you {}?
Here is the link you wanted: https://{}'''.format(recipient, args.link)
    
        html = '''<html>
<head></head>
    <body>
    <div style="margin:0;padding:0;font-family:Calibri, Arial, sans-serif;font-color:#333399">
        <p style="margin:0;padding:0;">
           Hello {}<br>
           This is a sample <a href="https://{}">link</a>.<br>
           This is a sample message: {}.<br>
           Spanish 'my goodness': ¡Dios mío!<br>
           <br>
           This message is an example of a python mail script.<br>
           <br>
           Get this script at <a href="file:///\\samba-server\data\python_sysadmin_script_of_the_week\upcoming">\\\\samba-server\data\python_sysadmin_script_of_the_week\upcoming</a><br>
           and run it on a RHEL7 with --help
        </p>
        <p style="color: #ccc;">
            Stolen shamelessly from <a
            style="color: #ccc;"
            href="https://docs.python.org/2/library/email-examples.html">https://docs.python.org/2/library/email-examples.html</a>
        </p>
    </div>
    </body>
</html>'''.format(recipient, args.link, args.msg)
    
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain', 'utf-8')
        part2 = MIMEText(html, 'html', 'utf-8')
    
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
    
        # Send the message via local SMTP server.
        s = smtplib.SMTP('localhost')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        #s.sendmail(args.sender, recipient, msg.as_string())
        s.sendmail(args.sender, recipient, msg.as_string())
        s.quit()

if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("\nClosing...")

# vim: ai et ts=4 sw=4 sts=4 ru nu
