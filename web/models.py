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

    def save(self, *args, **kw):
        orig = ProxyAccount.objects.get(pk=self.pk)
        serv = getService(self.service)
        if not orig.enabled and self.enabled: # add
            serv.add(self.config)
        if orig.enabled and not self.enabled: # remove
            serv.remove(self.config)
        if orig.enabled and self.enabled: # update
            serv.update(self.config)
        super(ProxyAccount, self).save(*args, **kw)

    @property
    def html(self):
        cl = getService(self.service)
        return cl.html(self.config)

    @property
    def form(self):
        cl = getService(self.service)
        return cl.UserForm
