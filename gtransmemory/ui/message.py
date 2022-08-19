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

from gtransmemory.functions import (check_invalid_input,
                                    set_error_message_on_infobar)
from gtransmemory.localize import _
from gtransmemory.ui.base import UIBase

SECTION_WINDOW_NAME = 'message'


class UIMessage(UIBase):
    def __init__(self, parent, settings, options, messages):
        """Prepare the dialog"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='message.ui')
        # Initialize members
        self.parent = parent
        self.settings = settings
        self.options = options
        self.messages = messages
        self.selected_iter = None
        self.message = None
        self.translation = None
        self.source = None
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
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.dialog,
                                              section=SECTION_WINDOW_NAME)

    def show(self, default_message, default_translation, default_source,
             title, treeiter):
        """Show the dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.entry_message.set_text(default_message)
        self.ui.entry_translation.set_text(default_translation)
        self.ui.entry_source.set_text(default_source)
        self.ui.entry_message.grab_focus()
        self.ui.dialog.set_title(title)
        self.selected_iter = treeiter
        # Show the dialog
        response = self.ui.dialog.run()
        self.ui.dialog.hide()
        self.message = self.ui.entry_message.get_text().strip()
        self.translation = self.ui.entry_translation.get_text().strip()
        self.source = self.ui.entry_source.get_text().strip()
        return response

    def destroy(self):
        """Destroy the dialog"""
        logging.debug(f'{self.__class__.__name__} destroy')
        self.settings.save_window_position(window=self.ui.dialog,
                                           section=SECTION_WINDOW_NAME)
        self.ui.dialog.destroy()
        self.ui.dialog = None

    def do_show_error_message_on_infobar(self, widget, error_msg):
        """Show the error message on the GtkInfoBar"""
        set_error_message_on_infobar(
            widget=widget,
            widgets=(self.ui.entry_message, self.ui.entry_translation),
            label=self.ui.label_error_message,
            infobar=self.ui.infobar_error_message,
            error_msg=error_msg)

    def on_action_confirm_activate(self, widget):
        """Check che message configuration before confirm"""
        message = self.ui.entry_message.get_text().strip()
        if len(message) == 0:
            # Show error for missing message
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_message,
                error_msg=_('The message is missing'))
        elif self.messages.get_iter(message) not in (None, self.selected_iter):
            # Show error for existing message
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_message,
                error_msg=_('The specified message already exists'))
        else:
            self.ui.dialog.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_entry_message_changed(self, widget):
        """Check the message field"""
        check_invalid_input(widget, False, True, True)
