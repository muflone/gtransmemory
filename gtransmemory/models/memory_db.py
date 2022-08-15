##
#     Project: gTransMemory
# Description: Memory of terms for translators
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

import os.path
import sqlite3

from gtransmemory.constants import DIR_MEMORIES


class MemoryDB(object):
    def __init__(self, file_path):
        self.db = sqlite3.connect(os.path.join(DIR_MEMORIES, file_path))
        tables = []
        for row in self.execute('SELECT name FROM sqlite_master '
                                'WHERE type="table" ORDER BY name')[1]:
            tables.append(row[0])
        if 'settings' not in tables:
            self.execute('CREATE TABLE settings(name varchar, value varchar)')
            tables.append('settings')
        if 'messages' not in tables:
            self.execute('CREATE TABLE messages('
                         'message varchar, '
                         'value varchar, '
                         'source varchar)')
            tables.append('messages')

    def close(self):
        """Close the database connection"""
        self.db.commit()
        self.db.close()

    def execute(self, statement, parameters=None):
        """Execute a statement and returns the data from a cursor"""
        cursor = self.db.cursor()
        if parameters is None:
            cursor.execute(statement)
        else:
            cursor.execute(statement, parameters)
        if cursor.description is not None:
            fields = [r[0] for r in cursor.description]
            data = cursor.fetchall()
        else:
            fields = None
            data = None
        cursor.close()
        return (fields, data)

    def get_description(self):
        """Return the memory description"""
        data = self.execute('SELECT value FROM settings WHERE name=?',
                            ('description', ))[1]
        if data:
            return str(data[0][0])

    def set_description(self, description):
        """Set the memory description"""
        self.execute('DELETE FROM settings WHERE name=?',
                     ('description', ))
        self.execute('INSERT INTO settings VALUES(?, ?)',
                     ('description', description))

    def get_messages(self):
        """Return the memory messages"""
        data = self.execute('SELECT message, value, source '
                            'FROM messages ORDER BY message')
        return data[1]

    def add_message(self, message):
        """Add a new message or update an existing"""
        self.remove_message(message)
        self.execute('INSERT INTO messages VALUES(?, ?, ?)',
                     (message.msgid, message.translation, message.source))

    def remove_message(self, message):
        """Remove an existing message"""
        self.execute('DELETE FROM messages WHERE message=? and source=?',
                     (message.msgid, message.source))
