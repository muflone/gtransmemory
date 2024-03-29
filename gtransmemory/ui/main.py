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

import copy
import logging
import pathlib

import polib

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from gtransmemory.constants import (APP_NAME,
                                    DIR_MEMORIES,
                                    FILE_ICON,
                                    FILE_SETTINGS)
from gtransmemory.functions import (get_treeview_selected_row,
                                    create_filefilter,
                                    process_events)
from gtransmemory.localize import _, text
from gtransmemory.settings import (Settings,
                                   PREFERENCES_ICON_SIZE)
from gtransmemory.models.memory_db import MemoryDB
from gtransmemory.models.message_info import MessageInfo
from gtransmemory.models.messages import ModelMessages
from gtransmemory.models.memory_info import MemoryInfo
from gtransmemory.models.memories import ModelMemories
from gtransmemory.models.source_info import SourceInfo
from gtransmemory.models.sources import ModelSource
from gtransmemory.ui.about import UIAbout
from gtransmemory.ui.base import UIBase
from gtransmemory.ui.shortcuts import UIShortcuts
from gtransmemory.ui.memories import UIMemories
from gtransmemory.ui.message import UIMessage
from gtransmemory.ui.messages_import_file import UIMessagesImportFile
from gtransmemory.ui.messages_import_folder import UIMessagesImportFolder

SECTION_WINDOW_NAME = 'main'


class UIMain(UIBase):
    def __init__(self, application, options):
        """Prepare the main window"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='main.ui')
        # Initialize members
        self.application = application
        self.options = options
        self.database = None
        self.selected_count = 0
        self.loading_id = None
        self.loading_cancel = False
        self.latest_directory = None
        self.messages = {}
        # Load settings
        self.settings = Settings(filename=FILE_SETTINGS,
                                 case_sensitive=True)
        self.settings.load_preferences()
        self.settings_map = {}
        # Load UI
        self.load_ui()
        # Prepare the models
        self.model_memories = ModelMemories(self.ui.model_memories)
        self.model_messages = ModelMessages(self.ui.model_messages)
        self.model_sources = ModelSource(self.ui.model_sources)
        # Complete initialization
        self.startup()

    def load_ui(self):
        """Load the interface UI"""
        logging.debug(f'{self.__class__.__name__} load UI')
        # Initialize titles and tooltips
        self.set_titles()
        self.ui.entry_search.set_tooltip_text(text('Search'))
        self.ui.entry_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY, text('Search'))
        self.ui.entry_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.SECONDARY, text('Clear'))
        # Initialize Gtk.HeaderBar
        self.ui.header_bar.props.title = self.ui.window.get_title()
        self.ui.window.set_titlebar(self.ui.header_bar)
        self.set_buttons_icons(buttons=[self.ui.button_messages_add,
                                        self.ui.button_messages_import,
                                        self.ui.button_messages_edit,
                                        self.ui.button_messages_remove,
                                        self.ui.button_messages_search,
                                        self.ui.button_messages_selection,
                                        self.ui.button_memories,
                                        self.ui.button_about,
                                        self.ui.button_options,
                                        self.ui.button_search_close])
        # Set various properties
        self.ui.window.set_title(APP_NAME)
        self.ui.window.set_icon_from_file(str(FILE_ICON))
        self.ui.window.set_application(self.application)
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def startup(self):
        """Complete initialization"""
        logging.debug(f'{self.__class__.__name__} startup')
        self.settings_map = {}
        # Load settings
        for setting_name, action in self.settings_map.items():
            action.set_active(self.settings.get_preference(
                option=setting_name))
        # Set list items row height
        icon_size = self.settings.get_preference(PREFERENCES_ICON_SIZE)
        self.ui.cell_message.props.height = icon_size
        self.ui.cell_memory_description.props.height = icon_size
        # Load the messages list
        self.do_reload_memories()
        # Sort the data in the models
        self.model_memories.model.set_sort_column_id(
            self.ui.column_memory.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        self.model_messages.model.set_sort_column_id(
            self.ui.column_message.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Prepare filter results by cleaned message (case insensitively)
        self.ui.filter_messages.set_visible_func(self.do_filter_message)
        # Automatically select the first memory if any
        if len(self.model_memories) > 0:
            self.ui.tvw_memories.set_cursor(0)
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.window,
                                              section=SECTION_WINDOW_NAME)

    def run(self):
        """Show the UI"""
        self.ui.window.show_all()

    def do_add_message(self, message, update_data):
        """Add a new message to the model"""
        self.messages[message.key] = message
        if message.key not in self.model_messages.rows:
            # Add new row in the model
            self.model_messages.add_data(item=message)
        else:
            # Edit existing model row
            self.model_messages.set_item(
                treeiter=self.model_messages.rows[message.key],
                item=message)
        # Update database if requested
        if update_data:
            self.database.add_message(message)

    def do_filter_message(self, model, treeiter, data):
        """Compare the message text for filtering"""
        result = True
        # Filter results only when the search is active
        if self.ui.action_search.get_active():
            search_text = self.ui.entry_search.get_text()
            if search_text.startswith('source:'):
                # Filter by source
                text = self.model_messages.get_source(treeiter)
                search_text = search_text[7:]
            else:
                # Filter by cleaned message
                text = self.model_messages.get_cleaned_message(treeiter)
            result = search_text.casefold() in text.casefold()
        return result

    def do_reload_memories(self):
        """Load memories from memories folder"""
        self.model_memories.clear()
        for filename in DIR_MEMORIES.glob('*'):
            if filename.is_file() and filename.suffix == '.sqlite3':
                # Open the database file to get its description
                database = MemoryDB(file_path=filename)
                description = database.get_description() or filename.name
                # Add each database to the memories model
                self.model_memories.add_data(
                    MemoryInfo(name=str(filename.with_suffix(suffix='').name),
                               filename=str(filename),
                               description=description,
                               languages=database.get_languages()))
                database.close()

    def do_reload_messages(self, filename):
        """Load messages from the database memory"""
        def do_reload(messages):
            """Add each message to the messages model"""
            step = 0
            count = len(messages)
            # Load messages
            for msgid, translation, source in messages:
                # Break a previous loading
                if self.loading_cancel:
                    break
                # Add the new message to the messages model
                message = MessageInfo(
                    msgid=msgid.replace('\n', '\\n'),
                    translation=translation.replace('\n', '\\n'),
                    source=source)
                self.do_add_message(message=message,
                                    update_data=False)
                # Update the loading ProgressBar
                step += 1
                self.ui.progress_loading.set_fraction(1.0 / count * step)
                self.ui.progress_loading.set_text(
                    _('Loading message {STEP} of {COUNT}').format(STEP=step,
                                                                  COUNT=count))
                # Allow the thread to repeat for the next iteration
                yield True
            if not self.loading_cancel:
                self.ui.actions_search.set_sensitive(True)
                self.ui.actions_messages.set_sensitive(True)
                self.ui.actions_selection.set_sensitive(True)
                self.ui.progress_loading.set_text(
                    _('Loaded {COUNT} messages').format(COUNT=count))
            # Operation completed, stop the thread
            self.loading_id = None
            self.loading_cancel = False
            yield False
        # Close any previously opened database
        if self.database:
            self.database.close()
        # Cancel any previously running loading
        if self.loading_id:
            self.loading_cancel = True
            process_events()
        # Clear previos data
        self.model_messages.clear()
        self.messages.clear()
        self.ui.progress_loading.set_fraction(0.0)
        # Disable buttons while loading the memory database
        self.ui.actions_search.set_sensitive(False)
        self.ui.actions_messages.set_sensitive(False)
        self.ui.actions_selection.set_sensitive(False)
        # Load the memory database
        self.database = MemoryDB(filename)
        # Start messages loading in an idle thread
        task = do_reload(self.database.get_messages())
        self.loading_id = GObject.idle_add(task.__next__)

    def do_reload_sources(self):
        """Load sources from memories folder"""
        sources = set()
        self.database.commit()
        for filename in DIR_MEMORIES.glob('*'):
            if filename.is_file() and filename.suffix == '.sqlite3':
                # Open the database file
                database = MemoryDB(file_path=filename)
                # Get every sources in the database
                for source in database.get_sources():
                    sources.add(source[0])
                database.close()
        self.model_sources.clear()
        for source in sources:
            self.model_sources.add_data(SourceInfo(source=source))

    def do_remove_message(self, message, update_data):
        """Remove a message from the model"""
        self.messages.pop(message.key)
        self.model_messages.remove(
            treeiter=self.model_messages.get_iter(message.key))
        # Update database if requested
        if update_data:
            self.database.remove_message(
                message=MessageInfo(msgid=message.msgid.replace('\\n', '\n'),
                                    translation=message.translation,
                                    source=message.source))

    def on_action_about_activate(self, widget):
        """Show the information dialog"""
        dialog = UIAbout(parent=self.ui.window,
                         settings=self.settings,
                         options=self.options)
        dialog.show()
        dialog.destroy()

    def on_action_shortcuts_activate(self, widget):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(parent=self.ui.window,
                             settings=self.settings,
                             options=self.options)
        dialog.show()

    def on_action_quit_activate(self, widget):
        """Save the settings and close the application"""
        logging.debug(f'{self.__class__.__name__} quit')
        self.settings.save_window_position(window=self.ui.window,
                                           section=SECTION_WINDOW_NAME)
        self.settings.save()
        # Close any previously opened database
        if self.database:
            self.database.close()
        self.application.quit()

    def on_action_messages_add_activate(self, widget):
        """Add a new message to the messages model"""
        dialog = UIMessage(parent=self.ui.window,
                           settings=self.settings,
                           options=self.options,
                           messages=self.model_messages)
        response = dialog.show(default_message='',
                               default_translation='',
                               default_source='',
                               title=_('Add a new message'),
                               treeiter=None)
        if response == Gtk.ResponseType.OK:
            message = MessageInfo(msgid=dialog.message,
                                  translation=dialog.translation,
                                  source=dialog.source)
            self.do_add_message(message=message,
                                update_data=True)
            # Automatically select the newly added message
            self.ui.tvw_messages.set_cursor(
                path=self.model_messages.get_path_by_name(
                    f'{dialog.source}\\{dialog.message}'),
                column=None,
                start_editing=False)
        dialog.destroy()

    def on_action_messages_edit_activate(self, widget):
        """Edit an existing message in the messages model"""
        treeiter = get_treeview_selected_row(self.ui.tvw_messages)
        if treeiter:
            if self.ui.action_search.get_active():
                # Find the currently filtered iter
                treeiter = self.ui.filter_messages.convert_iter_to_child_iter(
                    treeiter)
            key = self.model_messages.get_key(treeiter)
            message_id = self.model_messages.get_message(treeiter)
            translation = self.model_messages.get_translation(treeiter)
            source = self.model_messages.get_source(treeiter)
            selected_iter = self.model_messages.get_iter(key)
            dialog = UIMessage(parent=self.ui.window,
                               settings=self.settings,
                               options=self.options,
                               messages=self.model_messages)
            # Show the edit message dialog
            response = dialog.show(default_message=message_id,
                                   default_translation=translation,
                                   default_source=source,
                                   title=_('Edit message'),
                                   treeiter=selected_iter)
            if response == Gtk.ResponseType.OK:
                # Remove the older message and add the newer
                self.do_remove_message(message=MessageInfo(msgid=message_id,
                                                           translation='',
                                                           source=source),
                                       update_data=True)
                message = MessageInfo(msgid=dialog.message,
                                      translation=dialog.translation,
                                      source=dialog.source)
                self.do_add_message(message=message,
                                    update_data=True)
                # Get the path of the message
                path = self.model_messages.get_path_by_name(
                    f'{dialog.source}\\{dialog.message}')
                if self.ui.action_search.get_active():
                    # Find the currently filtered path
                    path = self.ui.filter_messages.convert_child_path_to_path(
                        path)
                # Automatically select again the previously selected message
                self.ui.tvw_messages.set_cursor(path=path,
                                                column=None,
                                                start_editing=False)
            dialog.destroy()

    def on_action_messages_remove_activate(self, widget):
        """Remove the selected items from the messages model"""
        for key, row in copy.copy(list(self.model_messages.rows.items())):
            if self.model_messages.get_selection(row):
                message = self.messages[key]
                self.do_remove_message(message=message,
                                       update_data=True)
        # Deactivate the selection mode
        self.ui.action_selection.set_active(False)
        # Disable the remove selection actions
        self.ui.actions_messages_remove.set_sensitive(False)

    def on_action_messages_import_folder_activate(self, widget):
        """Import messages from a folder"""
        # Show the import folder dialog
        dialog = UIMessagesImportFolder(parent=self.ui.window,
                                        settings=self.settings,
                                        options=self.options)
        self.do_reload_sources()
        response = dialog.show(model_sources=self.ui.model_sources)
        if response == Gtk.ResponseType.OK:
            path_directory = pathlib.Path(dialog.directory)
            if path_directory.exists() and path_directory.is_dir():
                # Search all .po files contained in the selected folder
                for filename in path_directory.glob('*.po'):
                    # Find the databases with the same language
                    languages = self.model_memories.find_language(
                        language=filename.with_suffix('').name)
                    if languages:
                        # Use the database for the first language found
                        language, treeiter = languages[0]
                        database = MemoryDB(
                            self.model_memories.get_filename(treeiter))
                        logging.info(f'Importing file "{filename}" '
                                     f'to memory {database.get_description()} '
                                     f'({database.filename})')
                        for entry in polib.pofile(str(filename)):
                            # Add the message to the database
                            message = MessageInfo(msgid=entry.msgid,
                                                  translation=entry.msgstr,
                                                  source=dialog.source)
                            database.add_message(message=message)
                        database.close()
                    else:
                        # No existing database is available for the language
                        logging.warning(f'No available language found for '
                                        f'"{filename}"')
                # Reload the current memory
                self.ui.tvw_selection_memories.emit('changed')
        dialog.destroy()

    def on_action_messages_import_file_activate(self, widget):
        """Import messages from a PO/POT file"""
        # Show the import file dialog
        dialog = UIMessagesImportFile(parent=self.ui.window,
                                      settings=self.settings,
                                      options=self.options,
                                      initial_dir=self.latest_directory)
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('GNU gettext translation files'),
                              None,
                              ('*.po', '*.pot')))
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('All files'),
                              None,
                              ('*', )))
        self.do_reload_sources()
        response = dialog.show(model_sources=self.ui.model_sources)
        if response == Gtk.ResponseType.OK:
            # Load messages from a gettext PO/POT file
            for entry in polib.pofile(dialog.filename):
                # Add the message to the messages model
                message = MessageInfo(msgid=entry.msgid,
                                      translation=entry.msgstr,
                                      source=dialog.source)
                self.do_add_message(message=message,
                                    update_data=True)
            # Save the directory path for the latest imported file
            self.latest_directory = pathlib.Path(dialog.filename).parent
        dialog.destroy()

    def on_action_memories_activate(self, widget):
        """Edit memories"""
        treeiter = get_treeview_selected_row(self.ui.tvw_memories)
        if treeiter:
            selected_name = self.model_memories.get_key(treeiter)
        self.ui.tvw_selection_memories.unselect_all()
        dialog = UIMemories(parent=self.ui.window,
                            settings=self.settings,
                            options=self.options)
        # Use the already loaded model
        dialog.model = self.model_memories
        dialog.ui.tvw_memories.set_model(self.model_memories.model)
        dialog.show()
        dialog.destroy()
        # Restore the previous memory if it's still available
        if treeiter and selected_name in self.model_memories.rows:
            self.ui.tvw_memories.get_selection().select_iter(
                self.model_memories.rows[selected_name])

    def on_action_memories_previous_activate(self, widget):
        """Move to the previous memory"""
        treeiter = get_treeview_selected_row(self.ui.tvw_memories)
        if treeiter:
            treeiter = self.model_memories.model.iter_previous(treeiter)
            if treeiter:
                # Select the newly selected row in the memories list
                new_path = self.model_memories.get_path(treeiter=treeiter)
                self.ui.tvw_memories.set_cursor(new_path)

    def on_action_memories_next_activate(self, widget):
        """Move to the next memory"""
        treeiter = get_treeview_selected_row(self.ui.tvw_memories)
        if treeiter:
            treeiter = self.model_memories.model.iter_next(treeiter)
            if treeiter:
                # Select the newly selected row in the memories list
                new_path = self.model_memories.get_path(treeiter=treeiter)
                self.ui.tvw_memories.set_cursor(new_path)

    def on_action_selection_toggled(self, action):
        """Enable or disable the selection mode and change style accordingly"""
        selection_active = action.get_active()
        # Remove any previous selection
        for row in self.model_messages.rows.values():
            self.model_messages.set_selection(row, False)
        self.selected_count = 0
        # Change headerbar style
        style_context = self.ui.header_bar.get_style_context()
        if selection_active:
            style_context.add_class('selection-mode')
        else:
            style_context.remove_class('selection-mode')
        # Show/hide the column with the selection boxes
        self.ui.column_selection.set_visible(selection_active)
        # Enable/disable messages actions (add, import, edit) and memories list
        self.ui.actions_messages.set_sensitive(not selection_active)
        self.ui.actions_memories.set_sensitive(not selection_active)
        self.ui.tvw_memories.set_sensitive(not selection_active)
        # Disable the messages remove action (it will be enabled when the user
        # will select the rows using the selection boxes)
        if not selection_active:
            self.ui.actions_messages_remove.set_sensitive(False)

    def on_action_select_all_activate(self, widget):
        """Select or deselect all messages"""
        self.ui.action_selection.set_active(True)
        self.selected_count = 0
        # Determine to select or deselect all
        status = widget == self.ui.action_select_all
        # Iterate over all the Gtk.TreeIter
        for row in self.model_messages.rows.values():
            # Check if the row is filtered
            if self.ui.action_search.get_active():
                visible = self.ui.filter_messages.convert_child_iter_to_iter(
                    row)[0]
            else:
                # When no filter is used all rows are visible
                visible = True
            # Flag only visible rows
            if visible:
                self.model_messages.set_selection(row, status)
                if status:
                    self.selected_count += 1
        self.ui.actions_messages_remove.set_sensitive(self.selected_count)

    def on_action_search_toggled(self, widget):
        """Show and hide the search bar"""
        # Show and hide the child in the Gtk.Revealer
        self.ui.revealer_search.set_reveal_child(
            not self.ui.revealer_search.get_reveal_child())
        if self.ui.action_search.get_active():
            self.ui.entry_search.grab_focus()
            # Apply filter to messages
            self.ui.tvw_messages.set_model(self.ui.filter_messages)
            self.ui.filter_messages.refilter()
        else:
            # Restore model with all the messages
            self.ui.tvw_messages.set_model(self.ui.model_messages)

    def on_action_search_close_activate(self, widget):
        """Hide the search bar"""
        self.ui.action_search.set_active(False)

    def on_action_options_menu_activate(self, widget):
        """Open the options menu"""
        self.ui.button_options.clicked()

    def on_cell_selection_toggled(self, widget, treepath):
        """Toggle the selection status"""
        if self.ui.action_search.get_active():
            # Find the currently filtered path
            treepath = self.ui.filter_messages.convert_path_to_child_path(
                Gtk.TreePath().new_from_string(treepath))
        key = self.model_messages.get_key(treepath)
        treeiter = self.model_messages.get_iter(key)
        status = not self.model_messages.get_selection(treeiter)
        self.model_messages.set_selection(treeiter, status)
        # Set the selection action state
        self.selected_count += 1 if status else -1
        self.ui.actions_messages_remove.set_sensitive(self.selected_count)

    def on_entry_search_changed(self, widget):
        """Filter messages"""
        self.ui.filter_messages.refilter()

    def on_entry_search_icon_release(self, widget, icon_position, event):
        """Clear the search text by clicking the icon next to the Gtk.Entry"""
        if icon_position == Gtk.EntryIconPosition.SECONDARY:
            self.ui.entry_search.set_text('')

    def on_tvw_messages_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        treeiter = get_treeview_selected_row(self.ui.tvw_messages)
        if treeiter and not self.ui.action_selection.get_active():
            # Start message edit
            self.ui.action_messages_edit.activate()

    def on_tvw_messages_button_release_event(self, widget, event):
        """Show popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            if self.ui.action_selection.get_active():
                # Show selection menu
                self.ui.menu_options_selection.popup_at_pointer(event)
            else:
                # Show messages menu
                self.ui.menu_messages.popup_at_pointer(event)

    def on_tvw_selection_memories_changed(self, widget):
        """Set action sensitiveness on selection change"""
        treeiter = get_treeview_selected_row(self.ui.tvw_memories)
        if treeiter:
            # Load the messages from the memory database
            self.do_reload_messages(
                filename=self.model_memories.get_filename(treeiter))
        else:
            # Cancel any previous loading
            if self.loading_id:
                self.loading_cancel = True
            self.ui.actions_search.set_sensitive(False)
            self.ui.actions_messages.set_sensitive(False)
            self.ui.actions_selection.set_sensitive(False)
            # Clear previously loaded messages when no memory is selected
            self.model_messages.clear()
            # Close the messages database
            if self.database:
                self.database.close()
                self.database = None

    def on_tvw_selection_messages_changed(self, widget):
        """Set action sensitiveness on selection change"""
        treeiter = get_treeview_selected_row(self.ui.tvw_messages)
        if not self.ui.action_selection.get_active():
            self.ui.action_messages_edit.set_sensitive(bool(treeiter))

    def on_window_delete_event(self, widget, event):
        """Close the application by closing the main window"""
        self.ui.action_quit.activate()
