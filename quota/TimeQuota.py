from django import forms
from web.models import Quota
from web.forms import SmartDateField

FRIENDLY_NAME = 'Time'

class Form(forms.Form):
    when = SmartDateField(label='Expire on')

def descript(q, is_admin=False):
    '''return user-friendly strings descripting status of one account quota '''
    from core.util import smart_datetime
    ret = []
    par_when = q.param.get('when', '2038-1-1')
    calcdate = smart_datetime(
        par_when, 
        q.last_trigged
    )
    ret.append('Expire on %s' % calcdate.strftime('%Y-%m-%d %H:%M')) 
    if is_admin: ret.append('Param: %s'%par_when)
    return ret

def is_exceeded(q):  # q: Quota
    from core.util import smart_datetime
    from django.utils import timezone
    calcdate = smart_datetime(
        q.param.get('when', '2038-1-1'), 
        q.last_trigged
    )
    try:
        return calcdate <= timezone.now()
    except:
        return timezone.make_aware(calcdate, timezone.get_default_timezone()) <= timezone.now()
