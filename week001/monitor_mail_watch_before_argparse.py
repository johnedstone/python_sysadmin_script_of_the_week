#!/usr/bin/python
from __future__ import print_function

'''
Monitoring until Oasis Monitoring is confirmed
'''

import os
import shlex
import smtplib
import sys
import time

from datetime import datetime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

DEBUG = False
ITERATIONS = 3
SLEEP = 300 
MAIL_MSG = ''
OUTPUT = ''

lock_file = '/var/tmp/ose_monitor.lock'
if os.path.exists(lock_file):
    print('LOCK Exists.  Either this script is running or the script has detected an OSE error', file=sys.stderr)
    print('Remove this file to continue: {}'.format(lock_file), file=sys.stderr)
    sys.exit(1)

hostname = '{{ ansible_hostname }}'
scripts_to_monitor = [
    '/usr/local/bin/Some-Prefix_ose_monitor_pods_default.sh',
    '/usr/local/bin/Some-Prefix_ose_monitor_pods_logging.sh',
    '/usr/local/bin/Some-Prefix_ose_monitor_pods_openshift-infra.sh',
    '/usr/local/bin/Some-Prefix_ose_monitor_cluster_health.sh',

]

def send_email(mail_msg, subject='pod and cluster health alert'):
    mail_to = ['yourname@yourcompany.com',
              ]
    msg = MIMEText(mail_msg)
    msg['Subject'] = subject 
    msg['From'] = 'Openshift Monitoring Team'
    msg['To'] = ','.join(mail_to)
    s = smtplib.SMTP('localhost')
    s.sendmail('pod and cluster moniter', mail_to, msg.as_string())
    s.quit()

try:
    start = datetime.now()
    with open(lock_file, 'w') as ose_lock:
        for number in range(0,ITERATIONS):
            for script in scripts_to_monitor:
                cmd = shlex.split(script)
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                results = '''stdout: {}\nstderr: {}\nreturn code: {}\n'''.format(stdout, stderr, p.returncode)
    
                if DEBUG:
                    print(results)
    
                if p.returncode:
                    OUTPUT  += results
                    ose_lock.write(results)
    
            time.sleep(SLEEP)
    
except Exception as e:
    err = '\nEXCEPTION: {}\n'.format(e)
    OUTPUT += err
    if DEBUG:
        print('EXCEPTION: {}\nOUTPUT:{}'.format(err, OUTPUT))
    fh = open(lock_file, 'a')
    fh.write(err)
    fh.write('\n')
    fh.close()

finally:
    end = datetime.now()

    if OUTPUT or os.stat(lock_file).st_size > 0: 
        MAIL_MSG = '''Start: {}
{}
End:{}
REMOVE LOCK FILE TO RESUME MONITORING: {}
HOST: {}
'''.format(start, OUTPUT, end, lock_file, hostname)

        send_email(MAIL_MSG, 'host:{} - OSE Pod and Cluster Health monitoring: {}'.format(hostname, end))

    if os.stat(lock_file).st_size == 0:
        os.remove(lock_file)

# vim: ai et ts=4 sw=4 sts=4 nu
