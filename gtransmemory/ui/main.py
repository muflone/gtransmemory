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

import polib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from gtransmemory.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, DIR_MEMORIES)
from gtransmemory.functions import (
    get_ui_file, get_treeview_selected_row, show_popup_menu, create_filefilter,
    process_events, text, _)
import gtransmemory.preferences as preferences
import gtransmemory.settings as settings
from gtransmemory.gtkbuilder_loader import GtkBuilderLoader

from gtransmemory.models.memory_db import MemoryDB
from gtransmemory.models.message_info import MessageInfo
from gtransmemory.models.messages import ModelMessages
from gtransmemory.models.memory_info import MemoryInfo
from gtransmemory.models.memories import ModelMemories

from gtransmemory.ui.about import UIAbout
from gtransmemory.ui.shortcuts import UIShortcuts
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
        self.selection_mode = False
        self.selected_count = 0
        self.loading_id = None
        self.loading_cancel = False
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
        # Add extra accelerators
        self.ui.accelerators.connect(accel_key=Gdk.keyval_from_name('Escape'),
                                     accel_mods=0,
                                     accel_flags=0,
                                     closure=self._end_selection)
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        self.ui.button_search_close.set_tooltip_text(
            self.ui.action_search_close.get_label().replace('_', ''))
        self.ui.entry_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY, text('Search'))
        self.ui.entry_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.SECONDARY, text('Clear'))
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
                self.ui.toolbar_main = None
            # Flatten the Gtk.ScrolledWindows
            self.ui.scroll_memories.set_shadow_type(Gtk.ShadowType.NONE)
            self.ui.scroll_messages.set_shadow_type(Gtk.ShadowType.NONE)
        else:
            # No headerbar
            self.ui.headerbar = None
        # Prepare the search bar
        self.ui.revealer_search = None
        # Add a Gtk.Revealer, only for GTK+ 3.10.0 and higher
        if not Gtk.check_version(3, 10, 0):
            self.ui.box_main.remove(self.ui.frame_search)
            self.ui.revealer_search = Gtk.Revealer()
            self.ui.revealer_search.add(self.ui.frame_search)
            self.ui.box_main.add(self.ui.revealer_search)
            self.ui.box_main.reorder_child(
                child=self.ui.revealer_search,
                position=1 if self.ui.toolbar_main else 0)
            self.ui.frame_search.set_visible(True)
        # Set custom search entry for messages
        self.ui.tvw_messages.set_search_entry(self.ui.entry_search)
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
            # Set a name to the new button
            name = 'button_%s' % action.get_name()
            new_button.set_name(name)
            setattr(self.ui, name, new_button)
            # Use icon from the action
            icon_name = action.get_icon_name()
            if (preferences.get(preferences.HEADERBARS_SYMBOLIC_ICONS) and
                    not icon_name.endswith('-symbolic')):
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
        self.ui.headerbar = header_bar
        header_bar.props.title = self.ui.win_main.get_title()
        header_bar.set_show_close_button(True)
        self.ui.win_main.set_titlebar(header_bar)
        # Add buttons to the left side
        for action in (self.ui.action_new,
                       self.ui.action_import,
                       self.ui.action_edit,
                       self.ui.action_remove):
            header_bar.pack_start(create_button_from_action(action))
        # Add buttons to the right side (in reverse order)
        for action in reversed((self.ui.action_memories,
                                self.ui.action_search,
                                self.ui.action_selection,
                                self.ui.action_about)):
            header_bar.pack_end(create_button_from_action(action))
        # Initially hide the remove messages button
        # (there's a bug in the GtkActions that show the button, regardless
        # the initial visibility
        self.ui.actions_selection_action.set_visible(False)
        self.ui.button_action_remove.set_no_show_all(True)

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

    def on_action_shortcuts_activate(self, action):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(self.ui.win_main)
        dialog.show()

    def on_action_quit_activate(self, action):
        """Close the application by closing the main window"""
        event = Gdk.Event()
        event.key.type = Gdk.EventType.DELETE
        self.ui.win_main.event(event)

    def reload_messages(self):
        """Load messages from the database memory"""
        def do_reload(messages):
            step = 1
            count = len(messages)
            # Load messages
            for msgid, translation, source in messages:
                # Break any previous loading
                if self.loading_cancel:
                    yield False
                message = MessageInfo(msgid.replace('\n', '\\n'),
                                      translation.replace('\n', '\\n'),
                                      source)
                self.add_message(message, False)
                step += 1
                self.ui.progress_loading.set_fraction(1.0 / count * step)
                self.ui.progress_loading.set_text(
                    _('Loading message {step} of {count}').format(step=step,
                                                                  count=count))
                yield True
            self.ui.progress_loading.set_visible(False)
            self.ui.action_new.set_sensitive(True)
            self.loading_id = None
            self.loading_cancel = False
            yield False
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
        self.ui.progress_loading.set_visible(True)
        memory_path = self.model_memories.get_filename(
            get_treeview_selected_row(self.ui.tvw_memories))
        self.database = MemoryDB(memory_path)
        self.loading_cancel = False
        # Start messages loading in idle
        task = do_reload(self.database.get_messages())
        self.loading_id = GObject.idle_add(task.__next__)

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

    def on_action_remove_activate(self, action):
        """Remove the selected items"""
        for key, row in self.model_messages.rows.items():
            if self.model_messages.get_selection(row):
                message = self.messages[key]
                self.remove_message(message=message, update_settings=True)
        self.ui.action_selection.set_active(False)

    def on_action_import_activate(self, action):
        """Import messages from a PO/POT file"""
        # Show the import file dialog
        dialog = UIMessagesImport(self.ui.win_main)
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('GNU gettext translation files'),
                              None,
                              ('*.po', '*.pot')))
        dialog.ui.file_chooser_import.add_filter(
            create_filefilter(_('All files'),
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
        if selected_row and not self.selection_mode:
            # Start message edit
            self.ui.action_edit.activate()

    def on_action_memories_activate(self, widget):
        """Edit memories"""
        self.ui.tvw_selection_memories.unselect_all()
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
        """Show popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            if self.selection_mode:
                # Show selection menu
                show_popup_menu(self.ui.menu_selection, event.button)
            else:
                # Show messages menu
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
        self.ui.actions_selection.set_sensitive(bool(selected_row))
        self.model_messages.clear()
        if selected_row:
            self.reload_messages()
            # Automatically select the first message for the memory
            self.ui.tvw_messages.set_cursor(0)
        else:
            self.ui.actions_message.set_sensitive(False)
            # Close the messages database
            if self.database:
                self.database.close()
                self.database = None

    def on_tvw_selection_messages_changed(self, widget):
        """Set action sensitiveness on selection change"""
        selected_row = get_treeview_selected_row(self.ui.tvw_messages)
        self.ui.actions_message.set_sensitive(bool(selected_row))

    def on_action_selection_toggled(self, action):
        """Enable or disable the selection mode and change style accordingly"""
        status = action.get_active()
        self.selection_mode = status
        # Remove any previous selection
        if not status:
            for row in self.model_messages.rows.values():
                self.model_messages.set_selection(row, False)
        self.selected_count = 0
        if self.ui.headerbar:
            # Change headerbar style
            style_context = self.ui.headerbar.get_style_context()
            if status:
                style_context.add_class('selection-mode')
            else:
                style_context.remove_class('selection-mode')
            self.ui.actions_messages.set_visible(not status)
            self.ui.actions_message.set_visible(not status)
            self.ui.actions_memories.set_visible(not status)
            self.ui.actions_selection_action.set_visible(status)
        else:
            # No headerbar, therefore simply enable and disable toolbuttons
            self.ui.actions_messages.set_sensitive(not status)
            self.ui.actions_message.set_sensitive(not status)
            self.ui.actions_selection_action.set_sensitive(status)
        self.ui.actions_selection_action.set_sensitive(False)
        self.ui.column_selection.set_visible(status)
        self.ui.tvw_memories.set_sensitive(not status)

    def _end_selection(self, accel_group, acceleratable, keyval, modifier):
        """End of the selection mode"""
        self.ui.action_selection.set_active(False)

    def on_action_select_all_activate(self, action):
        """Select or deselect all messages"""
        self.ui.action_selection.set_active(True)
        self.selected_count = 0
        status = action == self.ui.action_select_all
        # Iterate over all the Gtk.TreeIter
        for row in self.model_messages.rows.values():
            self.model_messages.set_selection(row, status)
            if status:
                self.selected_count += 1
        self.ui.actions_selection_action.set_sensitive(self.selected_count)

    def on_cell_selection_toggled(self, widget, treepath):
        """Toggle the selection status"""
        key = self.model_messages.get_key(treepath)
        treeiter = self.model_messages.get_iter(key)
        status = not self.model_messages.get_selection(treeiter)
        self.model_messages.set_selection(treeiter, status)
        # Set the selection action state
        self.selected_count += 1 if status else -1
        self.ui.actions_selection_action.set_sensitive(self.selected_count)

    def on_action_search_toggled(self, action):
        """Show and hide the search bar"""
        if self.ui.revealer_search:
            # There's a Gtk.Revealer, show and hide the child
            self.ui.revealer_search.set_reveal_child(
                not self.ui.revealer_search.get_reveal_child())
            if self.ui.revealer_search.get_reveal_child():
                self.ui.entry_search.grab_focus()
        else:
            # No Gtk.Revealer, simply show and hide the Gtk.Frame
            self.ui.frame_search.set_visible(
                not self.ui.frame_search.get_visible())
            if self.ui.frame_search.get_visible():
                self.ui.entry_search.grab_focus()

    def on_action_search_close_activate(self, action):
        """Hide the search bar"""
        self.ui.action_search.set_active(False)

    def on_entry_search_icon_release(self, widget, icon_position, event):
        """Clear the search text by clicking the icon next to the Gtk.Entry"""
        if icon_position == Gtk.EntryIconPosition.SECONDARY:
            self.ui.entry_search.set_text('')
