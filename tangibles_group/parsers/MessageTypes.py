from enum import Enum


class MessageTypes(Enum):
    FRAME = "/tuio2/frm"
    ALIVE = "/tuio2/alv"
    TOKEN = "/tuio2/tok"
    POINTER = "/tuio2/ptr"
    BOUNDS = "/tuio2/bnd"
    SYMBOL = "/tuio2/sym"
