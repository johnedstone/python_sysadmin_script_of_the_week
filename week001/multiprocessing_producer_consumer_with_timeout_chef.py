#!/opt/python27/bin/python
'''
The Python Standard Library 10.4, p.542 Joinable Queue
http://pguides.net/python-tutorial/python-timeout-a-function/
    kills hung process
The Python Standard Library 2.4.1.4, p.93, sorting on the fly
'''
import multiprocessing
import time
import datetime

import sys
from subprocess import Popen, PIPE

import signal
import bisect
import random

import itertools
import threading

##### Start of Setup #####
## timeout = 12  ## time to kill hung ssh in seconds
timeout = 22  ## time to kill hung ssh in seconds
list_of_servers = []
for n in range(733,751):
        list_of_servers.append('someotherserver%04d' % n)
## list_of_servers.extend(['someotherserver0538','someotherserver0541','someotherserver0544'])
#for n in range(2,700):
#    list_of_servers.append('someotherserver%04d' % n)
#list_of_servers += ['someotherserver', 'someotherserver-hn02']
#list_of_servers = ['someotherserver0539', 'someotherserver0542',]
## list_of_servers += ['someotherserver', 'someotherserver-hn02']
##list_of_servers += ['eradicator0998', 'eradicator0999']
##list_of_servers = ['eradicator0997',]
##print list_of_servers

command_list = [
    '''export http_proxy=http://ip:proxy''',
    '''export https_proxy=https://ip:proxy''',
    '''nohup chef-client > /var/tmp/chef_client_threaded_`date +%Y%m%d_%H%M%S`.log 2>&1 & jobs''',
    ''' tail -1 /var/log/chef/chef-client.log ''',
    ## ''' tail -1 /var/tmp/chef* ''',
    ## ''' ls /var/tmp/chef* ''',
    ]
##### End of Setup #####

command = ';'.join(command_list)
number_of_servers = len(list_of_servers)

class Spinner(threading.Thread):
    def run(self):
        self._exit = False
        self._spinner = itertools.cycle('-\|/')
        while not self._exit:
            #sys.stdout.write(next(self._spinner) + "\b")
            #sys.stdout.flush()
            time.sleep(0.02)

    def stop(self):
        self._exit = True
        self.join()


class TimeoutException(Exception):
    pass

class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue, timeout):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.timeout = timeout

    def run(self):
        def timeout_handler(signum, frame):
            raise TimeoutException()

        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                ## print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            ## print '%s: %s' % (proc_name, next_task)
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
            try:
                answer = next_task()
                self.task_queue.task_done()
                self.result_queue.put(answer)
            except TimeoutException:
                self.task_queue.task_done()
                self.result_queue.put((next_task, ['Failed: %s' % next_task]))
                
        return

class Task(object):
    def __init__(self, server, command):
        self.server = server 
        self.command = command

    def __call__(self):
        cmd = ['/usr/bin/ssh', '-qx',
               '-o  PubkeyAuthentication=yes',
               self.server,
               self.command]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        output = p.communicate()[0]
        if output:
            return (self.server, output.split('\n'))
        else:
            return (self.server, [])

    def __str__(self):
        return '%s' % self.server

if __name__ == '__main__':
    termination_list = []
    socket_total = 0
    cpu_count_total = 0
    ram_total = 0
    server_count = 0
    result_dict = {}

    print '\n%d servers' % number_of_servers
    print 'command: %s' % command
    print 'Querying ... '
    spin = Spinner()
    spin.start()

    try:
        start = time.time()

        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        num_consumers = multiprocessing.cpu_count() * 2
        consumers = [Consumer(tasks, results, timeout)
                     for i in range(num_consumers)]

        for w in consumers:
            w.start()

        for s in list_of_servers:
            tasks.put(Task(s, command))

        for i in range(num_consumers):
            tasks.put(None)

        tasks.join()

        while number_of_servers:
            server, output = results.get()
            server = str(server)
            if output:
                if output[0].startswith('Failed:'):
                    bisect.insort(termination_list, server)
                else:
                    result_dict[server] = output 
            number_of_servers -= 1

    except KeyboardInterrupt:
        print 'Closing ...'
        sys.exit()
    finally:
        spin.stop()

        dict_keys = result_dict.keys()
        dict_keys.sort()

        for ea in dict_keys:
            for l in [x for x in result_dict[ea] if x]:
                print '%s:%s' % (ea, l)

        print
        if termination_list:
            print 'Server connection termininated:', ', '.join(termination_list)
        print 'Elapsed time: %0.4f seconds' %  (time.time() - start)
        print
        sys.stdout.flush()
