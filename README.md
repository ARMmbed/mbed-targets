# mbed-targets
Python package that informs the mbed build system about targets and their configuration.

## Development and Testing

For development and testing purposes it is essential to use a virtual environment, it is recommended that `pipenv` is used.

### Setup Pipenv

To start developing install pip and pipenv on your system. Note the latter is done a user level to keep the system installation of python clean which is important on a Mac (at least):

```bash
sudo easy_install pip
```

Install pipenv (the --user is important, do not use `sudo`)

```bash
pip install --user pipenv
```

Check pipenv is in the binary path

```bash
pipenv --version
```

If not find the user base binary directory

```bash
python -m site --user-base
#~ /Users/<username>/Library/Python/2.7
```

Append `bin` to the directory returned and add this to your path by updating `~/.profile`. For example you might add the following:

```bash
export PATH=~/Library/Python/3.7/bin/:$PATH
```

### Setup Development Environment

Clone GitHub repository

```bash
git clone git@github.com:ARMmbed/mbed-targets.git
```

Setup Pipenv to use Python 3 (Python 2 is not supported) and install package development dependencies:

```bash
cd mbed-targets/
pipenv --three
pipenv install "-e ." --dev
```

Shell into virtual environment and run unit tests:

```bash
pipenv shell
python -m unittest
```
