##
#     Project: gTransMemory
# Description: Translator with learning memory
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

import polib
from gi.repository import Gtk
from gi.repository import Gdk

from gtransmemory.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, DIR_MEMORIES)
from gtransmemory.functions import (
    get_ui_file, get_treeview_selected_row, show_popup_menu, create_filefilter,
    text, _)
import gtransmemory.preferences as preferences
import gtransmemory.settings as settings
from gtransmemory.gtkbuilder_loader import GtkBuilderLoader

from gtransmemory.models.memory_db import MemoryDB
from gtransmemory.models.message_info import MessageInfo
from gtransmemory.models.messages import ModelMessages
from gtransmemory.models.memory_info import MemoryInfo
from gtransmemory.models.memories import ModelMemories

from gtransmemory.ui.about import UIAbout
from gtransmemory.ui.memories import UIMemories
from gtransmemory.ui.message import UIMessage
from gtransmemory.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)
from gtransmemory.ui.messages_import import UIMessagesImport

SECTION_WINDOW_NAME = 'main'


class UIMain(object):
    def __init__(self, application):
        self.application = application
        # Load settings
        settings.settings = settings.Settings(FILE_SETTINGS, False)
        settings.positions = settings.Settings(FILE_WINDOWS_POSITION, False)
        preferences.preferences = preferences.Preferences()
        self.loadUI()
        self.model_messages = ModelMessages(self.ui.store_messages)
        self.model_memories = ModelMemories(self.ui.store_memories)
        self.database = None
        # Load the messages list
        self.messages = {}
        self.reload_memories()
        # Sort the data in the models
        self.model_memories.model.set_sort_column_id(
            self.ui.column_memory.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        self.model_messages.model.set_sort_column_id(
            self.ui.column_message.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Automatically select the first memory if any
        if self.model_memories.count() > 0:
            self.ui.tvw_memories.set_cursor(0)
            # Automatically select the first messages if any
            if self.model_messages.count() > 0:
                self.ui.tvw_messages.set_cursor(0)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader(get_ui_file('main.ui'))
        self.ui.win_main.set_application(self.application)
        self.ui.win_main.set_title(APP_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            label = widget.get_label()
            if not label:
                label = widget.get_short_label()
            widget.set_label(text(label))
            widget.set_short_label(label)
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        # Set list items row height
        icon_size = preferences.ICON_SIZE
        self.ui.cell_message.props.height = preferences.get(icon_size)
        self.ui.cell_memory_description.props.height = (
            preferences.get(icon_size))
        # Set memories visibility
        self.ui.scroll_memories.set_visible(
            preferences.get(preferences.MEMORIES_SHOW))
        # Add a Gtk.Headerbar, only for GTK+ 3.10.0 and higher
        if (not Gtk.check_version(3, 10, 0) and
                not preferences.get(preferences.HEADERBARS_DISABLE)):
            self.load_ui_headerbar()
            if preferences.get(preferences.HEADERBARS_REMOVE_TOOLBAR):
                # This is only for development, it should always be True
                # Remove the redundant toolbar
                self.ui.toolbar_main.destroy()
            # Flatten the Gtk.ScrolledWindows
            self.ui.scroll_memories.set_shadow_type(Gtk.ShadowType.NONE)
            self.ui.scroll_messages.set_shadow_type(Gtk.ShadowType.NONE)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def load_ui_headerbar(self):
        """Add a Gtk.HeaderBar to the window with buttons"""
        def create_button_from_action(action):
            """Create a new Gtk.Button from a Gtk.Action"""
            if isinstance(action, Gtk.ToggleAction):
                new_button = Gtk.ToggleButton()
            else:
                new_button = Gtk.Button()
            new_button.set_use_action_appearance(False)
            new_button.set_related_action(action)
            # Use icon from the action
            icon_name = action.get_icon_name()
            if preferences.get(preferences.HEADERBARS_SYMBOLIC_ICONS):
                icon_name += '-symbolic'
            # Get desired icon size
            icon_size = (Gtk.IconSize.BUTTON
                         if preferences.get(preferences.HEADERBARS_SMALL_ICONS)
                         else Gtk.IconSize.LARGE_TOOLBAR)
            new_button.set_image(Gtk.Image.new_from_icon_name(icon_name,
                                                              icon_size))
            # Set the tooltip from the action label
            new_button.set_tooltip_text(action.get_label().replace('_', ''))
            return new_button
        # Add the Gtk.HeaderBar
        header_bar = Gtk.HeaderBar()
        header_bar.props.title = self.ui.win_main.get_title()
        header_bar.set_show_close_button(True)
        self.ui.win_main.set_titlebar(header_bar)
        # Add buttons to the left side
        for action in (self.ui.action_new,
                       self.ui.action_import,
                       self.ui.action_edit,
                       self.ui.action_delete):
            header_bar.pack_start(create_button_from_action(action))
        # Add buttons to the right side (in reverse order)
        for action in reversed((self.ui.action_memories,
                                self.ui.action_about)):
            header_bar.pack_end(create_button_from_action(action))

    def run(self):
        """Show the UI"""
        self.ui.win_main.show_all()

    def on_win_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        settings.positions.save_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)
        settings.positions.save()
        settings.settings.save()
        if self.database:
            self.database.close()
        self.application.quit()

    def on_action_about_activate(self, action):
        """Show the about dialog"""
        dialog = UIAbout(self.ui.win_main)
        dialog.show()
        dialog.destroy()

    def on_action_quit_activate(self, action):
        """Close the application by closing the main window"""
        event = Gdk.Event()
        event.key.type = Gdk.EventType.DELETE
        self.ui.win_main.event(event)

    def reload_messages(self):
        """Load messages from the database memory"""
        if self.database:
            self.database.close()
        self.model_messages.clear()
        self.messages.clear()
        memory_path = self.model_memories.get_filename(
            get_treeview_selected_row(self.ui.tvw_memories))
        self.database = MemoryDB(memory_path)
        for msgid, translation, source in self.database.get_messages():
            message = MessageInfo(msgid.replace('\n', '\\n'),
                                  translation.replace('\n', '\\n'),
                                  source)
            self.add_message(message, False)
        self.ui.action_new.set_sensitive(True)

    def add_message(self, message, update_settings):
        """Add a new message to the data and to the model"""
        self.messages[message.key] = message
        if message.key not in self.model_messages.rows:
            self.model_messages.add_data(message)
        else:
            self.model_messages.set_data(self.model_messages.rows[message.key],
                                         message)
        # Update settings file if requested
        if update_settings:
            self.database.add_message(message)

    def remove_message(self, message, update_settings):
        """Remove a message"""
        self.messages.pop(message.key)
        self.model_messages.remove(self.model_messages.get_iter(message.key))
        if update_settings:
            self.database.remove_message(message)

    def reload_memories(self):
        """Load memories from memories folder"""
        self.model_memories.clear()
        for filename in os.listdir(DIR_MEMORIES):
            file_path = os.path.join(DIR_MEMORIES, filename)
            if (os.path.isfile(file_path) and filename.endswith('sqlite3')):
                # For each database add a new memory object
                database = MemoryDB(file_path)
                name = os.path.splitext(filename)[0]
                description = database.get_description() or filename
                self.model_memories.add_data(MemoryInfo(name,
                                                        filename,
                                                        description))
                database.close()

    def on_action_new_activate(self, action):
        """Define a new message"""
        dialog = UIMessage(parent=self.ui.win_main,
                           messages=self.model_messages)
        response = dialog.show(default_message='',
                               default_translation='',
                               default_source='',
                               title=_('Add a new message'),
                               treeiter=None)
        if response == Gtk.ResponseType.OK:
            message = MessageInfo(dialog.message,
                                  dialog.translation,
                                  dialog.source)
            self.add_message(message=message,
                             update_settings=True)
            # Automatically select the newly added message
            self.ui.tvw_messages.set_cursor(
                path=self.model_messages.get_path_by_key(
                    '%s\%s' % (dialog.source, dialog.message)),
                column=None,
                start_editing=False)
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Edit an existing message"""
        selected_row = get_treeview_selected_row(self.ui.tvw_messages)
        if selected_row:
            key = self.model_messages.get_key(selected_row)
            message_id = self.model_messages.get_message(selected_row)
            messageid = self.model_messages.get_translation(selected_row)
            translation = self.model_messages.get_translation(selected_row)
            source = self.model_messages.get_source(selected_row)
            selected_iter = self.model_messages.get_iter(key)
            dialog = UIMessage(parent=self.ui.win_main,
                               messages=self.model_messages)
            # Show the edit message dialog
            response = dialog.show(default_message=message_id,
                                   default_translation=translation,
                                   default_source=source,
                                   title=_('Edit message'),
                                   treeiter=selected_iter)
            if response == Gtk.ResponseType.OK:
                # Remove older message and add the newer
                self.remove_message(message=MessageInfo(message_id,
                                                        '',
                                                        source),
                                    update_settings=True)
                message = MessageInfo(dialog.message,
                                      dialog.translation,
                                      dialog.source)
                self.add_message(message=message, update_settings=True)
                # Get the path of the message
                path = self.model_messages.get_path_by_key(
                    '%s\%s' % (dialog.source, dialog.message))
                # Automatically select again the previously selected message
                self.ui.tvw_messages.set_cursor(path=path,
                                                column=None,
                                                start_editing=False)

    def on_action_delete_activate(self, action):
        """Remove the selected message"""
        selected_row = get_treeview_selected_row(self.ui.tvw_messages)
        if selected_row and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.win_main,
                message_type=Gtk.MessageType.QUESTION,
                title=None,
                msg1=_('Remove message'),
                msg2=_('Remove the selected message?'),
                is_response_id=Gtk.ResponseType.YES):
            message = self.messages[self.model_messages.get_key(selected_row)]
            self.remove_message(message=message, update_settings=True)

    def on_action_import_activate(self, action):
        """Import messages from a PO/POT file"""
        # Show the import file dialog
        dialog = UIMessagesImport(self.ui.win_main)
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('GNU gettext translation files'),
                              None,
                              ('*.po', '*.pot')))
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('All Files'),
                              None,
                              ('*', )))
        response = dialog.show(_('Import messages from file'))
        if response == Gtk.ResponseType.OK:
            # Load messages from a gettext PO/POT file
            for entry in polib.pofile(dialog.filename):
                message = MessageInfo(entry.msgid,
                                      entry.msgstr,
                                      dialog.source)
                self.add_message(message=message, update_settings=True)
        dialog.destroy()

    def on_tvw_messages_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        selected_row = get_treeview_selected_row(self.ui.tvw_messages)
        if selected_row:
            # Start message edit
            self.ui.action_edit.activate()

    def get_current_memory_path(self):
        """Return the name of the currently selected memory"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        return self.model_memories.get_key(selected_row)

    def on_action_memories_activate(self, widget):
        """Edit memories"""
        dialog = UIMemories(parent=self.ui.win_main)
        dialog.model = self.model_memories
        dialog.ui.tvw_memories.set_model(self.model_memories.model)
        dialog.show()
        dialog.destroy()

    def on_tvw_memories_button_release_event(self, widget, event):
        """Show memories popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            show_popup_menu(self.ui.menu_memories, event.button)

    def on_tvw_messages_button_release_event(self, widget, event):
        """Show connections popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            show_popup_menu(self.ui.menu_messages, event.button)

    def on_action_memories_previous_activate(self, action):
        """Move to the previous memory"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        new_iter = self.model_memories.model.iter_previous(selected_row)
        if new_iter:
            # Select the newly selected row in the memories list
            new_path = self.model_memories.get_path(new_iter)
            self.ui.tvw_memories.set_cursor(new_path)

    def on_action_memories_next_activate(self, action):
        """Move to the next memory"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        new_iter = self.model_memories.model.iter_next(selected_row)
        if new_iter:
            # Select the newly selected row in the memories list
            new_path = self.model_memories.get_path(new_iter)
            self.ui.tvw_memories.set_cursor(new_path)

    def on_tvw_selection_memories_changed(self, widget):
        """Set action sensitiveness on selection change"""
        selected_row = get_treeview_selected_row(self.ui.tvw_memories)
        self.ui.actions_messages.set_sensitive(bool(selected_row))
        self.model_messages.clear()
        if selected_row:
            self.reload_messages()
            # Automatically select the first message for the memory
            self.ui.tvw_messages.set_cursor(0)
        else:
            self.ui.actions_message.set_sensitive(False)

    def on_tvw_selection_messages_changed(self, widget):
        """Set action sensitiveness on selection change"""
        selected_row = get_treeview_selected_row(self.ui.tvw_messages)
        self.ui.actions_message.set_sensitive(bool(selected_row))
