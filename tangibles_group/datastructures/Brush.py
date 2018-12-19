
from enum import Enum


class BrushTypes(Enum):
    NONE = 0
    MAGNIFY = 1
    DELETION = 2
    SEND_MAIL = 3
    STORAGE = 4
    CONVEYOR_BELT = 5
    MOVE = 6
    DELEGATE = 7
    TAG = 8
    PALETTE = 9


class Brush:
    def __init__(self, brush_type, effect):
        self.brush_tpye = brush_type
        self.effect = effect

    def set_brush_type(self, t):
        self.brush_tpye = t

    def get_brush_type(self):
        return self.brush_tpye

    def set_effect(self, e):
        self.effect = e

    def get_effect(self):
        return self.effect
