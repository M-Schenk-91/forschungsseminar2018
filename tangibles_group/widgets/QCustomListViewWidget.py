
from PyQt5 import QtCore, QtWidgets, QtGui

from enum import Enum


class QCustomListViewWidget(QtWidgets.QListView):
    def __init__(self, x, y, parent=None):
        super(QCustomListViewWidget, self).__init__(parent)
        self.setGeometry(x, y, 200, 100)
        self._model = QtGui.QStandardItemModel(self)
        self.setModel(self._model)

        self.item_icons = []
        self.item_texts = []
        self.item_progresses = []
        self.item_rows = {}
        self.setCursor(QtCore.Qt.BlankCursor)

    def set_parent(self, parent):
        self.setParent(parent)
        self.setItemDelegate(QCustomListViewItem(parent.app))

    def update_model_all(self, file_path, name):
        self.item_icons.append(QtGui.QPixmap(file_path).scaledToWidth(55))
        self.item_texts.append(name)
        self.item_progresses.append(0)

        for r, i in enumerate(self.item_texts):
            item = QtGui.QStandardItem(i)

            self.item_rows[r] = r

            self._model.setItem(r, 0, item)
            self._model.setData(self._model.index(r, 0), {'icon': self.item_icons[r:r + 1], 'progress': self.item_progresses[r]}, 256)

        self.setModel(self._model)

        self.setGeometry(self.x(), self.y(), self.width(), self.sizeHintForRow(0) * 1.4 * self.model().rowCount())

        self.show()

    def update_model_progress(self, progress, row):
        item = QtGui.QStandardItem(self.item_texts[self.item_rows[row]])

        self.item_progresses[self.item_rows[row]] = progress
        self._model.setItem(self.item_rows[row], 0, item)
        self._model.setData(self._model.index(self.item_rows[row], 0), {'icon': self.item_icons[self.item_rows[row]:self.item_rows[row] + 1], 'progress': self.item_progresses[self.item_rows[row]]}, 256)

    def update_model_remove_item(self, row):
        self._model.removeRow(self.item_rows[row])
        self.item_texts.pop(0)
        self.item_progresses.pop(0)
        self.item_icons.pop(0)

        self.setGeometry(self.x(), self.y(), self.width(), self.sizeHintForRow(0) * 1.4 * self.model().rowCount())

        keys = []

        for i in self.item_rows.keys():
            self.item_rows[i] -= 1

            if self.item_rows[i] < 0:
                keys.append(i)

        for k in keys:
            self.item_rows.pop(k, None)

        self.setUpdatesEnabled(True)

        if self.model().rowCount() == 0:
            self.hide()


class ImageType(Enum):
    PLACEHOLDER = 0
    FILE = 1
    PAPER = 2


class QCustomListViewItem(QtWidgets.QStyledItemDelegate):
    def __init__(self, app):
        QtWidgets.QStyledItemDelegate.__init__(self)

        self.padding = 2
        self.AlignmentFlag = QtCore.Qt.AlignLeft
        self.app = app
        self.progress_bar = QtWidgets.QStyleOptionProgressBar()

    def paint(self, painter, option, index):
        x = option.rect.x()
        y = option.rect.y()

        width = option.rect.width()
        height = option.rect.height() * 1.5

        data = index.data(256)

        icon_list = data['icon']
        progress = data['progress']

        text = index.data()

        for a, i in enumerate(icon_list):
            m = max([i.width(), i.height()])
            f = (height - 2 * self.padding) / m
            i = i.scaled(int(i.width() * f), int(i.height() * f))
            painter.drawPixmap(QtCore.QPoint(x, y + self.padding), i)
            x += height

        painter.drawText(QtCore.QRect(x + self.padding, y + self.padding, width - x - 2 * self.padding, height - 2 * self.padding), self.AlignmentFlag, text)

        self.progress_bar.state = QtWidgets.QStyle.State_Enabled
        self.progress_bar.direction = QtWidgets.QApplication.layoutDirection()
        self.progress_bar.rect = option.rect
        self.progress_bar.rect.setX(x + self.padding * 40)
        self.progress_bar.rect.setY(y + 2 * self.padding)
        self.progress_bar.rect.setWidth(65)
        self.progress_bar.fontMetrics = QtWidgets.QApplication.fontMetrics()
        self.progress_bar.minimum = 0
        self.progress_bar.maximum = 100
        self.progress_bar.textAlignment = QtCore.Qt.AlignCenter
        self.progress_bar.textVisible = True

        self.progress_bar.progress = progress

        self.app.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, self.progress_bar, painter)
