'''
Default type of Quota. do not modify this.
'''
from django import forms

FRIENDLY_NAME = 'Unconfigured'

class Form(forms.Form):
    pass

def descript(q, is_admin=False):
    return ["Unconfigured quota."]

def is_exceeded(q):
    return False
