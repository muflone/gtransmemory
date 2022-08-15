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

import gettext
import locale

import gtransmemory.requires

from gtransmemory.functions import store_message, text, _
from gtransmemory.constants import DOMAIN_NAME, DIR_LOCALE

# Load domain for translation
for module in (gettext, locale):
    module.bindtextdomain(DOMAIN_NAME, DIR_LOCALE)
    module.textdomain(DOMAIN_NAME)

# Set default empty translation for empty string
store_message('', '')
# Import some translated messages from GTK+ domain
store_message('_Icon:', '_%s:' % text(message='Icon', gtk30=True))
for message in ('_OK', '_Cancel', '_Close', 'Se_lection', 'Search'):
    text(message=message, gtk30=True)
# With domain context
for message in ('_Add', '_Remove', '_Edit', '_New', '_About', '_Clear',
                'Select _All'):
    text(message=message, gtk30=True, context='Stock label')
# Remove the underscore
for message in ('_Add', '_Clear'):
    store_message(message.replace('_', ''), _(message).replace('_', ''))
# Import fixed texts
store_message('Project home page', _('Project home page'))
store_message('Source code', _('Source code'))
store_message('Author information', _('Author information'))
store_message('Issues and bugs tracking', _('Issues and bugs tracking'))
store_message('Translations', _('Translations'))
