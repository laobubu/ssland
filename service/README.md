A service module must at least have these stuff:

## Basic Control Function

 - `init(config)`
 - `start(accounts)`
 - `stop()`

 content of `config` for initialization function comes from `/config.py` file.
 
 when ssland boots, it will

 1. initialize all services,
 2. fetch all active accounts from the database,
 3. start the services for the active accounts.

 `accounts` is an array of active `account_config` (see below).

 if there is no active account, ssland will provide an empty array.
 however, some proxy servers may fail to start. be careful to handle this.

 when ssland exits, it will
 
 1. stop all services.

## Account Control Function
 
 - `add(account_config)`
 - `remove(account_config)`
 - `update(account_config)`     - update one active account.
 
 the account_config comes from database records.

 while designing a service, do not forget setting up an user-readonly field 
 in the account_config, which is the key to implement the `update` function.

 for example, *port* for Shadowsocks, *username* for L2TP/IPSec

## Web-panel Related

 - `def html(account_config)`           - generate visual information for web browsers. 
 - `class UserForm(django.forms.Form)`  - user configurable params
