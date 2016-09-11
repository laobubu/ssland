#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as auth_models
from jsonfield import JSONField
from service import getService
import datetime, json
 
class ProxyAccount(models.Model):
    user = models.ForeignKey(auth_models.User)
    service = models.CharField(max_length=130)
    enabled = models.BooleanField(default=False)
    config = JSONField()
    log = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    expire_when = models.DateTimeField(default=datetime.datetime(2000,1,1), blank=True)

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
    account = models.ForeignKey(ProxyAccount)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    amount = models.IntegerField()

class UsageQuota(models.Model):
    class Meta:
        abstract = True
