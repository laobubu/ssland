from django import forms
from django.core import validators 
from django.utils.encoding import force_text

class VisiblePasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(VisiblePasswordField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MinLengthValidator(4))

    def widget_attrs(self, widget):
        attrs = super(VisiblePasswordField, self).widget_attrs(widget)
        attrs['minlength'] = '4'
        attrs['data-visiblepass'] = 'true'
        return attrs

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
