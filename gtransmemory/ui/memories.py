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

from gi.repository import Gtk

from gtransmemory.gtkbuilder_loader import GtkBuilderLoader
from gtransmemory.constants import DIR_MEMORIES
from gtransmemory.functions import (get_ui_file,
                                    get_treeview_selected_row)
from gtransmemory.localize import _, text
import gtransmemory.preferences as preferences
import gtransmemory.settings as settings

from gtransmemory.models.memory_db import MemoryDB
from gtransmemory.models.memories import ModelMemories
from gtransmemory.models.memory_info import MemoryInfo

from gtransmemory.ui.memory_detail import UIMemoryDetail
from gtransmemory.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'memories'


class UIMemories(object):
    def __init__(self, parent):
        """Prepare the memories dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('memories.ui'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_memories.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_memories, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.Button):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        # Load the memories
        self.model = ModelMemories(self.ui.store_memories)
        self.selected_iter = None
        # Sort the data in the models
        self.model.model.set_sort_column_id(
            self.ui.column_description.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self):
        """Show the dialog"""
        self.ui.dialog_memories.run()
        self.ui.dialog_memories.hide()

    def destroy(self):
        """Destroy the dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_memories, SECTION_WINDOW_NAME)
        self.ui.dialog_memories.destroy()
        self.ui.dialog_memories = None

    def on_action_add_activate(self, action):
        """Add a new memory"""
        dialog = UIMemoryDetail(self.ui.dialog_memories, self.model)
        if dialog.show(default_name='',
                       default_description='',
                       title=_('Add new memory'),
                       treeiter=None) == Gtk.ResponseType.OK:
            database_name = '%s.sqlite3' % dialog.name
            db = MemoryDB(database_name)
            db.set_description(dialog.description)
            db.close()
            self.model.add_data(MemoryInfo(name=dialog.name,
                                           filename=database_name,
                                           description=dialog.description))
        dialog.destroy()

    def on_action_remove_activate(self, action):
        """Remove the selected memory"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        memory_name = (self.model.get_filename(selected_row)
                       if selected_row else '')
        memory_description = (self.model.get_description(selected_row)
                              if selected_row else '')
        if selected_row and memory_name and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.dialog_memories,
                message_type=Gtk.MessageType.WARNING,
                title=None,
                msg1=_('Remove the memory'),
                msg2=_('Remove the memory %s?') % memory_description,
                is_response_id=Gtk.ResponseType.YES):
            memory_path = os.path.join(DIR_MEMORIES, memory_name)
            os.remove(memory_path)
            self.model.remove(selected_row)
