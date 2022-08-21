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

from gtransmemory.models.abstract import ModelAbstract


class ModelMemories(ModelAbstract):
    COL_FILENAME = 1
    COL_DESCRIPTION = 2
    COL_LANGUAGES = 3

    def add_data(self, item):
        """Add a new row to the model if it doesn't exist"""
        super(self.__class__, self).add_data(item)
        if item.key not in self.rows:
            new_row = self.model.append((
                item.key,
                item.filename,
                item.description,
                item.languages))
            self.rows[item.key] = new_row
            return new_row

    def get_filename(self, treeiter):
        """Get the filename from a TreeIter"""
        return self.model[treeiter][self.COL_FILENAME]

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]

    def get_languages(self, treeiter):
        """Get the languages from a TreeIter"""
        return self.model[treeiter][self.COL_LANGUAGES]
