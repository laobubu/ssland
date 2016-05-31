#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Utils Module.
#   Just some useful functions
#

def get_stdout(*args):
    import subprocess
    p = subprocess.Popen(*args, stdout=subprocess.PIPE, bufsize=1)
    o = []
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
