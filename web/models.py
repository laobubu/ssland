#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as auth_models
from jsonfield import JSONField
from service import getService
from quota import getQuotaModule
 
class ProxyAccount(models.Model):
    user = models.ForeignKey(auth_models.User)
    service = models.CharField(max_length=130)
    enabled = models.BooleanField(default=False)
    config = JSONField(default={})
    log = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    expire_when = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def is_active(self):
        return self.enabled and self.user.is_active

    def stop_service(self):
        '''DANGEROUS: unconditionally stop service for this account'''
        getService(self.service).remove(self.config)

    def start_service(self):
        '''DANGEROUS: unconditionally start service for this account'''
        getService(self.service).add(self.config)

    def save(self, *args, **kw):
        try:
            orig = ProxyAccount.objects.get(pk=self.pk)
            serv = getService(self.service)
            
            a_orig = orig.is_active
            a_curr = self.is_active

            if not a_orig and a_curr:   serv.add(self.config)       # add
            if a_orig and not a_curr:   serv.remove(self.config)    # remove
            if a_orig and a_curr:       serv.update(self.config)    # update
                
        except ProxyAccount.DoesNotExist as e:
            pass
        except Exception as e2:
            from core.util import print_exception
            import logging
            print_exception(e2)
            logging.error("Failed to update service for ProxyAccount %d", self.pk)
        self.config['id'] = self.pk
        super(ProxyAccount, self).save(*args, **kw)

    @property
    def html(self):
        cl = getService(self.service)
        return cl.html(self.config)

    @property
    def form(self):
        cl = getService(self.service)
        return cl.UserForm

    @property
    def adminForm(self):
        cl = getService(self.service)
        return cl.AdminForm

class TrafficStat(models.Model):
    account = models.ForeignKey(ProxyAccount, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    amount = models.IntegerField()

class Quota(models.Model):
    account = models.ForeignKey(ProxyAccount, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    last_trigged = models.DateTimeField(auto_now_add=True, blank=True)
    comment = models.CharField(max_length=140, default='')
    
    is_alias_of = models.ForeignKey('self', on_delete=models.CASCADE, default=-1)       # clone type and param from this one
    type = models.CharField(default='Unconfigured', max_length=20)
    param = JSONField(default={})

    synced = False
    alias_target_enabled = True

    def update_from_alias(self, forced=False):
        '''Copy type and param from the alias target, if is_alias_of is set.
        
        Call this function before reading type or param.
        '''
        if not forced and self.synced: 
            return
        self.synced = True
        if self.is_alias_of_id != -1 :
            a = self.is_alias_of
            self.type = a.type
            self.param = a.param
            self.alias_target_enabled = a.enabled
    
    @property
    def is_really_enabled(self):
        self.update_from_alias()
        return self.alias_target_enabled and self.enabled and self.account.enabled

    @property
    def module(self):
        self.update_from_alias()
        return getQuotaModule(self.type)
    
    @property
    def name(self):
        return self.module.FRIENDLY_NAME
    
    def descript(self, is_admin=False):
        return self.module.descript(self, is_admin)

    def trig(self):
        self.account.enabled = False
        self.account.save()
        self.reset()

    def reset(self):
        from django.utils import timezone
        self.last_trigged = timezone.now()
        self.save()

    def is_exceeded(self):
        return self.module.is_exceeded(self)
