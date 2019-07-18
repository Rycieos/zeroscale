from enum import Enum, auto


class Status(Enum):
    stopped = auto()
    starting = auto()
    running = auto()
    stopping = auto()

    # Hide unimportant value
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)
