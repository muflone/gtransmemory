# gTransMemory

[![Travis CI Build Status](https://img.shields.io/travis/com/muflone/gtransmemory/master.svg)](https://www.travis-ci.com/github/muflone/gtransmemory)
[![CircleCI Build Status](https://img.shields.io/circleci/project/github/muflone/gtransmemory/master.svg)](https://circleci.com/gh/muflone/gtransmemory)

**Description:** Memory of terms for translators

**Copyright:** 2016-2022 Fabio Castelli (Muflone) <muflone(at)muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/gtransmemory

**Documentation:** http://www.muflone.com/gtransmemory/

System Requirements
-------------------

* Python 2.x (developed and tested for Python 2.7.5)
* GTK+ 3.0 libraries for Python 2.x
* GObject libraries for Python 2.x
* XDG library for Python 2.x (https://pypi.python.org/pypi/pyxdg/)
* Distutils library for Python 2.x (usually shipped with Python distribution)
* POlib for Python 2.x (https://pypi.python.org/pypi/polib)

Installation
------------

A distutils installation script is available to install from the sources.

To install in your system please use:

    cd /path/to/folder
    python2 setup.py install

To install the files in another path instead of the standard /usr prefix use:

    cd /path/to/folder
    python2 setup.py install --root NEW_PATH

Usage
-----

If the application is not installed please use:

    cd /path/to/folder
    python2 gtransmemory.py

If the application was installed simply use the gtransmemory command.
