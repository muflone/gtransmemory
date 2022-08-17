# gTransMemory

[![Travis CI Build Status](https://img.shields.io/travis/com/muflone/gtransmemory/master.svg)](https://www.travis-ci.com/github/muflone/gtransmemory)
[![CircleCI Build Status](https://img.shields.io/circleci/project/github/muflone/gtransmemory/master.svg)](https://circleci.com/gh/muflone/gtransmemory)

**Description:** Memory of terms for translators

**Copyright:** 2016-2022 Fabio Castelli (Muflone) <muflone(at)muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/gtransmemory

**Documentation:** https://www.muflone.com/gtransmemory/

**Translations:** https://explore.transifex.com/muflone/gtransmemory/

# Description

With *gTransMemory* you can create one or multiple memories of terms for
translators in order to save your translation terms and use them to translate
other projects

![Main window](https://www.muflone.com/resources/gtransmemory/archive/latest/english/main.png)

For each language or memory you can have as many terms you need and have the
same terms also for different sources. For example a different source may be
another application.

This way you can always know how a particular text was translated in a project
or in another.

![Detail](https://www.muflone.com/resources/gtransmemory/archive/latest/english/detail.png)

You can create all the memories you need and you can change from a memory with
a simple click.

![Memories](https://www.muflone.com/resources/gtransmemory/archive/latest/english/memories.png)

# System Requirements

* Python >= 3.6 (developed and tested for Python 3.9 and 3.10)
* XDG library for Python 3 ( https://pypi.org/project/pyxdg/ )
* GTK+ 3.0 libraries for Python 3
* GObject libraries for Python 3 ( https://pypi.org/project/PyGObject/ )
* POlib for Python 3 ( https://pypi.python.org/pypi/polib )

# Installation

A distutils installation script is available to install from the sources.

To install in your system please use:

    cd /path/to/folder
    python3 setup.py install

To install the files in another path instead of the standard /usr prefix use:

    cd /path/to/folder
    python3 setup.py install --root NEW_PATH

# Usage

If the application is not installed please use:

    cd /path/to/folder
    python3 gtransmemory.py

If the application was installed simply use the gtransmemory command.
