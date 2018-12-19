
from enum import Enum
from smath import smath
from datastructures.TrackableTypes import TrackableTypes
from datastructures.Trackables import File

import math

from PyQt5 import QtCore, QtGui


class EffectType(Enum):
    MAGNIFICATION = 1
    DELETION = 2
    SEND_EMAIL = 3
    STORAGE = 4
    MOVE = 5
    CONVEYOR_BELT = 6
    DELEGATE = 7
    TAG = 8
    PALETTE = 9
    NUM_EFFECTS = 8


class EffectColor(Enum):
    MAGNIFICATION = QtGui.QColor("#33BB33")
    DELETION = QtGui.QColor("#BB3333")
    SEND_EMAIL = QtGui.QColor("#3333BB")
    STORAGE = QtGui.QColor("#BBBB33")
    DELEGATE = QtGui.QColor("#A142F4")
    TAG = QtGui.QColor("#A05A09")


class Effect:
    def __init__(self, _type):
        self.effect_type = _type


class Magnification(Effect):
    def __init__(self, interval=[], has_gradient=False):
        super().__init__(EffectType.MAGNIFICATION.value)
        self.interval = interval
        self.has_gradient = has_gradient
        self.gradient = []
        self.factor = sum(self.interval) / len(self.interval) / 100
        self.effect_text = '{0}%'.format(self.factor * 100)
        self.effect_color = EffectColor.MAGNIFICATION.value
        self.name = "Magnification"

    def __repr__(self):
        return '\nMagnification:\n' \
               '\tinterval: {0}\n' \
               '\thas gradient: {1}\n' \
               '\tgradient: {2}'.format(self.interval, self.has_gradient, self.gradient)

    def manipulate(self, target, source_shape):
        return self.__magnify(target)

    def __magnify(self, trackable):
        if not self.has_gradient:
            if trackable.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                trackable.parent.on_pd_magnification_requested.emit(trackable.id, self.factor)
            elif trackable.type_id == TrackableTypes.FILE.value:
                trackable.parent.on_file_magnification_requested.emit(trackable.id, self.factor)
        else:
            # more complicated case
                # use center of trackable for zoom? (e.g. document, file)
            pass

        return None


class Deletion(Effect):
    def __init__(self):
        super().__init__(EffectType.DELETION.value)

        self.effect_text = ''
        self.effect_color = EffectColor.DELETION.value
        self.name = "Deletion"

    def __repr__(self):
        return 'Deletion'

    def manipulate(self, target, source_shape):
        return self.__delete(target)

    def __delete(self, target):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.grabbed:
                target.parent.on_delete_solo_file.emit(target.center)
        elif target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            target.parent.on_delete_digital_twin.emit(target.id)

        return None


class SendMail(Effect):
    def __init__(self, receiver):
        super().__init__(EffectType.SEND_EMAIL.value)

        self.receiver = receiver

        self.effect_text = 'To ' + self.receiver
        self.effect_color = EffectColor.SEND_EMAIL.value
        self.source_shape = None
        self.name = "Send Mail"

    def __repr__(self):
        return 'Send via Email\n' \
               '\tReceiver: {0}'.format(self.receiver)

    def manipulate(self, target, source_shape):
        return self.__send_via_email(target, source_shape)

    def __send_via_email(self, target, source_shape):
        self.source_shape = source_shape

        if target.type_id == TrackableTypes.FILE.value or target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.emailed:
                target.emailed = True
                source_shape.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)

        return None


class Storage(Effect):
    def __init__(self):
        super().__init__(EffectType.STORAGE.value)
        self.effect_text = ''
        self.effect_color = EffectColor.STORAGE.value
        self.name = "Storage"

    def __repr__(self):
        return 'Storage'

    def manipulate(self, target, source_shape):
        return self.__store(target, source_shape)

    def __store(self, target, source_shape):
        if target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.stored:
                target.stored = True

                x, y = target.center[0], target.center[1]
                target.parent.on_new_file_append_requested.emit(x, y, 'CHI\'19.txt' if target.id == 1 else 'blank.png', target.id)
        elif target.type_id == TrackableTypes.FILE.value:
            if not target.stored:
                target.stored = True

                target.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)

        return None


class ConveyorBelt(Effect):
    def __init__(self, items=[], looped=False):
        super().__init__(EffectType.CONVEYOR_BELT.value)

        self.items = items
        self.looped = looped
        self.traveled_to_line = []
        self.target_points = []
        self.effect_text = ''
        self.effect_color = None
        self.name = "Conveyor Belt"

    def __repr__(self):
        return 'Conveyor_Belot\n' \
               '\tLooped: {0}\n' \
               '\tNumber of Items: {1}\n' \
               '\tItems:\n' \
               '\t\t{2}'.format(self.looped, len(self.items), self.items)

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.is_on_conveyor_belt:
                line = source_shape.middle_line

                min_distance = float(math.inf)
                idx = 0

                for i in range(len(line)):
                    d = smath.Math.vector_norm((target.center[0] - line[i][0], target.center[1] - line[i][1]))

                    if d < min_distance:
                        min_distance = d
                        idx = i

                units_per_second = 6000
                travel_length = sum([smath.Math.vector_norm([i[0], i[1]]) for i in line[idx:]])

                actual_animation_time = travel_length / units_per_second * 1000
                target.parent.on_conveyor_move_requested.emit(target.center[0], target.center[1], idx, line, actual_animation_time, self.looped)

        return None


class Delegate(Effect):
    def __init__(self, receiver):
        super().__init__(EffectType.DELEGATE.value)

        self.receiver = receiver
        self.effect_text = 'To ' + self.receiver
        self.effect_color = EffectColor.DELEGATE.value
        self.name = "Delegate"
        self.source_shape = None

    def __repr__(self):
        return 'Delegate\n' \
               '\tReceiver: {0}'.format(self.receiver)

    def manipulate(self, target, source_shape):
        self.source_shape = source_shape

        if target.type_id == TrackableTypes.FILE.value or target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.delegated:
                target.delegated = True
                source_shape.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)


class Tag(Effect):
    def __init__(self, tagging):
        super().__init__(EffectType.TAG.value)

        self.effect_color = EffectColor.TAG.value
        self.name = "Tag"
        self.tagging = tagging
        self.effect_text = "Tag with " + self.tagging

    def __repr__(self):
        return "Tag"

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.done_at_once:
                target.done_at_once = True
                source_shape.parent.on_do_at_once_requested.emit(source_shape.roi, target.id, self.tagging)


class Palette(Effect):
    def __init__(self):
        super().__init__(EffectType.PALETTE.value)

        self.name = 'Palette'
        self.effect_colors = [
            EffectColor.MAGNIFICATION.value,
            EffectColor.DELETION.value,
            EffectColor.SEND_EMAIL.value,
            EffectColor.STORAGE.value,
            EffectColor.DELEGATE.value,
            EffectColor.TAG.value
        ]

        self.effect_text = ""
        self.effect_color = None

    def __repr__(self):
        return 'Palette'

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.TOUCH.value:
            print("pallette clicked")
