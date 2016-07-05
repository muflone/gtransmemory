##
#     Project: gTransMemory
# Description: Learn memory for translators
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#   Copyright: 2016 Fabio Castelli
#     License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

import os
import os.path
import fnmatch
import json
import string
from gettext import gettext, dgettext

from gi.repository import Gtk
from gi.repository import Gdk

from gtransmemory.constants import DIR_UI

localized_messages = {}


def readlines(filename, empty_lines=False):
    """Read all the lines of a filename, optionally skipping empty lines"""
    result = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if line or empty_lines:
                result.append(line)
        f.close()
    return result


def process_events():
    """Process every pending GTK+ event"""
    while Gtk.events_pending():
        Gtk.main_iteration()


def text(message, gtk30=False, context=None):
    """Return a translated message and cache it for reuse"""
    if message not in localized_messages:
        if gtk30:
            # Get a message translated from GTK+ 3 domain
            full_message = message if not context else '%s\04%s' % (
                context, message)
            localized_messages[message] = dgettext('gtk30', full_message)
            # Fix for untranslated messages with context
            if context and localized_messages[message] == full_message:
                localized_messages[message] = dgettext('gtk30', message)
        else:
            localized_messages[message] = gettext(message)
    return localized_messages[message]


def store_message(message, translated):
    """Store a translated message in the localized_messages list"""
    localized_messages[message] = translated


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return os.path.join(DIR_UI, filename)


def check_invalid_input(widget, empty, separators, invalid_chars):
    """Check the input for empty value or invalid characters"""
    text = widget.get_text().strip()
    if (not empty and len(text) == 0) or \
            (not separators and ('/' in text or ',' in text)) or \
            (not invalid_chars and ('\'' in text or '\\' in text)):
        icon_name = 'dialog-error'
    else:
        icon_name = None
    widget.set_icon_from_icon_name(
        Gtk.EntryIconPosition.SECONDARY, icon_name)
    return bool(icon_name)


def set_error_message_on_infobar(widget, widgets, label, infobar, error_msg):
    """Show an error message for a widget"""
    if error_msg:
        label.set_text(error_msg)
        infobar.set_visible(True)
        if widget in widgets:
            widget.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, 'dialog-error')
            widget.grab_focus()
    else:
        infobar.set_visible(False)
        for w in widgets:
            w.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)


def recursive_glob(starting_path, pattern):
    """Return a list of all the matching files recursively"""
    result = []
    for root, dirnames, filenames in os.walk(starting_path):
        for filename in fnmatch.filter(filenames, pattern):
            result.append(os.path.join(root, filename))
    return result


def get_treeview_selected_row(widget):
    """Return the selected row in a GtkTreeView"""
    return widget.get_selection().get_selected()[1]


def show_popup_menu(menu, button=Gdk.BUTTON_SECONDARY):
    """Show a GtkMenu popup"""
    return menu.popup(parent_menu_shell=None,
                      parent_menu_item=None,
                      func=None,
                      data=None,
                      button=button,
                      activate_time=Gtk.get_current_event_time())


def create_filefilter(title, mime_types=None, file_patterns=None):
    """Add a new filter to the dialog"""
    new_filter = Gtk.FileFilter()
    new_filter.set_name(title)
    if mime_types:
        for mime_type in mime_types:
            new_filter.add_mime_type(mime_type)
    if file_patterns:
        for file_pattern in file_patterns:
            new_filter.add_pattern(file_pattern)
    return new_filter


# This special alias is used to track localization requests to catch
# by xgettext. The text() calls aren't tracked by xgettext
_ = text

__all__ = [
    'readlines',
    'process_events',
    'text',
    '_',
    'localized_messages',
    'get_ui_file',
    'check_invalid_input',
    'set_error_message_on_infobar',
    'recursive_glob',
    'get_treeview_selected_row',
    'show_popup_menu',
    'create_filefilter'
]
