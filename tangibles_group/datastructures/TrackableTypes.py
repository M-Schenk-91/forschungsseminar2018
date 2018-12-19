
from enum import Enum


class TrackableTypes(Enum):
    PHYSICAL_DOCUMENT = 1
    TANGIBLE = 2
    HAND = 3
    TOUCH = 4
    FILE = 5
    BUTTON = 6


class TangibleTypes(Enum):
    ACCEPT = 0
    REJECT = 1
    NOTED = 2


class FileType(Enum):
    TEXT = 1
    IMAGE = 2
