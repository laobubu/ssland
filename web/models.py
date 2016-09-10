#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as auth_models
from service import getService
import datetime, json
 
class ProxyAccount(models.Model):
    user = models.ForeignKey(auth_models.User)
    service = models.CharField(max_length=130)
    enabled = models.BooleanField(default=False)
    config = models.CharField(max_length=512)
    log = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    expire_when = models.DateTimeField(default=datetime.datetime(1970,1,1), blank=True)

    @property
    def html(self):
        cl = getService(self.service)
        conf = json.loads(self.config)
        return cl.html(conf)
    
    @property
    def form(self):
        cl = getService(self.service)
        return cl.UserForm
