
from interaction.Effect import *
from PyQt5 import QtCore, QtWidgets, QtGui
from style import style
from widgets import QCustomListViewWidget


class Shape:
    def __init__(self, roi=[], effect=None, parent=None):
        """
        Picture Sources:
            * https://www.flaticon.com/free-icon/magnifying-glass_49116 : Icon made by Freepik from www.flaticon.com
            * https://www.flaticon.com/free-icon/rubbish-bin_63260#term=deletion&page=1&position=3 : Icon made by Icon Works from www.flaticon.com
            * https://www.flaticon.com/free-icon/contact_133667#term=mail%20icon&page=1&position=3 : Icon made by EpicCoders from www.flaticon.com
            * https://www.flaticon.com/free-icon/floppy-disk-interface-symbol-for-save-option-button_39613#term=save%20icon&page=1&position=10 : Icon made by Freepik from www.flaticon.com
            * https://www.flaticon.com/free-icon/factory_499190#term=conveyor%20line&page=1&position=8 : Icon made by Eucalyp from www.flaticon.com
        """

        self.roi = roi
        self.aabb = smath.Math.polygon_aabb(self.roi)
        self.effect = effect
        self.middle_line = []
        self.img = None
        self.img_path = None
        self.text = None
        self.parent = parent
        self.is_looped = False

        self.shape_part_one = []
        self.shape_part_two = []

        self.center = smath.Math.center_of_polygon(self.roi)
        self.list_view = None
        self.moveable = False
        self.attached = False
        self.dropped = False
        self.is_active = False

        self.moveable_highlighting = []

        self.direction_visualization_arrows = []
        self.touch_id = -1
        self.sub_area_points = []
        self.sub_area_rois = []
        self.palette_effect = None
        self.effect_color_index = -1
        self.palette_effect_selected = False
        self.is_palette_parent = False
        self.is_palette_extended = False
        self.palette_parent = -1
        self.palette_additional_info = None
        self.palette_children_indices = []

    def set_image(self):
        if self.effect is not None:
            self.center = smath.Math.center_of_polygon(self.roi)

        self.text = QtWidgets.QLabel()
        self.img = QtWidgets.QLabel()

        if self.effect is not None:
            text = self.effect.effect_text

            if self.palette_effect is None:
                if self.effect.effect_type == EffectType.MAGNIFICATION.value:
                    self.img_path = 'res/img/magnifying-glass.png'
                elif self.effect.effect_type == EffectType.DELETION.value:
                    self.img_path = 'res/img/rubbish-bin.png'
                elif self.effect.effect_type == EffectType.SEND_EMAIL.value:
                    self.img_path = 'res/img/contact.png'
                elif self.effect.effect_type == EffectType.STORAGE.value:
                    self.img_path = 'res/img/save.png'
                elif self.effect.effect_type == EffectType.CONVEYOR_BELT.value:
                    self.img_path = 'res/img/factory.png'
                elif self.effect.effect_type == EffectType.DELEGATE.value:
                    self.img_path = 'res/img/next.png'
                elif self.effect.effect_type == EffectType.TAG.value:
                    self.img_path = 'res/img/down-arrow.png'
                elif self.effect.effect_type == EffectType.PALETTE.value:
                    return
            else:
                if not self.is_palette_extended:
                    self.palette_effect = 8 if self.palette_effect == 5 else self.palette_effect

                    if self.palette_effect == EffectType.MAGNIFICATION.value:
                        self.img_path = 'res/img/magnifying-glass.png'
                        self.effect_color_index = 0
                    elif self.palette_effect == EffectType.DELETION.value:
                        self.img_path = 'res/img/rubbish-bin.png'
                        self.effect_color_index = 1
                    elif self.palette_effect == EffectType.SEND_EMAIL.value:
                        self.img_path = 'res/img/contact.png'
                        self.effect_color_index = 2
                    elif self.palette_effect == EffectType.STORAGE.value:
                        self.img_path = 'res/img/save.png'
                        self.effect_color_index = 3
                    elif self.palette_effect == EffectType.CONVEYOR_BELT.value:
                        self.img_path = 'res/img/factory.png'
                    elif self.palette_effect == EffectType.DELEGATE.value:
                        self.img_path = 'res/img/next.png'
                        self.effect_color_index = 4
                    elif self.palette_effect == EffectType.TAG.value:
                        self.img_path = 'res/img/down-arrow.png'
                        self.effect_color_index = 5
                    elif self.palette_effect == EffectType.PALETTE.value:
                        pass
                else:
                    text = str(self.palette_additional_info)

        self.img.setParent(self.parent)
        self.img.setObjectName("shape_img")
        self.img.setScaledContents(True)
        self.img.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.img.setGeometry(self.center[0], self.center[1], 20, 20)

        self.text.setStyleSheet(style.WidgetStyle.QLABEL_STYLE.value)

        if self.effect is not None:
            self.text.setText(text)

        font = self.text.font()
        font.setPointSize(18)
        self.text.setFont(font)
        self.text.adjustSize()
        self.text.setParent(self.parent)
        self.text.setObjectName("shape_text")
        self.text.setScaledContents(True)
        self.text.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.text.setGeometry(self.img.x() - self.text.width() / 2, self.img.y() - self.text.height() - 10, self.text.width(), self.text.height())

        self.text.show()

        self.list_view = QCustomListViewWidget.QCustomListViewWidget(self.center[0] - 100, self.center[1] - 50)

        if self.effect is not None:
            if self.img_path is not None:
                self.img.setPixmap(QtGui.QPixmap(self.img_path).scaledToWidth(45))

                if self.effect.effect_type != EffectType.CONVEYOR_BELT.value:
                    self.img.show()

    def __repr__(self):
        ret = '\nShape:\n\t'

        ret += 'roi: '
        for p in self.roi:
            ret += ('(' + str(p[0]) + ',' + str(p[1]) + '), ')

        ret = ret[:-2] + '\n\t'

        ret += ('effect: ' + str(self.effect))

    def set_roi(self, roi):
        self.roi = roi
        self.center = smath.Math.center_of_polygon(self.roi)
        self.aabb = smath.Math.polygon_aabb(self.roi)

        if self.effect.effect_type == EffectType.PALETTE.value:
            self.aabb = [
                self.aabb[0],
                (self.aabb[1][0], self.aabb[1][1] + (self.aabb[1][1] - self.aabb[0][1])),
                (self.aabb[2][0], self.aabb[2][1] + (self.aabb[2][1] - self.aabb[0][1])),
                self.aabb[3]
            ]
        else:
            self.aabb = smath.Math.polygon_aabb(self.roi)
        self.sub_area_rois = []

        if self.aabb is not None:
            arrows = smath.Math.movement_indication(self.aabb)
            self.moveable_highlighting = arrows
        else:
            self.moveable_highlighting = []

        if len(self.roi) > 0:
            temp = [self.roi[0]]

            for i, p in enumerate(self.roi[1:]):
                temp.append(p)

                if i > 0 and i % 12 == 0:
                    self.sub_area_rois.append([self.center] + temp + [self.center])
                    temp = [p]

            self.sub_area_rois.append([self.center] + temp + [self.center])

    def collides_with_via_aabb(self, other, what=""):
        return smath.Math.aabb_in_aabb(self.aabb, other)

    def set_effect(self, effect):
        self.effect = effect

        if self.img is not None:
            self.img.close()

        self.set_image()

    def set_palette_effect(self, index, *args):
        self.palette_effect = index

        # for potential future use
        if len(args) > 0:
            if args[0] == EffectType.MAGNIFICATION.value:
                self.palette_additional_info = args[1]
            if args[0] == EffectType.SEND_EMAIL.value:
                self.palette_additional_info = args[1]
            if args[0] == EffectType.DELEGATE.value:
                self.palette_additional_info = args[1]
            if args[0] == EffectType.TAG.value:
                self.palette_additional_info = args[1]

    def set_middle_line(self, l):
        self.middle_line = smath.Math.resample_points(l[:-3], 100)

        if self.effect.effect_type == EffectType.CONVEYOR_BELT.value:
            direction_visualization = []

            x = 10
            prev_i = 0

            for i in range(len(self.middle_line)):
                if i != 0 and i % x == 0:
                    direction_visualization.append(self.middle_line[prev_i:i][5:])
                    prev_i = i

            for line in direction_visualization:
                arrow = {}

                arrow['arrow_part1'], arrow['arrow_part2'] = smath.Math.get_arrow_tip(line[-2], line[-1], 25, 2)
                arrow['arrow_base'] = line

                self.direction_visualization_arrows.append(arrow)

    def affect_trackable(self, target):
        if self.effect is None:
            return target

        if self.effect.effect_type == EffectType.STORAGE.value or self.effect.effect_type == EffectType.SEND_EMAIL.value or self.effect.effect_type == EffectType.DELEGATE.value:
            self.list_view.set_parent(self.parent)

            if target.type_id == TrackableTypes.FILE.value:
                if (not target.stored and self.effect.effect_type == EffectType.STORAGE.value) or (not target.emailed and self.effect.effect_type == EffectType.SEND_EMAIL.value) or (not target.delegated and self.effect.effect_type == EffectType.DELEGATE.value):
                    path = 'res/img/file_icon.png'

                    self.list_view.update_model_all(path, target.name)
            elif target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                path = 'res/img/placeholder.png'

                if self.effect.effect_type == EffectType.SEND_EMAIL.value:
                    if not target.emailed:
                        self.list_view.update_model_all(path, target.name)

        return self.effect.manipulate(target, self)

    def update_progress(self, progress, row):
        if self.effect.effect_type == EffectType.STORAGE.value or self.effect.effect_type == EffectType.SEND_EMAIL.value or self.effect.effect_type == EffectType.DELEGATE.value:
            self.list_view.update_model_progress(progress, row)

    def remove_completed_item(self, row):
        if self.effect.effect_type == EffectType.STORAGE.value or self.effect.effect_type == EffectType.SEND_EMAIL.value or self.effect.effect_type == EffectType.DELEGATE.value:
            self.list_view.update_model_remove_item(row)

    def push_roi(self, x, y):
        for i in range(len(self.roi)):
            self.roi[i] = (self.roi[i][0] + x, self.roi[i][1] + y)

    def push_middle_line(self, x, y):
        for i in range(len(self.middle_line)):
            self.middle_line[i] = (self.middle_line[i][0] + x, self.middle_line[i][1] + y)

    def push_conveyorbelt_visualizations(self, x, y):
        if self.effect is not None:
            if self.effect.effect_type == EffectType.CONVEYOR_BELT.value:
                for arrow in self.direction_visualization_arrows:
                    for i in range(len(arrow['arrow_base'])):
                        arrow['arrow_base'][i] = (arrow['arrow_base'][i][0] + x, arrow['arrow_base'][i][1] + y)

                    arrow['arrow_part1'] = [(arrow['arrow_part1'][0][0] + x, arrow['arrow_part1'][0][1] + y), (arrow['arrow_part1'][1][0] + x, arrow['arrow_part1'][1][1] + y)]
                    arrow['arrow_part2'] = [(arrow['arrow_part2'][0][0] + x, arrow['arrow_part2'][0][1] + y), (arrow['arrow_part2'][1][0] + x, arrow['arrow_part2'][1][1] + y)]

    def push_moveable_highlighting_visualizations(self, x, y):
        for arrow in self.moveable_highlighting:
            arrow['upper'] = [(arrow['upper'][0][0] + x, arrow['upper'][0][1] + y), (arrow['upper'][1][0] + x, arrow['upper'][1][1] + y)]
            arrow['lower'] = [(arrow['lower'][0][0] + x, arrow['lower'][0][1] + y), (arrow['lower'][1][0] + x, arrow['lower'][1][1] + y)]
            arrow['angle_one'] = [(arrow['angle_one'][0][0] + x, arrow['angle_one'][0][1] + y), (arrow['angle_one'][1][0] + x, arrow['angle_one'][1][1] + y)]
            arrow['angle_two'] = [(arrow['angle_two'][0][0] + x, arrow['angle_two'][0][1] + y), (arrow['angle_two'][1][0] + x, arrow['angle_two'][1][1] + y)]

        for i, p in enumerate(self.aabb):
            p = (p[0] + x, p[1] + y)
            self.aabb[i] = p

    def push_palette_children(self, x, y):
        for i, s in enumerate(self.palette_children_indices):
            self.parent.drawn_shapes[self.palette_children_indices[i]].push(x, y)

    def push(self, x, y):
        self.img.setGeometry(self.img.x() + x, self.img.y() + y, self.img.width(), self.img.height())
        self.text.setGeometry(self.text.x() + x, self.text.y() + y, self.text.width(), self.text.height())

        self.push_roi(x, y)

        self.center = smath.Math.center_of_polygon(self.roi)

        self.push_middle_line(x, y)
        self.push_conveyorbelt_visualizations(x, y)
        self.push_moveable_highlighting_visualizations(x, y)

        if self.is_palette_parent:
            self.push_palette_children(x, y)
