A service module provides proxy service. 

It must implement these stuff...

## Basic Control Function

 - `init(config)`
 - `start(accounts, event_loop)`
 - `stop()`

 content of `config` for initialization function comes from `/config.py` file.
 
 when ssland boots, it will

 1. initialize all services,
 2. fetch all active accounts from the database,
 3. start the services for the active accounts.

 when ssland exits, it will
 
 1. stop all services.

### Details on `start` function

 `accounts` is an array of active `account_config` (see below).

 if there is no active account, ssland will provide an empty array.
 however, some proxy servers may fail to start. be careful to handle this.
 
 `event_loop` is the SSLand main event loop, an instance of [shadowsocks eventloop].

 you can ignore this param, or use it to do statistics and periodic tasks.
 for example, Shadowsocks may report the traffic statistics per 10 seconds.

 [shadowsocks eventloop]: https://github.com/shadowsocks/shadowsocks/blob/master/shadowsocks/eventloop.py

## Account Control Function
 
 - `add(account_config)`
 - `remove(account_config)`
 - `update(account_config)`     - update one active account.

 - `skeleton()` - return an account_config for a new account. 
 
### account_config

 `account_config` is a dict object, stroaged in the database.
 you may structure it as you like, except these reserved fields:

 - `id` - the primary key of this account.

## Web-panel Related

 - `def html(account_config)`           - generate visual information for web browsers. 
 - `class UserForm(django.forms.Form)`  - user configurable params
 - `class AdminForm(django.forms.Form)` - admin params, including user params
 
 Optionally, 
  you may implement `is_valid_for_account(self, account)` for UserForm and AdminForm, 
  where `account` is an instance of `web.models.ProxyAccount`.
 This function will be called after Django `is_valid()` validating. 
 You may use `cleaned_data` to do further validation.
