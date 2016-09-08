#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Utils Module.
#   Just some useful functions
#

import logging

def get_stdout(*args):
    '''
    Execute an application, returning (stdout, exitcode)

    Example: 
        response, retval = get_stdout(["whoami"])
    '''
    import subprocess
    p = subprocess.Popen(*args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    o = []
    p.stdin.close()
    with p.stdout:
        for line in iter(p.stdout.readline, b''):
            o.append(line)
    p.wait() # wait for the subprocess to exit
    return ''.join(o), p.returncode

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def print_exception(e):
    logging.error(e)
    import traceback
    traceback.print_exc()

def to_bytes(s):
    if bytes != str:
        if type(s) == str:
            return s.encode('utf-8')
    return s


def to_str(s):
    if bytes != str:
        if type(s) == bytes:
            return s.decode('utf-8')
    return s
