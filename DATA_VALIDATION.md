# Data Validation

[![report](https://img.shields.io/badge/report-data%20inconsistencies-orange)](https://mbed-target.s3.eu-west-2.amazonaws.com/validation/index.html)

Mbed has historically had a number of ways to manage target information, which has led to inconsistencies over time
where some sources have been updated while others have not. This repository contains a tool that compares the various
sources of data and generates a report of their consistency. This report is generated on a daily basis and this is
available via the link above.

The following table describes the data sources and usage for Mbed 5.

| Data Source | Definition Location | Used By |
| :---------- | :------------------ | :------ |
| Tools Platform Database | [mbed-os-tools](https://github.com/ARMmbed/mbed-os-tools/blob/master/src/mbed_os_tools/detect/platform_database.py) | `mbed-ls` `mbed detect` |
| `targets.json` | [mbed-os](https://github.com/ARMmbed/mbed-os/blob/master/targets/targets.json) | `mbed compile`, Online Compiler |
| Online Database | OS Site Database (os.mbed.com) | Product Code reservation, Public Websites, Mbed Studio |
 
## Single Source of Truth

The tools for Mbed 6 use a single source of truth for each piece of data, although all data may not come from the same
source. For all common data, the source will be the OS Site Online Database, for example the `Product Code` to 
`Build Target` mapping will be stored in the OS Site Database and all other definitions will be considered irrelevant.
Other information, such as build configuration, will continue to be stored in Mbed OS as it is only relevant to Mbed 
OS. However, it will not be duplicated elsewhere.

There is the potential for confusion during the transition from Mbed 5 to Mbed 6. For example, the `mbed-tools devices` 
command may identify boards differently from the tool `mbed-ls`, which it is replacing. But ensuring there is a single
source of truth will mean that Mbed OS and all tools will be consistent in the future.

# Mbed Targets Offline Database

This package contains an internal database of the relevant information from the OS Site Online Database so that it can
be used in an offline mode. This database is generated as part of CI, which is run on a daily basis and results in a
Pull Request in GitHub if any information needs to be updated. Updates to the database are then released as a new
version of the Python package on PyPI.

The following diagram shows an example usage of this package (`mbed-targets`) by the `mbed-tools devices` command, which
needs to identify the `Build Target` from the `Product Code`. This can be attempted in an offline, online or auto mode,
which uses the internal database first, falling back to accessing the online database if the `Product Code` is unknown.

![Mbed Targets Dataflow](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ARMmbed/mbed-targets/master/diagrams/data_validation/mbed_targets_dataflow.puml)
