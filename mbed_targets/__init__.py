"""mbed-targets provides an abstraction layer for boards and platforms supported by Mbed OS.

This package is intended for use by developers using Mbed OS.

Configuration
=============

Configuring mbed-targets
------------------------

All the configuration options can be set either via environment variables or using a `.env` file
containing the variable definitions as follows:
```
VARIABLE=value
```

The `.env` file takes precendence, meaning the values set in the file will override any
values previously set in your environment.

.. WARNING::
   Do not upload `.env` files containing private tokens to version control! If you use this package
   as a dependency of your project, please ensure to include the `.env` in your `.gitignore`.

MBED_DATABASE_MODE
------------------

Mbed Targets supports an online and offline mode, which instructs targets where to look up the target database.

The target lookup can be from either the online or offline database, depending
on the value of an environment variable called `MBED_DATABASE_MODE`.

The mode can be set to one of the following:

- `AUTO`: the offline database is searched first, if the target isn't found the online database is searched.
- `ONLINE`: the online database is always used.
- `OFFLINE`: the offline database is always used.

If `MBED_DATABASE_MODE` is not set, it defaults to `AUTO`.


MBED_API_AUTH_TOKEN
-------------------

Mbed Targets uses the online mbed target database at os.mbed.com as its data source.
A snapshot of the target database is shipped with the package, for faster lookup of known
targets. Only public targets are stored in the database snapshot. If you are fetching data
for a private target, mbed-targets will need to contact the online database.

To fetch data about private targets from the online database, the user must have an account
on os.mbed.com and be member of a vendor team that has permissions to see the private board.
An authentication token for the team member must be provided in an environment variable named
`MBED_API_AUTH_TOKEN`.

"""
from mbed_targets._version import __version__
from mbed_targets.mbed_targets import (
    get_target_by_product_code,
    get_target_by_online_id,
    MbedTarget,
)
from mbed_targets import exceptions
