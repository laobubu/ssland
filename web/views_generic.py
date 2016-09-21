from __future__ import absolute_import

from django.shortcuts import render
from django.contrib.auth.models import User
from web.models import ProxyAccount, Quota, TrafficStat

def generate_traffic_view(request, stats_objects, title, padding=0.05):
    '''Generate web page to view traffic info
    '''
    
    from django.utils import timezone
    from django.utils.dateparse import parse_date

    stats = stats_objects.order_by('time')

    try:
        qto = parse_date(request.GET['to'])
        stats = stats.filter(time__lt = qto + timezone.timedelta(days=1, hours=2))
    except:
        qto = timezone.now()
    
    try:
        qfrom = parse_date(request.GET['from'])
        stats = stats.filter(time__gt = qfrom - timezone.timedelta(hours=2))
    except:
        qfrom = qto - timezone.timedelta(days=7, hours=2)

    if not stats:
        return render(request, 'traffic.html', {
            'title': title, 
            'stats': [], 
            'sum': 0,
            'grids' : [],
            'padding': padding*100,
            'qfrom': qfrom,
            'qto': qto,
        })

    tfrom = stats.first().time
    tto = stats.last().time
    tlength = (tto - tfrom).total_seconds()
    if tlength < 1: tlength = 1
    get_percent = lambda time: (1-padding) * 100 * (time - tfrom).total_seconds() / tlength

    stats2 = []
    _sum = 0
    for s in stats:
        _sum += s.amount
        stats2.append({
            "x_percent": get_percent(s.time),
            "time": s.time,
            "amount": s.amount,
            "sum": _sum,
        })
    
    for s in stats2:
        s['y_percent_rev'] = (1-padding) * (100 - 100 * s['sum'] / _sum)

    grids = []
    _gtime = timezone.datetime(tfrom.year, tfrom.month, tfrom.day, tzinfo=timezone.get_current_timezone())
    while True:
        _percent = get_percent(_gtime)
        _gtime += timezone.timedelta(days=1) # FIXME: shall not be here? but it works!
        if _percent > 100: break
        if _percent > 0:
            grids.append({
                'x_percent': _percent,
                'time': _gtime
            })

    return render(request, 'traffic.html', {
        'title': title, 
        'stats': stats2, 
        'sum': _sum,
        'grids' : grids,
        'padding': padding*100,
        'qfrom': qfrom,
        'qto': qto,
    })
