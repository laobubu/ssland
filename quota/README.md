Quota modules are designed to restrict accounts. 
Most Quota modules are Service-independent, eg. `TimeQuota` cuts off accounts if time exceed.

Before implementing a new type of Quota, read and learn the `Quota` model.

# Quota Model

See `web/models.py`

# Quota Module

A module provides necessary methods and information. When SSLand check one account's usage, it will

1. Get the Quota instance `q` from database, getting its params, last trigged time, etc.
2. Load corresponding quota module.
3. Call `is_exceeded(q)` of the module. If get `True`, the account will be suspended.

Here is what a module shall have:

## Misc

 - `FRIENDLY_NAME`      - constant string, name of this Quota type.
 - `class Form`

   For admins, designed to configure the params.

## Methods 
 
 - `def descript(q, is_admin=False)`

   **Returns** array of string that descripts `q`, a Quota instance.

 - `def is_exceeded(q)` 
 
   **Returns** bool, telling if `q.account` exceed this Quota. 
