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

* Python >= 3.6 (developed and tested for Python 3.9 and 3.10)
* XDG library for Python 3 ( https://pypi.org/project/pyxdg/ )
* GTK+ 3.0 libraries for Python 3
* GObject libraries for Python 3 ( https://pypi.org/project/PyGObject/ )
* POlib for Python 3 ( https://pypi.python.org/pypi/polib )

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
