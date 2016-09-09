A service module must at least have these stuff:

## Basic Control Function

 - `init(config)`   - the config file comes from `/config.py`
 - `start()`        - start the service, which will be called when ssland boots
 - `stop()`         - stop the service, which will be called when ssland exits 

## Web-panel Related

 - `def html(account_config)`          
   - generate visual information for web browsers. 
   - the account_config comes from database records.
 - `class UserForm(django.forms.Form)` 
   - user configurable params