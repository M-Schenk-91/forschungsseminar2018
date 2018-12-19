
from smath import smath
from widgets import QFileIconWidget
from datastructures.TrackableTypes import TrackableTypes, FileType
from style import style
from datastructures.Mask import Mask


from PyQt5 import QtCore, QtWidgets, QtGui
import math


class Trackable(object):
    def __init__(self, session_id, type_id, user_id, name, position, roi, width, height, angle):
        self.session_id = session_id
        self.type_id = type_id
        self.user_id = user_id
        self.name = name
        self.position = position
        self.roi = roi
        self.collision_roi = roi
        self.width = width
        self.height = height
        self.angle = angle
        self.parent = None
        self.colliding_with_shape = False

        self.center = self.__compute_center(self.roi)
        self.collision_center = self.__compute_center(self.collision_roi)

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_name(self, name):
        self.name = name

    def set_position(self, position):
        self.position = position

    def set_roi(self, roi):
        self.roi = roi
        self.center = self.__compute_center(self.roi)

    def set_collision_roi(self, roi):
        self.collision_roi = roi
        self.collision_center = self.__compute_center(self.collision_roi)

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_angle(self, angle):
        self.angle = angle

    def __compute_center(self, roi):
        return smath.Math.center_of_polygon(roi)

    def set_parent_widget(self, widget):
        self.parent = widget


class Document(Trackable):
    def __init__(self, _id, session_id, type_id, user_id, name, position, roi, width, height, angle):
        super().__init__(session_id, type_id, user_id, name, position, roi, width, height, angle)

        self.id = _id
        self.emailed = False
        self.stored = False
        self.delegated = False

    def __repr__(self):
        return 'Document:\n' \
               '\tid: {0}\n' \
               '\tsession_id: {1}\n' \
               '\ttype_id: {2}\n' \
               '\tuser_id: {3}\n' \
               '\tname: {4}\n' \
               '\tposition: {5}\n' \
               '\tcenter: {6}\n' \
               '\troi: {7}\n' \
               '\twidth: {8}\n' \
               '\theight: {9}\n' \
               '\tangle: {10}\n' \
               '\tprocessed: {11}' \
               ''.format(self.id, self.session_id, self.type_id, self.user_id,
                           self.name, self.position, self.center, self.roi, self.width,
                           self.height, self.angle, self.processed)

    def set_id(self, _id):
        self.id = _id

    def update_roi(self, magnification_factor):
        new_roi = []

        for _tuple in self.roi:
            new_roi.append(
                smath.Math.stretch_polygon_by_percent(self.center, _tuple,
                                                      magnification_factor))

        self.set_roi(new_roi)


class Tangible(Trackable):
    def __init__(self, _type, session_id, type_id, user_id, name, center, roi, width, height, angle):
        super().__init__(session_id, type_id, user_id, name, center, roi, width, height, angle)

        self.id = 0
        self.type = _type
        self.aabb = smath.Math.polygon_aabb(self.roi + [self.roi[0]])
        circle_roi = smath.Math.compute_circle(self.center[0], self.center[1], int(math.fabs(self.aabb[3][0] - self.aabb[0][0]) / 2 + 50))

        self.set_roi(smath.Math.resample_points(circle_roi, 24))
        self.mask = Mask(self.roi, self.id)
        self.effect = None
        self.shape_index = None

    def __repr__(self):
        return 'Tangible:\n' \
               '\ttype: {0}\n' \
               '\tsession_id: {1}\n' \
               '\ttype_id: {2}\n' \
               '\tuser_id: {3}\n' \
               '\tname: {4}\n' \
               '\tposition: {5}\n' \
               '\tcenter: {6}\n' \
               '\troi: {7}\n' \
               '\twidth: {8}\n' \
               '\theight: {9}\n' \
               '\tangle: {10}' \
               ''.format(self.type, self.session_id, self.type_id, self.user_id,
                           self.name, self.position, self.center, self.roi, self.width,
                           self.height, self.angle)

    def set_type(self, _type):
        self.type = _type

    def set_effect(self, effect):
        self.effect = effect

    def set_shape_index(self, shape_index):
        self.shape_index = shape_index

    def set_mask(self):
        self.mask = Mask(self.roi, self.id)


class Hand(Trackable):
    def __init__(self, _id, hand_center, finger_tips, session_id, type_id, user_id, name, center, roi, width, height, angle):
        super().__init__(session_id, type_id, user_id, name, center, roi, width, height, angle)

        self.id = _id
        self.hand_center = hand_center
        self.finger_tips = finger_tips
        self.has_context_menu = False

    def __repr__(self):
        return 'Hand:\n' \
               '\tID: {0}\n' \
               '\thand_center: {1}\n' \
               '\tfinger_tips: {2}\n' \
               '\tsession_id: {3}\n' \
               '\ttype_id: {4}\n' \
               '\tuser_id: {5}\n' \
               '\tname: {6}\n' \
               '\tposition: {7}\n' \
               '\tcenter: {8}\n' \
               '\troi: {9}\n' \
               '\twidth: {10}\n' \
               '\theight: {11}\n' \
               '\tangle: {12}' \
               ''.format(self.id, self.hand_center, self.finger_tips, self.session_id,
                           self.type_id, self.user_id, self.name, self.position,
                           self.center, self.roi, self.width, self.height, self.angle)

    def set_hand_center(self, hand_center):
        self.hand_center = hand_center

    def set_finger_tips(self, finger_tips):
        self.finger_tips = finger_tips


class Touch(Trackable):
    def __init__(self, _id, finger_tip_position, area, session_id, type_id, user_id, name, center, roi, width, height, angle):
        super().__init__(session_id, type_id, user_id, name, center, roi, width, height, angle)

        self.id = _id
        self.finger_tip_position = finger_tip_position
        self.area = area
        self.touched_object = None

        self.successive_detection_increments = 0

    def __repr__(self):
        return 'Touch:\n' \
               '\tid: {0}\n' \
               '\tfinger_tip_position: {1}\n' \
               '\tarea: {2}\n' \
               '\tsession_id: {3}\n' \
               '\ttype_id: {4}\n' \
               '\tuser_id: {5}\n' \
               '\tname: {6}\n' \
               '\tposition: {7}\n' \
               '\tcenter: {8}\n' \
               '\troi: {9}\n' \
               '\twidth: {10}\n' \
               '\theight: {11}\n' \
               '\tangle: {12}\n' \
               '\tsuccessive_detection_increments: {13}\n' \
               '\t is_holding {14}\n'.format(self.id, self.finger_tip_position, self.area, self.session_id,
                           self.type_id, self.user_id, self.name, self.position,
                           self.center, self.roi, self.width, self.height, self.angle, self.successive_detection_increments, self.is_holding())

    def set_finger_tip_position(self, finger_tip_position):
        self.finger_tip_position = finger_tip_position

    def set_area(self, area):
        self.area = area

    def set_touched_object(self, value):
        self.touched_object = value

    def is_holding(self):
        return self.successive_detection_increments >= 10

    def get_touched_object(self):
        return self.touched_object


class File(Trackable):
    def __init__(self, _id, x, y, parent, name, content, type_, is_digital_twin=False, physical_representation_id=-1, debug=False):
        self.id = _id
        self.delegated = False
        self.done_at_once = False
        self.emailed = False
        self.stored = False
        self.magnified = False
        self.shows_preview = False
        self.grabbed = True
        self.conveyable = True
        self.touched = True
        self.mouse_used = False
        self.previously_touched = True
        self.is_transfer_magnified = False
        self.touch_id = -1
        self.anim_id = -1
        self.name = name
        self.parent = parent
        self.content = content
        self.type = type_
        self.last_absolut_touch_position = (0, 0)
        self.physical_representation_id = -1

        self.set_digital_twin(physical_representation_id)

        if type_ == FileType.IMAGE.value:
            self.widget = QFileIconWidget.QFileIconWidget(45 if debug else 65, 61 if debug else 92, parent, type_, path=content, name=name, file=self)
        else:
            self.widget = QFileIconWidget.QFileIconWidget(45 if debug else 65, 61 if debug else 92, parent, type_, name=name, file=self)

        self.widget.setGeometry(x, y, self.widget.default_width, self.widget.default_height)
        self.widget.name_widget.setGeometry(x - 15, y + self.widget.default_height + 5, self.widget.default_width + 30, 20)

        self.widget.preview.setGeometry(x + self.widget.default_width / 2, y + self.widget.default_height / 2, 10, 10)

        self.original_width = self.widget.name_widget.width()
        self.original_height = self.widget.height() + self.widget.name_widget.height()

        self.first_move = True
        self.is_on_conveyor_belt = False


        tlc, blc, brc, trc = (self.widget.name_widget.x(), self.widget.y()), \
                             (self.widget.name_widget.x(), self.widget.name_widget.y() + self.widget.name_widget.height()), \
                             (self.widget.name_widget.x() + self.widget.name_widget.width(), self.widget.name_widget.y() + self.widget.name_widget.height()), \
                             (self.widget.name_widget.x() + self.widget.name_widget.width(), self.widget.y())

        super().__init__(-1, TrackableTypes.FILE.value, -1, "FILE",
                         (self.widget.x(), self.widget.y()), [tlc, blc, brc, trc],
                         self.widget.width(), self.widget.height(), 0.0)

        self.aabb = smath.Math.polygon_aabb(self.roi)

        self.widget.on_mouse_move.connect(self.on_mouse_move)
        self.on_mouse_move()

    def __repr__(self):
        return '\nFile:\n' \
               '\tsession_id: {0}\n' \
               '\ttype_id: {1}\n' \
               '\tuser_id: {2}\n' \
               '\tname: {3}\n' \
               '\tposition: {4}\n' \
               '\tcenter: {5}\n' \
               '\troi: {6}\n' \
               '\twidth: {7}\n' \
               '\theight: {8}\n' \
               '\tangle: {9}\n' \
               .format(self.session_id, self.type_id, self.user_id, self.name,
                       self.position, self.center, self.roi, self.width,
                       self.height, self.angle)

    def set_digital_twin(self, _id):
        if _id < 0:
            self.is_digital_twin = False
        else:
            self.is_digital_twin = True

        self.physical_representation_id = _id

    def set_animation_id(self, _id):
        self.anim_id = _id

    def on_mouse_move(self):
        self.set_position((self.widget.x(), self.widget.y))

        self.widget.name_widget.setGeometry(self.widget.x() - 15,
                                            self.widget.y() + self.widget.height() + 5,
                                            self.widget.width() + 30, 20)

        if self.magnified:
            tlc, blc, brc, trc = (self.widget.preview.x(),
                                  self.widget.preview.y()), \
                                 (self.widget.preview.x(),
                                  self.widget.preview.y() + self.widget.preview_default_height), \
                                 (
                                 self.widget.preview.x() + self.widget.preview_default_width,
                                 self.widget.preview.y() + self.widget.preview_default_height), \
                                 (
                                 self.widget.preview.x() + self.widget.preview_default_width,
                                 self.widget.preview.y())

            self.set_roi([tlc, blc, brc, trc])

            self.widget.preview.setGeometry(
                self.widget.x() + self.widget.width() / 2 - self.widget.preview_default_width / 2,
                self.widget.y() + self.widget.height() / 2 - self.widget.preview_default_height / 2,
                self.widget.preview_default_width,
                self.widget.preview_default_height)

            tlc, blc, brc, trc = (self.widget.name_widget.x(), self.widget.y()), \
                                 (self.widget.name_widget.x(),
                                  self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                 (
                                 self.widget.name_widget.x() + self.widget.name_widget.width(),
                                 self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                 (
                                 self.widget.name_widget.x() + self.widget.name_widget.width(),
                                 self.widget.y())

            self.set_collision_roi([tlc, blc, brc, trc])

        else:
            if self.first_move:
                self.original_width = self.widget.name_widget.width()
                self.original_height = self.widget.height() + self.widget.name_widget.height()

            self.first_move = False

            tlc, blc, brc, trc = (self.widget.name_widget.x(), self.widget.y()), \
                                 (self.widget.name_widget.x(), self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                 (self.widget.name_widget.x() + self.widget.name_widget.width(), self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                 (self.widget.name_widget.x() + self.widget.name_widget.width(), self.widget.y())

            self.set_roi([tlc, blc, brc, trc])
            self.set_collision_roi([tlc, blc, brc, trc])

            self.widget.preview.setGeometry(self.widget.x() + self.widget.width() / 2 - self.widget.preview_default_width / 2, self.widget.y() + self.widget.height() / 2 - self.widget.preview_default_height / 2, self.widget.preview_default_width, self.widget.preview_default_height)

    def click(self, touch_id):
        self.touch_id = touch_id
        self.parent.on_file_click.emit(self.id, touch_id)
        self.grabbed = True
        self.conveyable = False
        self.previously_touched = True

    def drag(self, vector, touch_id):
        if not self.grabbed:
            self.parent.on_file_drag.emit(self.id)

        self.grabbed = True
        self.conveyable = False
        self.previously_touched = True

        self.touch_id = touch_id

        x = y = 0

        for t1 in self.parent.concurrent_touches:
            for t2 in self.parent.previous_concurrent_touches_1:
                if touch_id == t1.id == t2.id:
                    x, y = t1.center[0] - t2.center[0], t1.center[1] - t2.center[1]
                    self.last_absolut_touch_position = t1.center
                    break

        self.widget.setGeometry(self.widget.x() + x, self.widget.y() + y, self.widget.default_width, self.widget.default_height)

        self.on_mouse_move()

    def clear(self):
        self.widget.name_widget.close()
        self.widget.preview.close()
        self.widget.close()

    def show_preview(self):
        if not self.shows_preview:
            self.magnified = True
            self.shows_preview = True

            self.widget.preview.show()
            self.widget.name_widget.hide()
            self.widget.hide()

            tlc, blc, brc, trc = (self.widget.preview.x(), self.widget.preview.y()), \
                                 (self.widget.preview.x(), self.widget.preview.y() + self.widget.preview_default_height), \
                                 (self.widget.preview.x() + self.widget.preview_default_width, self.widget.preview.y() + self.widget.preview_default_height), \
                                 (self.widget.preview.x() + self.widget.preview_default_width, self.widget.preview.y())

            self.set_roi([tlc, blc, brc, trc])

            self.parent.on_magnification_toggled.emit(True, self.id)

    def show_icon(self):
        if self.shows_preview:
            self.magnified = False
            self.shows_preview = False

            self.widget.preview.hide()
            self.widget.name_widget.show()
            self.widget.show()

            if not self.grabbed:
                tlc, blc, brc, trc = (self.widget.name_widget.x(), self.widget.y()), \
                                     (self.widget.name_widget.x(),
                                      self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                     (
                                     self.widget.name_widget.x() + self.widget.name_widget.width(),
                                     self.widget.name_widget.y() + self.widget.name_widget.height()), \
                                     (
                                     self.widget.name_widget.x() + self.widget.name_widget.width(),
                                     self.widget.y())

                self.set_roi([tlc, blc, brc, trc])
            else:
                tlc, blc, brc, trc = (self.last_absolut_touch_position[0] - self.widget.name_widget.width() / 2, self.last_absolut_touch_position[1] - self.widget.name_widget.height() / 2), \
                                     (self.last_absolut_touch_position[0] - self.widget.name_widget.width() / 2, self.last_absolut_touch_position[1] - self.widget.name_widget.height() / 2 + self.widget.name_widget.height()), \
                                     (self.last_absolut_touch_position[0] - self.widget.name_widget.width() / 2 + self.widget.name_widget.width(), self.last_absolut_touch_position[1] - self.widget.name_widget.height() / 2 + self.widget.name_widget.height()), \
                                     (self.last_absolut_touch_position[0] - self.widget.name_widget.width() / 2 + self.widget.name_widget.width(), self.last_absolut_touch_position[1] - self.widget.name_widget.height() / 2)

                self.set_roi([tlc, blc, brc, trc])

                self.widget.setGeometry(self.last_absolut_touch_position[0] - self.widget.width() / 2, self.last_absolut_touch_position[1] - self.widget.height() / 2, self.widget.default_width, self.widget.default_height)

            self.parent.on_magnification_toggled.emit(False, self.id)


class Button(Trackable):
    def __init__(self, _id, x, y, name, parent):
        self.widget = QtWidgets.QPushButton(parent)
        self.widget.setGeometry(x, y, 50, 50)

        self.widget.setStyleSheet(style.WidgetStyle.QPUSHBUTTON_STYLE.value)
        self.widget.setIcon(QtGui.QIcon("res/img/brush.png"))
        self.widget.setIconSize(QtCore.QSize(45, 45))

        self.id = _id
        self.name = name
        self.parent = parent

        self.x = x
        self.y = y
        self.width = self.widget.width()
        self.height = self.widget.height()

        self.touched = False

        tlc = self.widget.x(), self.widget.y()
        blc = self.widget.x(), self.widget.y() + self.widget.height()
        brc = self.widget.x() + self.widget.width(), self.widget.y() + self.widget.height()
        trc = self.widget.x() + self.widget.width(), self.widget.y()

        self.roi = [tlc, blc, brc, trc]

        super(Button, self).__init__(-1, TrackableTypes.BUTTON.value, -1, name, (x, y), self.roi, self.width, self.height, 0.0)

        self.widget.show()

        self.widget.clicked.connect(self.on_click)

    def click(self, touch_id):
        self.widget.click()

    def on_click(self):
        self.parent.on_button_clicked.emit(self.id)
