##
#     Project: gTransMemory
# Description: Memory of terms for translators
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2016-2022 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

import os
import os.path
import fnmatch

from gi.repository import Gtk

from gtransmemory.constants import DIR_UI


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


def get_treeview_selected_row(widget):
    """Return the selected row in a GtkTreeView"""
    return widget.get_selection().get_selected()[1]


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return str(DIR_UI / filename)


def process_events():
    """Process every pending GTK+ event"""
    while Gtk.events_pending():
        Gtk.main_iteration()


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


def recursive_glob(starting_path, pattern):
    """Return a list of all the matching files recursively"""
    result = []
    for root, dirnames, filenames in os.walk(starting_path):
        for filename in fnmatch.filter(filenames, pattern):
            result.append(os.path.join(root, filename))
    return result


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
