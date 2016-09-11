#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from web.models import ProxyAccount

from web.views import FlickBackResponse
from core.util import random_password
import json

@permission_required('auth.add_user')
def user_list(request):
    from django.contrib.auth.models import User
    return render(request, 'admin/users.html', {
        'title': 'Users', 
        'users': User.objects.all(),
    })

class UserAddForm(auth_forms.UserCreationForm):
    pass

@permission_required('auth.add_user')
def user_add(request):
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            u = form.save()
            import config as ssland_config
            from service import getService
            for service_name in ssland_config.MODULES:
                s = getService(service_name)
                conf = s.skeleton()
                a = ProxyAccount(user=u, service=service_name, enabled=False, config=conf)
                a.save()
            return redirect('..')
    else:
        form = UserAddForm()
    return render(request, 'admin/user.add.html', {
        'title': 'Add User',
        'form': form,
    })

@permission_required('auth.add_user')
def user_toggle(request, uid):
    if str(uid) == str(request.user.pk):
        return FlickBackResponse(request)

    u = User.objects.get(pk=uid)
    u.is_active = not u.is_active
    u.save()

    for pa in ProxyAccount.objects.filter(user=u, enabled=True):
        try:
            if u.is_active: pa.start_service()
            else: pa.stop_service()
        except:
            pass
        
    return FlickBackResponse(request)

@permission_required('web.change_proxyaccount')
def account_toggle(request, account_id):
    account = ProxyAccount.objects.get(pk=account_id)
    account.enabled = not account.enabled
    account.save()
    return FlickBackResponse(request)

@permission_required('web.change_proxyaccount')
def account_edit(request, account_id):
    account = ProxyAccount.objects.get(pk=account_id)
    UserForm = account.adminForm
    prevURL =   request.POST['prev'] if 'prev' in request.POST else                 \
                request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else \
                '/'

    if request.method == "POST":
        form = UserForm(request.POST)
        bypass_twostep_validate = not getattr(form, 'is_valid_for_account', None)
        if form.is_valid() and (bypass_twostep_validate or form.is_valid_for_account(account)):
            account.config.update(form.cleaned_data)
            account.save()
            return redirect(prevURL)
    else:
        form = UserForm(initial=account.config)
            
    return render(request, 'account.edit.html', {
        'title': 'Edit Account', 
        'account': account,
        'prev': prevURL,
        'form': form
    })

@login_required
def ttt_test(request):
    pa = ProxyAccount(user=request.user, service='Shadowsocks', config='{"port":1234}')
    pa.save()
    return redirect('/account/')

