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

import logging

from gi.repository import Gtk

from gtransmemory.ui.base import UIBase

SECTION_WINDOW_NAME = 'messages import'


class UIMessagesImport(UIBase):
    def __init__(self, parent, settings, options, initial_dir):
        """Prepare the dialog"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='messages_import.ui')
        # Initialize members
        self.parent = parent
        self.settings = settings
        self.options = options
        self.initial_dir = str(initial_dir)
        self.filename = ''
        self.source = ''
        # Load UI
        self.load_ui()
        # Complete initialization
        self.startup()

    def load_ui(self):
        """Load the interface UI"""
        logging.debug(f'{self.__class__.__name__} load UI')
        # Initialize titles and tooltips
        self.set_titles()
        # Set various properties
        self.ui.dialog.set_transient_for(self.parent)
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def startup(self):
        """Complete initialization"""
        logging.debug(f'{self.__class__.__name__} startup')
        # Set the initial directory
        if self.initial_dir:
            self.ui.file_chooser_import.set_current_folder(self.initial_dir)
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.dialog,
                                              section=SECTION_WINDOW_NAME)

    def show(self, title):
        """Show the dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.dialog.set_title(title)
        # Show the dialog
        response = self.ui.dialog.run()
        self.ui.dialog.hide()
        self.filename = self.ui.file_chooser_import.get_filename()
        self.source = self.ui.entry_source.get_text().strip()
        return response

    def destroy(self):
        """Destroy the dialog"""
        logging.debug(f'{self.__class__.__name__} destroy')
        self.settings.save_window_position(window=self.ui.dialog,
                                           section=SECTION_WINDOW_NAME)
        self.ui.dialog.destroy()
        self.ui.dialog = None

    def do_check_file_source(self):
        """Check the filename and source arguments"""
        self.ui.action_confirm.set_sensitive(
            bool(self.ui.file_chooser_import.get_filename() and
                 bool(self.ui.entry_source.get_text().strip())))

    def on_action_confirm_activate(self, widget):
        """Check che message configuration before confirm"""
        self.ui.dialog.response(Gtk.ResponseType.OK)

    def on_entry_source_changed(self, widget):
        """Check the filename and source arguments"""
        self.do_check_file_source()

    def on_file_chooser_import_file_set(self, widget):
        """Check the filename and source arguments"""
        self.do_check_file_source()
