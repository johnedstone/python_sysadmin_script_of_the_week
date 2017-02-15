#!/usr/bin/python
from __future__ import print_function

'''
Monitoring until Oasis Monitoring is confirmed
'''

import argparse
import os
import shlex
import smtplib
import sys
import time

from collections import defaultdict
from datetime import datetime
from email.mime.text import MIMEText
from pprint import pprint
from subprocess import Popen, PIPE

def get_args():
 
    parser = argparse.ArgumentParser(
        description='''
This script is run by cron to double check Oasis monitoring or 
can be called by hand to monitor pods and cluster health.

This script calls several monitoring scripts and if there are
more than 2 errors, after 3 iterations, per script, will email
that there is a problem
''',

        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog =  '''

Monitoring from the cli:
%(prog)s --debug --disregard-file-lock --disable-mail -i 1 -s 0
    ''')

    parser.add_argument('-i', '--iterations', type=int, default=3,
        help='default: 3 iterations')
    parser.add_argument('-s', '--sleep', type=int, default=300,
        help='default: 300 sec (5 min)')
    parser.add_argument('--disregard-file-lock', action='store_true',
        help='This will disregard any locked files and will not create a lock file')
    parser.add_argument('--disable-mail', action='store_true',
        help='Stops any mail from being sent')
    parser.add_argument('-d', '--debug', action='store_true',
        help='Prints data to stdout')

    args = parser.parse_args()

    return args

def main(**kwargs):
    args = get_args()

    mail_msg = ''
    output = ''
    err = ''

    # https://www.accelebrate.com/blog/using-defaultdict-python/
    # https://docs.python.org/3/library/collections.html#collections.defaultdict
    monitor_error_count = defaultdict(int) # default value of int is 0
    
    lock_file = '/var/tmp/ose_monitor.lock'
    if not args.disregard_file_lock:
        if os.path.exists(lock_file):
            print('LOCK Exists.  Either this script is running or the script has detected an OSE error',
                file=sys.stderr)
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
        for i, number in enumerate(range(0,args.iterations)):
            iterate_msg = 'Iteration: {}\n{}\n'.format(i + 1, '#' * 16)
            if args.debug:
                print(iterate_msg)
            output += iterate_msg
            for script in scripts_to_monitor:
                # if args.debug:
                #     print(script)
                cmd = shlex.split(script)
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                results = '''stdout: {}\nstderr: {}\nreturn code: {}\n'''.format(stdout, stderr, p.returncode)
                output  += results
    
                if args.debug:
                    print(results)
    
                if p.returncode:
                    monitor_error_count[script] += 1
    
            time.sleep(args.sleep)
        
    except Exception as e:
        err = '\nEXCEPTION: {}\n'.format(e)
        if args.debug:
            print('EXCEPTION: {}'.format(err))
        if not args.disregard_file_lock:
            fh = open(lock_file, 'w')
            fh.write(err)
            fh.write('\n')
            fh.close()
    
    finally:
        if args.debug:
            pprint(monitor_error_count)
            pprint(monitor_error_count.viewvalues())
    
        end = datetime.now()
    
        if err or any(i > 2 for i in monitor_error_count.viewvalues()):
            if args.debug:
                pprint('Writing erroring output to lock file and sending email to notify that there are => 3 failurs')
    
            if not args.disregard_file_lock:
                fh = open(lock_file, 'a')
                fh.write(output)
                fh.write('\n')
                fh.close()
    
            if not args.disable_mail:
                mail_msg = '''Start: {}
OUTPUT: {}
EXCEPTION: {}
End:{}
REMOVE LOCK FILE TO RESUME MONITORING: {}
HOST: {}
'''.format(start, output, err, end, lock_file, hostname)
    
                send_email(mail_msg, 'host:{} - OSE Pod and Cluster Health monitoring: {}'.format(hostname, end))
    
        # In theory, this is not needed, as if there is no error or exceptions the file is 0
        # if os.path.exists(lock_file):
        #     if os.stat(lock_file).st_size == 0:
        #        os.remove(lock_file)

if __name__ == '__main__':
    # print('__main__ DRY RUN: {} - LOG: {} - SUMMARY: {}'.format(DRY_RUN, LOG, SUMMARY))
    try:
        main()

    except KeyboardInterrupt:
        print("\nClosing...")

# vim: ai et ts=4 sw=4 sts=4 nu
