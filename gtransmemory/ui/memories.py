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

from gtransmemory.constants import DIR_MEMORIES
from gtransmemory.functions import get_treeview_selected_row
from gtransmemory.localize import _, text
from gtransmemory.models.memory_db import MemoryDB
from gtransmemory.models.memories import ModelMemories
from gtransmemory.models.memory_info import MemoryInfo
from gtransmemory.ui.base import UIBase
from gtransmemory.ui.memory_detail import UIMemoryDetail
from gtransmemory.ui.message_dialog import (show_message_dialog,
                                            UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'memories'


class UIMemories(UIBase):
    def __init__(self, parent, settings, options):
        """Prepare the dialog"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='memories.ui')
        # Initialize members
        self.parent = parent
        self.settings = settings
        self.options = options
        self.selected_iter = None
        # Load UI
        self.load_ui()
        # Prepare the models
        self.model = ModelMemories(self.ui.model_memories)
        # Complete initialization
        self.startup()

    def load_ui(self):
        """Load the interface UI"""
        logging.debug(f'{self.__class__.__name__} load UI')
        # Initialize titles and tooltips
        self.set_titles()
        # Set various properties
        self.ui.dialog.set_transient_for(self.parent)
        self.set_buttons_icons(buttons=[self.ui.button_add,
                                        self.ui.button_remove])
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def startup(self):
        """Complete initialization"""
        logging.debug(f'{self.__class__.__name__} startup')
        # Sort the data in the models
        self.model.model.set_sort_column_id(
            self.ui.column_description.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.dialog,
                                              section=SECTION_WINDOW_NAME)

    def show(self):
        """Show the dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.dialog.run()
        self.ui.dialog.hide()

    def destroy(self):
        """Destroy the dialog"""
        logging.debug(f'{self.__class__.__name__} destroy')
        self.settings.save_window_position(window=self.ui.dialog,
                                           section=SECTION_WINDOW_NAME)
        self.ui.dialog.destroy()
        self.ui.dialog = None

    def on_action_add_activate(self, widget):
        """Add a new memory"""
        dialog = UIMemoryDetail(parent=self.ui.dialog,
                                settings=self.settings,
                                options=self.options,
                                model=self.model)
        if dialog.show(default_name='',
                       default_description='',
                       title=_('Add new memory')) == Gtk.ResponseType.OK:
            database_name = f'{dialog.name}.sqlite3'
            db = MemoryDB(database_name)
            db.set_description(dialog.description)
            db.close()
            self.model.add_data(MemoryInfo(name=dialog.name,
                                           filename=database_name,
                                           description=dialog.description))
        dialog.destroy()

    def on_action_remove_activate(self, widget):
        """Remove the selected memory"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        memory_name = (self.model.get_filename(selected_row)
                       if selected_row else '')
        memory_description = (self.model.get_description(selected_row)
                              if selected_row else '')
        if selected_row and memory_name and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.dialog,
                message_type=Gtk.MessageType.WARNING,
                title=None,
                msg1=_('Remove the memory'),
                msg2=_(f'Remove the memory {memory_description}?'),
                is_response_id=Gtk.ResponseType.YES):
            memory_path = DIR_MEMORIES / memory_name
            memory_path.unlink()
            self.model.remove(selected_row)
