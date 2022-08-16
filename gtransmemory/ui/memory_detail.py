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

from gi.repository import Gtk

import gtransmemory.preferences as preferences
from gtransmemory.gtkbuilder_loader import GtkBuilderLoader
from gtransmemory.functions import (
    check_invalid_input, get_ui_file, set_error_message_on_infobar, text, _)


class UIMemoryDetail(object):
    def __init__(self, parent, groups):
        """Prepare the group detail dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('memory_detail.ui'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_edit_memory.set_transient_for(parent)
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
        self.model = groups
        self.name = ''
        self.description = ''
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_name, default_description, title, treeiter):
        """Show the Group detail dialog"""
        self.ui.txt_name.set_text(default_name)
        self.ui.txt_name.grab_focus()
        self.ui.txt_description.set_text(default_description)
        self.ui.dialog_edit_memory.set_title(title)
        response = self.ui.dialog_edit_memory.run()
        self.ui.dialog_edit_memory.hide()
        self.name = self.ui.txt_name.get_text().strip()
        self.description = self.ui.txt_description.get_text().strip()
        return response

    def destroy(self):
        """Destroy the Group detail dialog"""
        self.ui.dialog_edit_memory.destroy()
        self.ui.dialog_edit_memory = None

    def on_action_confirm_activate(self, action):
        """Check che group configuration before confirm"""
        def show_error_message_on_infobar(widget, error_msg):
            """Show the error message on the GtkInfoBar"""
            set_error_message_on_infobar(
                widget=widget,
                widgets=(self.ui.txt_name, self.ui.txt_description),
                label=self.ui.lbl_error_message,
                infobar=self.ui.infobar_error_message,
                error_msg=error_msg)
        name = self.ui.txt_name.get_text().strip()
        description = self.ui.txt_description.get_text().strip()
        if len(name) == 0:
            # Show error for missing memory name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The memory name is missing'))
        elif '\'' in name or '\\' in name or '/' in name or ',' in name:
            # Show error for invalid memory name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The memory name is invalid'))
        elif self.model.get_iter(name):
            # Show error for existing memory name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('A memory with that name already exists'))
        elif len(description) == 0:
            # Show error for missing description name
            show_error_message_on_infobar(
                self.ui.txt_description,
                _('The memory description is missing'))
        else:
            self.ui.dialog_edit_memory.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_txt_name_changed(self, widget):
        """Check the memory name field"""
        check_invalid_input(widget, False, False, False)

    def on_txt_description_changed(self, widget):
        """Check the memory description field"""
        check_invalid_input(widget, False, True, True)
