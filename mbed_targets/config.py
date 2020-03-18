"""Configuration options for `mbed-targets`.

All the configuration options can be set either via environment variables or using a `.env` file
containing the variable definitions as follows:

```
VARIABLE=value
```

Environment variables take precendence, meaning the values set in the file will be overriden
by any values previously set in your environment.

.. WARNING::
   Do not upload `.env` files containing private tokens to version control! If you use this package
   as a dependency of your project, please ensure to include the `.env` in your `.gitignore`.
"""
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

MBED_API_AUTH_TOKEN = os.getenv("MBED_API_AUTH_TOKEN")
"""Mbed Targets uses the online mbed target database at os.mbed.com as its data source.
A snapshot of the target database is shipped with the package, for faster lookup of known
targets. Only public targets are stored in the database snapshot. If you are fetching data
for a private target, mbed-targets will need to contact the online database.

To fetch data about private targets from the online database, the user must have an account
on os.mbed.com and be member of a vendor team that has permissions to see the private board.
An authentication token for the team member must be provided in an environment variable named
`MBED_API_AUTH_TOKEN`.
"""

MBED_DATABASE_MODE = os.getenv("MBED_DATABASE_MODE", "AUTO")
"""Mbed Targets supports an online and offline mode, which instructs targets where to look up the target database.

The target lookup can be from either the online or offline database, depending
on the value of an environment variable called `MBED_DATABASE_MODE`.

The mode can be set to one of the following:

- `AUTO`: the offline database is searched first, if the target isn't found the online database is searched.
- `ONLINE`: the online database is always used.
- `OFFLINE`: the offline database is always used.

If `MBED_DATABASE_MODE` is not set, it defaults to `AUTO`.
"""
