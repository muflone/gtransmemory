##
#     Project: gTransMemory
# Description: Learn memory for translators
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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

from gtransmemory.constants import APP_ID, DIR_SETTINGS
from gtransmemory.functions import get_ui_file
from gtransmemory.gtkbuilder_loader import GtkBuilderLoader

from gtransmemory.ui.main import UIMain


class Application(Gtk.Application):
    def __init__(self):
        """Create the application object"""
        super(self.__class__, self).__init__(application_id=APP_ID)
        self.connect('activate', self.activate)
        self.connect('startup', self.startup)

    def startup(self, application):
        """Configure the application during the startup"""
        self.ui = UIMain(self)
        # Add the about action to the app menu
        action = Gio.SimpleAction(name='settings_folder')
        action.connect('activate', self.on_app_settings_folder_activate)
        self.add_action(action)
        # Add the about action to the app menu
        action = Gio.SimpleAction(name='about')
        action.connect('activate', self.on_app_about_activate)
        self.add_action(action)
        # Add the shortcut action to the app menu
        # only for GTK+ 3.20.0 and higher
        if not Gtk.check_version(3, 20, 0):
            action = Gio.SimpleAction(name='shortcuts')
            action.connect('activate', self.on_app_shortcuts_activate)
            self.add_action(action)
        # Add the quit action to the app menu
        action = Gio.SimpleAction(name='quit')
        action.connect('activate', self.on_app_quit_activate)
        self.add_action(action)
        # Add the app menu
        builder_appmenu = GtkBuilderLoader(get_ui_file('appmenu.ui'))
        self.set_app_menu(builder_appmenu.app_menu)

    def activate(self, application):
        """Execute the application"""
        self.ui.run()

    def on_app_settings_folder_activate(self, action, data):
        """Open the settings folder from the app menu"""
        Gtk.show_uri(None, 'file://%s' % DIR_SETTINGS, Gdk.CURRENT_TIME)

    def on_app_about_activate(self, action, data):
        """Show the about dialog from the app menu"""
        self.ui.on_action_about_activate(action)

    def on_app_shortcuts_activate(self, action, data):
        """Show the shortcuts dialog from the app menu"""
        __pychecker__ = 'unusednames=data'
        self.ui.on_action_shortcuts_activate(action)

    def on_app_quit_activate(self, action, data):
        """Quit the application from the app menu"""
        self.ui.on_action_quit_activate(action)
