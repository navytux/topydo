# Topydo - A todo.txt client written in Python.
# Copyright (C) 2014 - 2015 Bram Schoenmakers <bram@topydo.org>
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

"""
This module provides the Todo class.
"""

from datetime import date, timedelta

from topydo.lib.Config import config
from topydo.lib.TodoBase import TodoBase
from topydo.lib.Utils import date_string_to_date


class Todo(TodoBase):
    """
    This class adds common functionality with respect to dates to the Todo
    base class, mainly by interpreting the start and due dates of task.
    """

    def __init__(self, p_str):
        TodoBase.__init__(self, p_str)
        self.attributes = {}

    def get_date(self, p_tag):
        """ Given a date tag, return a date object. """
        string = self.tag_value(p_tag)
        result = None

        try:
            result = date_string_to_date(string) if string else None
        except ValueError:
            pass

        return result

    def _due_date(self): # -> (due, flags)
        """ Returns date object for due date and set of due modifier flags. """
        flags = set()
        due   = self.tag_value(config().tag_due())
        if due is None:
            return (None, flags)
        if due.startswith('='):
            flags.add('on')
            due = due[1:]

        tdue = None
        try:
            tdue = date_string_to_date(due)
        except ValueError:
            flags = set()

        return (tdue, flags)


    def start_date(self):
        """ Returns a date object of the todo's start date. """
        tstart = self.get_date(config().tag_start())
        if tstart is not None:
            return tstart
        tdue, flags = self._due_date()
        if 'on' in flags:
            tstart = tdue - timedelta(days=1)
        return tstart

    def due_date(self):
        """ Returns a date object of the todo's due date. """
        tdue, _ = self._due_date()
        return tdue

    def is_active(self):
        """
        Returns True when the start date is today or in the past and the
        task has not yet been completed.
        """
        start = self.start_date()
        return not self.is_completed() and (not start or start <= date.today())

    def is_overdue(self):
        """
        Returns True when the due date is in the past and the task has not
        yet been completed.
        """
        return not self.is_completed() and self.days_till_due() < 0

    def days_till_due(self):
        """
        Returns the number of days till the due date. Returns a negative number
        of days when the due date is in the past.
        Returns 0 when the task has no due date.
        """
        due = self.due_date()
        if due:
            diff = due - date.today()
            return diff.days
        return 0

    def length(self):
        """
        Returns the length (in days) of the task, by considering the start date
        and the due date. When there is no start date, its creation date is
        used. Returns 0 when one of these dates is missing.
        """
        start = self.start_date() or self.creation_date()
        due = self.due_date()

        if start and due and start < due:
            diff = due - start
            return diff.days
        else:
            return 0
