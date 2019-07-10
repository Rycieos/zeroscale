from enum import Enum

class Status(Enum):
    stopped = 1
    starting = 2
    running = 3
    stopping = 4
