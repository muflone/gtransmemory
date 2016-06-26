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

from gtransmemory.models.abstract import ModelAbstract


class ModelMemories(ModelAbstract):
    COL_FILENAME = 1
    COL_DESCRIPTION = 2

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.key not in self.rows:
            new_row = self.model.append((
                item.key,
                item.filename,
                item.description))
            self.rows[item.key] = new_row
            return new_row

    def get_filename(self, treeiter):
        """Get the filename from a TreeIter"""
        return self.model[treeiter][self.COL_FILENAME]

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]
