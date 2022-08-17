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

SECTION_WINDOW_NAME = 'detail'


class UIMemoryDetail(UIBase):
    def __init__(self, parent, settings, options, model):
        """Prepare the dialog"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='memory_detail.ui')
        # Initialize members
        self.parent = parent
        self.settings = settings
        self.options = options
        self.model = model
        self.name = ''
        self.description = ''
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

    def show(self, default_name, default_description, title):
        """Show the dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.entry_name.set_text(default_name)
        self.ui.entry_name.grab_focus()
        self.ui.entry_description.set_text(default_description)
        self.ui.dialog.set_title(title)
        response = self.ui.dialog.run()
        self.ui.dialog.hide()
        self.name = self.ui.entry_name.get_text().strip()
        self.description = self.ui.entry_description.get_text().strip()
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
            widgets=(self.ui.entry_name, self.ui.entry_description),
            label=self.ui.label_error_message,
            infobar=self.ui.infobar_error_message,
            error_msg=error_msg)

    def on_action_confirm_activate(self, widget):
        """Check che group configuration before confirm"""
        name = self.ui.entry_name.get_text().strip()
        description = self.ui.entry_description.get_text().strip()
        if len(name) == 0:
            # Show error for missing memory name
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_name,
                error_msg=_('The memory name is missing'))
        elif '\'' in name or '\\' in name or '/' in name or ',' in name:
            # Show error for invalid memory name
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_name,
                error_msg=_('The memory name is invalid'))
        elif self.model.get_iter(name):
            # Show error for existing memory name
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_name,
                error_msg=_('A memory with that name already exists'))
        elif len(description) == 0:
            # Show error for missing description name
            self.do_show_error_message_on_infobar(
                widget=self.ui.entry_description,
                error_msg=_('The memory description is missing'))
        else:
            self.ui.dialog.response(Gtk.ResponseType.OK)

    def on_entry_description_changed(self, widget):
        """Check the memory description field"""
        check_invalid_input(widget=widget,
                            empty=False,
                            separators=True,
                            invalid_chars=True)

    def on_entry_name_changed(self, widget):
        """Check the memory name field"""
        check_invalid_input(widget=widget,
                            empty=False,
                            separators=False,
                            invalid_chars=False)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)
