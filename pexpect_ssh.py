'''
Created on Feb 27, 2018

@author: Zhu Tong
'''
import logging
import os
import re
from multiprocessing.dummy import Pool

import pexpect


def get_logger():
    log_pattern = '[%(asctime)s] %(message)s'
    formatter = logging.Formatter(log_pattern)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.propagate = False
    return logger

logger = get_logger()


class SSH(object):
    SSH_STR = 'ssh -o "UserKnownHostsFile /dev/null" -l %s %s'

    def __init__(self, device_info):
        self.device_info = device_info
        self.timeout = device_info.get('timeout',18000)

    def login(self):
        ip = self.device_info['ip']
        username = self.device_info.get('username')
        password = self.device_info.get('password')
        timeout = self.timeout
        prompt = '#'
        try:
            logger.info('ssh %s as %s', ip, username)
            cmd_str = self.SSH_STR % (username, ip)
            child = pexpect.spawn(cmd_str, maxread=8192, searchwindowsize=4096)

            first_pattern = ['.*assword:',
                             '.*(yes/no)',
                             pexpect.TIMEOUT,
                             pexpect.EOF]
            i = child.expect(first_pattern, timeout=timeout)
            if i == 3:
                raise Exception('LoginException.CONNECTION_CLOSED')
            if i == 2:
                raise Exception('LoginException.TIMEOUT')
            if i == 1:
                child.sendline('yes')
                child.expect(['.*assword:'])
            child.sendline(password)

            second_pattern = ['.*%s' % prompt,
                              '.*assword:',
                              pexpect.TIMEOUT,
                              pexpect.EOF]
            i = child.expect(second_pattern, timeout=timeout)
            if i == 1:
                raise Exception('LoginException.LOGIN_FAILED')
            if i == 2:
                raise Exception('LoginException.LOGIN_TIMEOUT')
            if i == 3:
                raise Exception('LoginException.CONNECTION_CLOSED')

            child.sendline('term len 0')
            child.expect(prompt, timeout=timeout)
            last_line = child.before.splitlines()[-1]
            self.hostname = hostname = last_line
            self.prompt = last_line + prompt
            self.child = child
            logger.info('ssh %s success. Got hostname: %s', ip, hostname)
            expect_pattern = [pexpect.TIMEOUT,
                              pexpect.EOF,
                              re.escape(self.prompt),
                              ]
            expect_pattern.append('.*\r\n')
            self.expect_pattern = expect_pattern
            return self.hostname
        except Exception as e:
            logger.error('ssh %s failed: %s', ip, e.message)
            raise

    def execute(self, command):
        ip = self.hostname or self.device_info['ip']
        expect_pattern = self.expect_pattern
        new_line_pattern_id = len(expect_pattern) - 1
        timeout = self.timeout
        child = self.child
        res = []
        logger.info('%s execute: %s', ip, command)
        child.sendline(command)
        while True:
            c = child.expect(expect_pattern, timeout=timeout)
            res.append(child.before)
            res.append(str(child.after))
            if c < new_line_pattern_id:
                break
        if c == 0:
            msg = 'Timeout'
            logger.error('Timeout execute: %s @ %s', command, ip)
            raise Exception(msg)

        return ''.join(res)

    def execute_multi(self, commands):
        outputs = []
        for command in commands:
            output = self.execute(command)
            outputs.append(output)
        return ''.join(outputs)

    def close(self):
        try:
            self.child.close()
            logger.info('Disconnected from %s', self.device_info['ip'])
        except:
            pass


def do_one_device(device_info):
    ssh = SSH(device_info)
    ip = device_info['ip']
    hostname = ssh.login()
    output = ssh.execute_multi(device_info['commands'])
    filename = os.path.join(PATH, '%s_%s.txt' % (hostname, ip))
    logger.info('Save output to file %s', filename)
    with open(filename, 'w') as f:
        f.write(output)


def main(username, password, enable_password, commands, devices):
    params = []
    for ip in DEVICES:
        params.append(dict(ip=ip,
                           username=username,
                           password=password,
                           enable_password=enable_password,
                           commands=commands))

    pool = Pool(10)
    pool.map(do_one_device, params)
    pool.close()
    pool.join()


# ================================================================
PATH = '/Users/AlexFeng/git/MDS_Interface_Counters/interface_transceiver_detail'

USERNAME = 'admin'
PASSWORD = 'cisco!123'
EN_PSWD = '',

COMMANDS = '''
show int trans detail
'''.strip().splitlines()

DEVICES = '''
10.75.60.3
10.75.60.4
'''.strip().splitlines()

main(USERNAME, PASSWORD, EN_PSWD, COMMANDS, DEVICES)
