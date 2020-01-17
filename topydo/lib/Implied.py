# Implied - implience for Topydo - A todo.txt client written in Python.
# Copyright (C) 2020 Kirill Smelkov <kirr@navytux.spb.ru>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Module Implied provides implied() function that returns associations for
provided items.

For example implied(['+pygolang']) -> ['+work', '+python', '+go']

The associations have to be set up in topydo configuration in [topydo.implied]
section e.g. as follows:

[implied]
# X implies -> A B C ...
+pygolang   = +work +python +go
@jp         = +work
@jerome     = +work +zodbtools
...
"""

from topydo.lib.Config import config


def implied(items): # -> implied_items
    db = _db()
    I     = set(items)  # resulting implied set we build; will remove source items in the end
    Inext = set(items)  # items to scan as roots in the next round

    while len(Inext) > 0:
        Icur  = Inext
        Inext = set()

        for item in Icur:
            for i in db.get(item, []):
                if i in I:
                    continue    # we already have this item

                # new item - add it to result set and schedule scan from it in
                # the next round
                I.add(i)
                Inext.add(i)

    # I now has complete closure of implience starting from items.
    # return only what is new.
    I = I.difference(items)
    L = list(I)
    L.sort()
    #print('implied %s -> %s' % (items, L))
    return L



# _db returns {} with implied words database:
# {} key -> [] of implied items
__db = None
def _db():
    global __db
    if __db is not None:
        return __db

    # load the database from config
    __db = config().implied()
    return __db
