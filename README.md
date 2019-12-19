# Mbed Targets

![Package](https://img.shields.io/badge/Package-mbed--targets-lightgrey)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ARMmbed/mbed-targets/blob/master/LICENCE)

[![PyPI](https://img.shields.io/pypi/v/mbed-targets)](https://pypi.org/project/mbed-targets/)
[![PyPI - Status](https://img.shields.io/pypi/status/mbed-targets)](https://pypi.org/project/mbed-targets/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mbed-targets)](https://pypi.org/project/mbed-targets/)
[![Azure DevOps builds](https://img.shields.io/azure-devops/build/mbed-bot/xxxxx/2)](https://dev.azure.com/mbed-bot/mbed-targets/_build?definitionId=2)
[![Codecov](https://img.shields.io/codecov/c/github/ARMmbed/mbed-targets)](https://codecov.io/gh/ARMmbed/mbed-cloud-sdk-python)

## Overview

**This package provides an abstraction layer for boards and platforms supported by Mbed OS.**

It is expected that this package will be used by developers of Mbed OS tooling rather than by users of Mbed OS. For
a command line interface for Mbed OS please see the package [mbed-tools](https://github.com/ARMmbed/mbed-tools).

## Installation

It is recommended that a virtual environment such as [Pipenv](https://github.com/pypa/pipenv/blob/master/README.md) is
used for all installations to avoid Python dependency conflicts.

To install the most recent production quality release use:

```
pip install mbed-targets
```

To install a specific release:

```
pip install mbed-targets==<version>
```

The list of all available versions can be found on the [PyPI Release History](https://pypi.org/project/mbed-targets/#history).

## Guides and Issues

- For release notes and change history, please see the [Changelog](./CHANGELOG.md)
- For guide to developing this package, please see the [Development Guide](./DEVELOPMENT.md)
- For guide to contributing to the project, please see the [Contributions Guidelines](./CONTRIBUTING.md)
- For a list of known issues and possible work arounds, please see [Known Issues](./KNOWNISSUES.md)
- To raise a defect or enhancement please use [GitHub Issues](https://github.com/ARMmbed/mbed-targets/issues)
- To ask a question please use the [Mbed Forum](https://forums.mbed.com/)

## Versioning

The version scheme used follows [PEP440](https://www.python.org/dev/peps/pep-0440/) and 
[Semantic Versioning](https://semver.org/). 

For production quality releases the version will look as follows:

- `<major>.<minor>.<patch>`

For beta releases the version will look as follows:

- `<major>.<minor>.<patch>b<build_number>`

Please note that beta releases may not be stable and should not be used for production. Additionally any interfaces
introduced in beta releases may be removed or changed without notice.