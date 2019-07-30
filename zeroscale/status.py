from enum import Enum


class Status(Enum):
    stopped = 1
    starting = 2
    running = 3
    stopping = 4

    # Hide unimportant value
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)
