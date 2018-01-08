from django import forms
from django.db.models import Sum
from web.models import Quota, TrafficStat

FRIENDLY_NAME = 'Traffic'


class Form(forms.Form):
    traffic = forms.NumberInput(label='Traffic (MB)', attrs={'step': '0.01'})


def descript(q, is_admin=False):
    '''return user-friendly strings descripting status of one account quota '''
    par_traffic = float(q.param.get('traffic', '1024768'))
    current_used = TrafficStat.objects                          \
        .filter(account=q.account, time__gte=q.last_trigged)    \
        .aggregate(Sum('amount')) / 1e6

    return [
        "Used: %.2f / %.2f (MB)   (%.1f %%)" % (current_used, par_traffic,
                                                (current_used / par_traffic * 100))
    ]


def is_exceeded(q):  # q: Quota
    par_traffic = float(q.param.get('traffic', '1024768'))
    current_used = TrafficStat.objects                          \
        .filter(account=q.account, time__gte=q.last_trigged)    \
        .aggregate(Sum('amount')) / 1e6
    return current_used >= par_traffic
