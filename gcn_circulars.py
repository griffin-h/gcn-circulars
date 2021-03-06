#!/usr/bin/env python
import requests
import smtplib
from email.mime.text import MIMEText
import time
import re
import os
import sys
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


def get_gcn(gcn_number):
    url = f'https://gcn.gsfc.nasa.gov/gcn3/{gcn_number:3d}.gcn3'
    gcn = requests.get(url)
    return gcn


def send_email(gcn_text, subject):
    msg = MIMEText(gcn_text)
    msg['Subject'] = subject
    gmail_username = 'gcn.circulars@gmail.com'
    me = f'GCN Circulars <{gmail_username}>'
    you = 'gcn-circulars@googlegroups.com'
    msg['From'] = me
    msg['To'] = you

    s = smtplib.SMTP_SSL('smtp.gmail.com')
    s.ehlo()
    s.login(gmail_username, gmail_password)
    s.sendmail(me, [you], msg.as_string())
    s.close()


def get_last_gcn_number():
    with open('last_gcn.txt') as f:
        last_gcn = int(f.read())
    return last_gcn


def store_last_gcn_number(gcn_number):
    with open('last_gcn.txt', 'w') as f:
        f.write(str(gcn_number))


def listen(check_every=60):
    gcn_number = get_last_gcn_number() + 1
    while True:
        try:
            gcn = get_gcn(gcn_number)
        except Exception as e:
            logging.error(e)
            time.sleep(check_every)
            continue
        if gcn.ok:
            subject = re.search('SUBJECT: (.*)', gcn.text).groups()[0]
            logging.info(f'sending GCN {gcn_number:d}')
            send_email(gcn.text, subject)
            store_last_gcn_number(gcn_number)
            gcn_number += 1
        else:
            logging.info(f'GCN {gcn_number:d} {str(gcn)}')
            time.sleep(check_every)


if __name__ == '__main__':
    gmail_password = os.environ['GMAIL_PASSWD']
    if len(sys.argv) == 1:
        check_every = 60
    else:
        check_every = int(sys.argv[1])
    listen(check_every)
