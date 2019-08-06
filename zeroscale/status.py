"""Helper for mapping statuses of services"""
from enum import Enum


class Status(Enum):
    """Status options for server"""

    stopped = 1
    starting = 2
    running = 3
    stopping = 4

    # Hide unimportant value
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)
