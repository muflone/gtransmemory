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

import json

from gi.repository import Gtk

from gtransmemory.gtkbuilder_loader import GtkBuilderLoader
from gtransmemory.functions import (
    check_invalid_input, get_ui_file, get_treeview_selected_row,
    set_error_message_on_infobar, text, _)
import gtransmemory.preferences as preferences
import gtransmemory.settings as settings

from gtransmemory.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'message'


class UIMessage(object):
    def __init__(self, parent, messages):
        """Prepare the message dialog"""
        self.messages = messages
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('message.ui'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_message.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_message, SECTION_WINDOW_NAME)
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
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        self.selected_iter = None
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_message, default_translation, default_source,
             title, treeiter):
        """Show the dialog"""
        self.ui.txt_message.set_text(default_message)
        self.ui.txt_translation.set_text(default_translation)
        self.ui.txt_source.set_text(default_source)
        self.ui.txt_message.grab_focus()
        self.ui.dialog_message.set_title(title)
        self.selected_iter = treeiter
        # Show the dialog
        response = self.ui.dialog_message.run()
        self.ui.dialog_message.hide()
        self.message = self.ui.txt_message.get_text().strip()
        self.translation = self.ui.txt_translation.get_text().strip()
        self.source = self.ui.txt_source.get_text().strip()
        return response

    def destroy(self):
        """Destroy the dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_message, SECTION_WINDOW_NAME)
        self.ui.dialog_message.destroy()
        self.ui.dialog_message = None

    def on_action_confirm_activate(self, action):
        """Check che message configuration before confirm"""
        def show_error_message_on_infobar(widget, error_msg):
            """Show the error message on the GtkInfoBar"""
            set_error_message_on_infobar(
                widget=widget,
                widgets=(self.ui.txt_message, self.ui.txt_translation),
                label=self.ui.lbl_error_message,
                infobar=self.ui.infobar_error_message,
                error_msg=error_msg)
        message = self.ui.txt_message.get_text().strip()
        if len(message) == 0:
            # Show error for missing message
            show_error_message_on_infobar(
                self.ui.txt_message,
                _('The message is missing'))
        elif self.messages.get_iter(message) not in (None, self.selected_iter):
            # Show error for existing message
            show_error_message_on_infobar(
                self.ui.txt_message,
                _('The specified message already exists'))
        else:
            self.ui.dialog_message.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_txt_message_changed(self, widget):
        """Check the message field"""
        check_invalid_input(widget, False, True, True)
