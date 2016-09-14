from django import forms
from web.models import Quota
from web.forms import SmartDateField

FRIENDLY_NAME = 'Time'

class Form(forms.Form):
    when = SmartDateField(label='Expire on')

def descript(q, is_admin=False):
    '''return user-friendly strings descripting status of one account quota '''
    ret = []
    if is_admin: ret.append(q.param.when)
    ret.append('Expire on %s' % smart_datetime(q.param.when, q.last_trigged).strftime('%Y-%m-%d')) 
    return ret

def is_exceeded(q):  # q: Quota
    from core.util import smart_datetime
    import datetime
    return smart_datetime(q.param.when, q.last_trigged) <= datetime.datetime.now()
