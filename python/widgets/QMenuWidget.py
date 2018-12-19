
from PyQt5 import QtWidgets, QtGui, QtCore

from style import style

from interaction import Effect
from datastructures import Brush


class QMenuWidget(QtWidgets.QMenu):
    def __init__(self, x, y, width, height, caller_id, parent=None, shape=None):
        super().__init__("Interaction", parent)

        self.x = x
        self.y = y
        self.width = 200
        self.height = 200
        self.caller_id = caller_id
        self.setParent(parent)

        self.shape = shape

        if self.shape is not None:
            self.setGeometry(self.shape.center[0] - self.width / 2, self.shape.center[1] - self.height / 2, self.width, self.height)
        else:
            self.setGeometry(x - self.width / 2, y - self.height / 2, self.width, self.height)

        font = self.font()
        font.setPointSize(18)

        self.setFont(font)
        self.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu = None
        self.setCursor(QtCore.Qt.BlankCursor)

    def x(self):
        return self.x

    def y(self):
        return self.y

    def add_top_level_menu(self):
        if self.shape is None:
            self.addAction("&Magnify", self.add_magnification)
            self.addAction("&Delete", self.add_deletion)
            self.addAction("&Send via Email", self.add_email_sending)
            self.addAction("&Storage", self.add_saving)
            self.addAction("&Delegate", self.add_delegate)
            self.addAction("&Do at once", self.add_do_at_once)
            self.addAction("&Conveyor Belt", self.add_conveyer_belt)
        else:
            if self.shape.effect is not None:
                if self.shape.effect.effect_type != Effect.EffectType.CONVEYOR_BELT.value:
                    self.addAction("&Magnify", self.reassign_magnification)
                    self.addAction("&Delete", self.reassign_deletion)
                    self.addAction("&Send via Email", self.reassign_email_sending)
                    self.addAction("&Storage", self.reassign_saving)
                    self.addAction("&Delegate", self.reassign_delegate)
                    self.addAction("&Do at once", self.reassign_do_at_once)

                    if self.shape.effect.effect_type == Effect.EffectType.DELETION.value:
                        self.addAction("&Delete Region", self.delete_region)

            else:
                self.addAction("&Magnify", self.reassign_magnification)
                self.addAction("&Delete", self.reassign_deletion)
                self.addAction("&Send via Email", self.reassign_email_sending)
                self.addAction("&Storage", self.reassign_saving)
                self.addAction("&Delegate", self.reassign_delegate)
                self.addAction("&Do at once", self.reassign_do_at_once)

            if not self.shape.moveable:
                self.addAction("&Move", lambda: self.movement(True))
            else:
                self.addAction("&Stop Move", lambda: self.movement(False))

            if not self.shape.attached:
                self.addAction("&Attach", lambda: self.attachment(True))
            else:
                self.addAction("&Detach", lambda: self.attachment(False))

        self.addAction("&Close Menu", self.close_menu)

    def add_magnification(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu.addAction("&15%", lambda: self.apply_magnification_effect(15))
        self.sub_menu.addAction("&25%", lambda: self.apply_magnification_effect(25))
        self.sub_menu.addAction("&50%", lambda: self.apply_magnification_effect(50))
        self.sub_menu.addAction("&75%", lambda: self.apply_magnification_effect(75))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()

    def apply_magnification_effect(self, magnification_factor):
        self.parent().current_brush.set_effect(Effect.Magnification([magnification_factor], False))
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.MAGNIFY.value)
        self.parent().brush_name = "Magnify by {}%".format(magnification_factor)

        self.close_menu()

    def add_deletion(self):
        self.parent().current_brush.set_effect(Effect.Deletion())
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.DELETION.value)

        self.parent().brush_name = "Deletion"

        self.close_menu()

    def add_email_sending(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu.addAction("&Raphael", lambda: self.apply_send_email_effect("Raphael"))
        self.sub_menu.addAction("&Florian", lambda: self.apply_send_email_effect("Florian"))
        self.sub_menu.addAction("&Preetha", lambda: self.apply_send_email_effect("Preetha"))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()

    def apply_send_email_effect(self, receiver):
        self.parent().current_brush.set_effect(Effect.SendMail(receiver))
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.SEND_MAIL.value)
        self.parent().brush_name = "Send Email To {0}".format(receiver)

        self.close_menu()

    def add_saving(self):
        self.parent().current_brush.set_effect(Effect.Storage())
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.STORAGE.value)
        self.parent().brush_name = "Storage"

        self.close_menu()

    def add_conveyer_belt(self):
        self.parent().current_brush.set_effect(Effect.ConveyorBelt())
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.CONVEYOR_BELT.value)

        self.parent().brush_name = "Conveyor Belt"

        self.close_menu()

    def add_delegate(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)
        self.sub_menu.addAction("&Andreas", lambda: self.apply_delegate_effect("Andreas"))
        self.sub_menu.addAction("&Lucia", lambda: self.apply_delegate_effect("Lucia"))
        self.sub_menu.addAction("&Laurin", lambda: self.apply_delegate_effect("Laurin"))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()

    def apply_delegate_effect(self, receiver):
        self.parent().current_brush.set_effect(Effect.Delegate(receiver))
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.DELEGATE.value)
        self.parent().brush_name = "Delegate To {0}".format(receiver)

        self.close_menu()

    def add_do_at_once(self):
        self.parent().current_brush.set_effect(Effect.Tag())
        self.parent().current_brush.set_brush_type(Brush.BrushTypes.TAG.value)
        self.parent().brush_name = "Do at once"

        self.close_menu()

    def reassign_magnification(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu.addAction("&15%", lambda: self.reassign_magnification_effect(15))
        self.sub_menu.addAction("&25%", lambda: self.reassign_magnification_effect(25))
        self.sub_menu.addAction("&50%", lambda: self.reassign_magnification_effect(50))
        self.sub_menu.addAction("&75%", lambda: self.reassign_magnification_effect(75))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()
        self.close()

    def reassign_magnification_effect(self, magnification_factor):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.Magnification([magnification_factor], False))

        self.close_menu()

    def reassign_deletion(self):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.Deletion())

        self.close_menu()

    def reassign_email_sending(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu.addAction("&Raphael", lambda: self.reassign_send_email_effect("Raphael"))
        self.sub_menu.addAction("&Florian", lambda: self.reassign_send_email_effect("Florian"))
        self.sub_menu.addAction("&Preetha", lambda: self.reassign_send_email_effect("Preetha"))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()
        self.close()

    def reassign_send_email_effect(self, receiver):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.SendMail(receiver))

        self.close_menu()

    def reassign_saving(self):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.Storage())

        self.close_menu()

    def reassign_delegate(self):
        self.sub_menu = QMenuWidget(self.x, self.y, self.width, self.height, self.caller_id, self.parent())
        self.sub_menu.setCursor(QtCore.Qt.BlankCursor)

        font = self.font()
        font.setPointSize(18)

        self.sub_menu.setFont(font)
        self.sub_menu.setStyleSheet(style.WidgetStyle.QMENU_ITEM_STYLE.value)

        self.sub_menu.addAction("&Andreas", lambda: self.reassign_delegate_effect("Andreas"))
        self.sub_menu.addAction("&Lucia", lambda: self.reassign_delegate_effect("Lucia"))
        self.sub_menu.addAction("&Laurin", lambda: self.reassign_delegate_effect("Laurin"))
        self.sub_menu.addAction("&Close Menu", self.close_menu)

        self.sub_menu.show()
        self.close()

    def reassign_delegate_effect(self, receiver):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.Delegate(receiver))

        self.close_menu()

    def reassign_do_at_once(self):
        self.shape.img.close()
        self.shape.text.setText("")
        self.shape.text.close()
        self.shape.set_effect(Effect.Tag("tagging"))

        self.close_menu()

    def movement(self, toggle, is_attached=False):
        if self.shape is not None:

            i = 0

            for i in range(len(self.parent().drawn_shapes)):
                if self.shape.roi == self.parent().drawn_shapes[i].roi:
                    self.parent().on_region_move_change_requested.emit(i, toggle, is_attached)
                    break

        self.close_menu()

    def attachment(self, toggle):
        self.movement(toggle, toggle)

    def delete_region(self):
        self.parent().on_shape_deletion.emit([self.shape])
        self.close_menu()

    def close_menu(self):
        self.parent().on_context_menu_close.emit(self.caller_id)
