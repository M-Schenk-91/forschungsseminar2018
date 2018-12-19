
from PyQt5 import QtCore, QtGui, QtWidgets
from style import style
from datastructures.TrackableTypes import FileType


def clickable(widget):
    class Filter(QtCore.QObject):
        press = QtCore.pyqtSignal(QtCore.QEvent)
        move = QtCore.pyqtSignal(QtCore.QEvent)
        release = QtCore.pyqtSignal(QtCore.QEvent)

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.press.emit(event)

                        return True

                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.release.emit(event)

                        return True

                if event.type() == QtCore.QEvent.MouseMove:
                    if obj.rect().contains(event.pos()):
                        self.move.emit(event)

                        return True

            return False

    filter = Filter(widget)

    widget.installEventFilter(filter)

    return filter.press, filter.release, filter.move


class QFileIconWidget(QtWidgets.QLabel):
    on_mouse_move = QtCore.pyqtSignal()

    def __init__(self, width, height, parent, type_, path='res/img/file_icon.png', name='dummy', file=None):
        # http://www.clker.com/clipart-new-file-simple.html

        super(QFileIconWidget, self).__init__()

        self.default_width = width
        self.default_height = height
        self.name = name
        self.setCursor(QtCore.Qt.BlankCursor)

        self.setParent(parent)
        self.file = file
        self.type = type_

        self.is_affected_by_effect = False
        self.setObjectName("file")

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setPixmap(QtGui.QPixmap(path).scaledToWidth(width))
        self.setScaledContents(False)
        self.is_over_icon = False

        self.name_widget = QtWidgets.QTextEdit()
        self.name_widget.setReadOnly(True)
        self.name_widget.setParent(self.parent())
        self.name_widget.setText(self.name)
        self.name_widget.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.name_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.name_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.name_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.name_widget.setStyleSheet(style.WidgetStyle.QTEXTEDIT_STYLE.value)
        self.name_widget.setGeometry(self.x() - 15, self.y() + 5, self.width() + 30, 20)
        self.name_widget.setCursor(QtCore.Qt.BlankCursor)

        self.name_widget.press, self.name_widget.release, self.name_widget.move = clickable(self.name_widget)

        self.name_widget.press.connect(self.mousePressEvent)
        self.name_widget.release.connect(self.mouseReleaseEvent)
        self.name_widget.move.connect(self.mouseMoveEvent)

        self.name_widget.setCursor(QtCore.Qt.BlankCursor)

        self.name_widget.show()

        if self.type == FileType.TEXT.value:
            width = 455
            height = 625

            self.preview_default_width = width
            self.preview_default_height = height

            self.preview = QtWidgets.QTextEdit()
            self.preview.setReadOnly(True)
            self.preview.setParent(self.parent())
            self.preview.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.preview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.preview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.preview.setStyleSheet(style.WidgetStyle.QTEXTEDIT_STYLE.value)
            self.preview.setGeometry(self.x() + self.width() / 2, self.y() + self.height() / 2, self.preview_default_width, self.preview_default_height)
            self.preview.setCursor(QtCore.Qt.BlankCursor)
            self.preview.setAcceptRichText(True)
            self.preview.setHtml(self.file.content)

        elif self.type == FileType.IMAGE.value:

            self.preview = QtWidgets.QLabel()
            self.preview.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)

            if self.file.is_digital_twin:
                self.preview_default_width = 520 / 4
                self.preview_default_height = 695 / 4
                self.preview.setPixmap(QtGui.QPixmap(self.file.content).scaledToWidth(520 / 4))
            else:
                self.preview_default_width = 520
                self.preview_default_height = 100
                self.preview.setPixmap(QtGui.QPixmap(self.file.content).scaledToWidth(520))

            self.preview.setGeometry(self.x() + self.width() / 2, self.y() + self.height() / 2, self.preview_default_width, self.preview_default_height)
            self.preview.setCursor(QtCore.Qt.BlankCursor)

            self.preview.setParent(self.parent())

        self.preview.press, self.preview.release, self.preview.move = clickable(self.preview)

        self.preview.press.connect(self.mousePressEvent)
        self.preview.release.connect(self.mouseReleaseEvent)
        self.preview.move.connect(self.mouseMoveEvent)
        self.preview.hide()

        self.__mousePressPos = None
        self.__mouseMovePos = None

    def mousePressEvent(self, event):
        self.is_over_icon = True
        self.file.mouse_used = True

        if self.file.is_on_conveyor_belt:
            self.file.grabbed = True

        if event.buttons() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(QFileIconWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.is_over_icon = True
            self.file.mouse_used = True

            if self.file.is_on_conveyor_belt:
                self.file.grabbed = True

            current_position = self.mapToGlobal(self.pos())
            global_position = event.globalPos()

            new_position = self.mapFromGlobal(current_position + global_position - self.__mouseMovePos)

            self.file.set_position((new_position.x(), new_position.y()))

            self.move(new_position)

            self.__mouseMovePos = global_position
            self.on_mouse_move.emit()

        super(QFileIconWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_over_icon = False
        self.file.grabbed = False
        self.file.mouse_used = False

        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(QFileIconWidget, self).mouseReleaseEvent(event)

    def set_pos(self, pos):
        self.file.previously_touched = True
        self.move(pos.x() - self.width() / 2, pos.y() - self.height() / 2)
        self.on_mouse_move.emit()

    posi = QtCore.pyqtProperty(QtCore.QPointF, fset=set_pos)
