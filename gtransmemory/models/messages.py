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

import sqlite3

from gtransmemory.models.abstract import ModelAbstract


class ModelMessages(ModelAbstract):
    COL_MESSAGE = 1
    COL_TRANSLATION = 2
    COL_SOURCE = 3
    COL_SELECTION = 4

    def __init__(self, model):
        """Create a new messages database"""
        super(self.__class__, self).__init__(model)
        self.db = None

    def open(self, file_path):
        self.db = sqlite3.connect(file_path)

    def save(self):
        self.db.commit()

    def close(self):
        self.save()
        self.db.close()

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.key not in self.rows:
            new_row = self.model.append(None, (item.key,
                                               item.msgid,
                                               item.translation,
                                               item.source,
                                               False))
            self.rows[item.key] = new_row
            return new_row

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        self.model.set_value(treeiter, self.COL_MESSAGE, item.msgid)
        self.model.set_value(treeiter, self.COL_TRANSLATION, item.translation)
        self.model.set_value(treeiter, self.COL_SOURCE, item.source)

    def get_selection(self, treeiter):
        """Get the selection from a TreeIter"""
        return self.model[treeiter][self.COL_SELECTION]

    def set_selection(self, treeiter, value):
        """Set the selection for a TreeIter"""
        self.model.set_value(treeiter, self.COL_SELECTION, value)

    def get_message(self, treeiter):
        """Get the message from a TreeIter"""
        return self.model[treeiter][self.COL_MESSAGE]

    def get_translation(self, treeiter):
        """Get the translation from a TreeIter"""
        return self.model[treeiter][self.COL_TRANSLATION]

    def get_source(self, treeiter):
        """Get the source from a TreeIter"""
        return self.model[treeiter][self.COL_SOURCE]
