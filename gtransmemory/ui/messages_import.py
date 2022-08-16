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

import pathlib

from gi.repository import Gtk

from gtransmemory.gtkbuilder_loader import GtkBuilderLoader
from gtransmemory.functions import get_ui_file, text
import gtransmemory.preferences as preferences
import gtransmemory.settings as settings

SECTION_WINDOW_NAME = 'messages import'


class UIMessagesImport(object):
    def __init__(self, parent, latest_imported_file):
        """Prepare the message dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('messages_import.ui'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_import.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_import, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize labels
        for widget in self.ui.get_objects_by_type(Gtk.Label):
            widget.set_label(text(widget.get_label()))
            widget.set_tooltip_text(widget.get_label().replace('_', ''))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.Button):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        self.filename = ''
        self.source = ''
        if latest_imported_file:
            self.ui.file_chooser_import.set_current_folder(
                str(pathlib.Path(latest_imported_file).parent))
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, title):
        """Show the dialog"""
        self.ui.dialog_import.set_title(title)
        # Show the dialog
        response = self.ui.dialog_import.run()
        self.ui.dialog_import.hide()
        self.filename = self.ui.file_chooser_import.get_filename()
        self.source = self.ui.txt_source.get_text().strip()
        return response

    def destroy(self):
        """Destroy the dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_import, SECTION_WINDOW_NAME)
        self.ui.dialog_import.destroy()
        self.ui.dialog_import = None

    def on_action_confirm_activate(self, action):
        """Check che message configuration before confirm"""
        self.ui.dialog_import.response(Gtk.ResponseType.OK)

    def on_check_for_input_values(self, widget):
        """Check the filename and source arguments"""
        self.ui.action_confirm.set_sensitive(
            bool(self.ui.file_chooser_import.get_filename() and
                 bool(self.ui.txt_source.get_text().strip())))
