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


class ModelSource(ModelAbstract):
    def __init__(self, model):
        """Create a new messages database"""
        super(self.__class__, self).__init__(model)

    def add_data(self, item):
        """Add a new row to the model if it doesn't exist"""
        super(self.__class__, self).add_data(item)
        if item.key not in self.rows:
            new_row = self.model.append((item.key, ))
            self.rows[item.key] = new_row
            return new_row
