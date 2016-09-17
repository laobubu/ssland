#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Utils Module.
#   Just some useful functions
#

import logging

import urllib
def encodeURIComponent(str):
    return urllib.quote(str, safe='~()*!.\'')

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

def html_strip_table(obj):
    '''turn flat dict into a html table
    '''
    from cgi import escape
    return  (
        ['<table class="strip">'] + 
        [('  <tr><th>%s</th><td>%s</td></tr>'%(k, escape(str(v)))) for k,v in obj.iteritems()] + 
        ['</table>']
    )

def random_password(N=16):
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

def ascii_progress_bar(percent, width=20):
    pi = int(percent)
    ps = ''.ljust(int(width * pi / 100), '|').ljust(width, '.')
    return '[%3d%%] %s' % (pi, ps[:width])

def get_prev_uri(request):
    '''used in SSLand web UI'''
    return  request.POST['prev'] if 'prev' in request.POST else                 \
            request.GET['prev']  if 'prev' in request.GET  else                 \
            request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else \
            '/'

import datetime
def smart_datetime(s, last=datetime.datetime.now()):
    '''turn smart date str into datetime instance.

    Formats:
     1. exact datetime, like "May 27 1974" or "2012-12-31 23:59:58"
     2. delta, like "last+1y30d" or "+ 2month,7day"
     3. special point:
       - "next week", "next month", "next day"
    '''
    import calendar
    from dateutil.relativedelta import relativedelta
    import re
    mat = re.search(r'^(?:last)?\s*\+\s*(.+)', s, re.IGNORECASE)
    if mat:
        ret = last
        span_ss = re.findall(r'(\d*\.?\d+)\s*([ymd])', mat.group(1).lower())
        for (amount, unit) in span_ss:
            amount_f = int(amount)
            if unit == 'y':     ret += relativedelta(years=amount_f)
            if unit == 'm':     ret += relativedelta(months=amount_f)
            if unit == 'd':     ret += relativedelta(days=amount_f)
        ret += relativedelta(hour=0, minute=0, second=0, microsecond=0)
        return ret

    mat = re.search(r'next\s+(\w+)', s.lower())
    if mat:
        type = mat.group(1)
        ret = last
        if type == 'week':      ret += relativedelta(days=1, weekday=calendar.firstweekday())
        if type == 'month':     ret += relativedelta(months=1, day=1)
        if type == 'day':       ret += relativedelta(days=1)
        ret += relativedelta(hour=0, minute=0, second=0, microsecond=0)
        return ret
    
    from dateutil.parser import parse as parse_datestr
    return parse_datestr(s)
