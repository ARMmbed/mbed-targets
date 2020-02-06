"""mbed-targets provides an abstraction layer for boards and platforms supported by Mbed OS.

This package is intended for use by developers using Mbed OS.

To fetch data about private targets, the user must have an account on os.mbed.com and be
member of a vendor team that has permissions to see the private board. An authentication
token for the team member must be provided in an environment variable named
`MBED_API_AUTH_TOKEN`. The package also accepts a `.env` file containing the environment
variable definition as follows:

```
MBED_API_AUTH_TOKEN=token
```

Where `token` is the authentication token.

The `.env` file takes precendence, so the token set in the file will be the one that is
used if you also set the environment variable in your shell session.

The code searches for the `.env` file by guessing where to start, using `__file__` or
the current working directory, then walks up the directory tree, stopping at the first
`.env` found.

Do not upload `.env` files containing private tokens to GitHub! If you use this package
as a dependency of your project, please ensure to include the `.env` in your `.gitignore`.

"""
from mbed_targets._version import __version__
from mbed_targets.mbed_targets import MbedTargets, MbedTarget
