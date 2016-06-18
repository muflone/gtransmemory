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

import sqlite3

from gtransmemory.models.abstract import ModelAbstract


class ModelMessages(ModelAbstract):
    COL_TRANSLATION = 1

    def __init__(self, model):
        """Create a new messages database"""
        super(self.__class__, self).__init__(model)
        self.db = None

    def open(file_path):
        self.db = sqlite3.connect(file_path)

    def save(self):
        self.db.commit()

    def close(self):
        self.save()
        self.db.close()

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.msgid not in self.rows:
            new_row = self.model.append(None, (item.msgid,
                                               item.translation))
            self.rows[item.msgid] = new_row
            return new_row

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        self.model.set_value(treeiter, self.COL_KEY, item.msgid)
        self.model.set_value(treeiter, self.COL_TRANSLATION, item.translation)

    def get_translation(self, treeiter):
        """Get the translation from a TreeIter"""
        return self.model[treeiter][self.COL_TRANSLATION]
