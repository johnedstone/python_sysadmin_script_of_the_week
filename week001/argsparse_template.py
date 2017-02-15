#!/usr/bin/python
from __future__ import print_function

'''
Template script for argsparse and subprocess
'''

import argparse
import shlex

from subprocess import Popen, PIPE
from time import sleep

def get_args():
 
    parser = argparse.ArgumentParser(
        description='''

Simple hello world which can be used as a template for argsparse and subprocess
''',

        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog =  '''

Example: %(prog)s --msg 'boo hoo'
    ''')

  #  parser.add_argument('-m', '--msg', default='hello world',
  #      help='default: "hello world" ')
  #  parser.add_argument('-d', '--debug', action='store_true')


    args = parser.parse_args()

    return args

def main(**kwargs):
    args = get_args()

    try:
        cmd = shlex.split('/bin/echo {}'.format(args.msg))
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if args.debug:
            sleep(10)

    except Exception as e:
        print('Exception: {}'.format(e))
    finally:
        print('stdout: {}'.format(stdout))
        print('stderr: {}'.format(stderr))
        print('return code: {}'.format(p.returncode))

if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("\nClosing...")

# vim: ai et ts=4 sw=4 sts=4 ru 
