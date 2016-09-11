#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from web.models import ProxyAccount

from core.util import encodeURIComponent
import pyqrcode, io

def FlickBackResponse(request):
    prevURL = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else '/'
    return redirect(prevURL)

def qr_view(request):
    qr = pyqrcode.create(request.GET['data'])
    out = io.BytesIO()
    qr.svg(out, scale=5)
    return HttpResponse(
        out.getvalue(),
        content_type = 'image/svg+xml'
    )

def login_view(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
    except:
        return render(request, 'login.html', {
            'title': 'Login',
            'nexturi': request.GET['next'] if ('next' in request.GET) else '/',
        })
    if user is not None:
        login(request, user)
        return redirect(request.POST['next'])
    else:
        return render(request, 'login.html', {
            'title': 'Login', 
            'nexturi': request.POST['next'],
            'username': username, 
        })

def logout_view(request):
    logout(request)
    return redirect('/')

def index_view(request):
    return render(request, 'index.html')

@login_required
def account_view(request):
    user = request.user
    accounts = ProxyAccount.objects.filter(user = user)
    return render(request, 'account.html', {'title': 'Accounts', 'accounts': accounts})

@login_required
def account_edit_view(request, service):
    user = request.user
    account = ProxyAccount.objects.filter(user=user,service=service) [0]
    UserForm = account.form

    if request.method == "POST":
        form = UserForm(request.POST)
        bypass_twostep_validate = not (getattr(form, 'is_valid_for_account', None) and True)
        if form.is_valid() and (bypass_twostep_validate or form.is_valid_for_account(account)):
            account.config.update(form.cleaned_data)
            account.save()
            return redirect('/account/#' + encodeURIComponent(service))
    else:
        form = UserForm(initial=account.config)
            
    return render(request, 'account.edit.html', {
        'title': 'Edit Account', 
        'account': account,
        'prev': '/account/#' + encodeURIComponent(service),
        'form': form
    })

from web import views_admin
