from django import forms
from django.core import validators 
from django.utils.encoding import force_text

class SmartDateField(forms.Field):
    def __init__(self, *args, **kwargs):
        super(SmartDateField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = force_text(value)
        return value

    def widget_attrs(self, widget):
        attrs = super(SmartDateField, self).widget_attrs(widget)
        attrs['data-smartdate'] = 'true'
        return attrs
