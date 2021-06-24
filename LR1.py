"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
"""

import json
import statistics
import sys

import numpy as np
import pyqtgraph as pg
from PyQt5 import uic, QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

PROJECT_FOLDER = 'LR1_data'


def valmap(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        # Variables
        self.keys = []
        self.data_x = []
        self.data_y = []
        self.blocks = []
        self.max_block_value = 0
        self.bars_x = []
        self.bars_y = []

        # Load GUI file
        self.gui = uic.loadUi('LR1.ui')
        self.gui.show()

        # Connect GUI controls
        self.gui.pushButton.clicked.connect(self.save_keys)
        self.gui.pushButton_2.clicked.connect(self.load_keys)
        self.gui.pushButton_3.clicked.connect(self.generate)
        self.gui.radioButton.clicked.connect(self.update_view)
        self.gui.radioButton_2.clicked.connect(self.update_view)
        self.gui.radioButton_3.clicked.connect(self.update_view)
        self.gui.radioButton_4.clicked.connect(self.update_view)

        # Initialize charts and tables
        self.init_charts()
        self.init_tables()

    """
    Initializes charts
    """

    def init_charts(self):
        self.gui.graphWidget.setBackground(QtGui.QColor('white'))
        self.gui.graphWidget_2.setBackground(QtGui.QColor('white'))
        self.gui.graphWidget_3.setBackground(QtGui.QColor('white'))
        self.gui.graphWidget_4.setBackground(QtGui.QColor('white'))
        # self.gui.graphWidget.getAxis('left').setPen(QtGui.QColor('black'))
        # self.gui.graphWidget.getAxis('left').setTextPen(QtGui.QColor('black'))
        # self.gui.graphWidget.getAxis('bottom').setPen(QtGui.QColor('black'))
        # self.gui.graphWidget.getAxis('bottom').setTextPen(QtGui.QColor('black'))
        self.gui.graphWidget_2.getPlotItem().hideAxis('left')
        self.gui.graphWidget_3.getPlotItem().hideAxis('bottom')
        self.gui.graphWidget.showGrid(x=True, y=True, alpha=1.0)
        self.gui.graphWidget_2.showGrid(x=True, y=True, alpha=1.0)
        self.gui.graphWidget_3.showGrid(x=True, y=True, alpha=1.0)
        self.gui.graphWidget_4.showGrid(x=True, y=True, alpha=1.0)

    """
    Initializes tables
    """

    def init_tables(self):
        # Key parameters table
        self.gui.tableWidget.setColumnCount(5)
        self.gui.tableWidget.setRowCount(4)
        self.gui.tableWidget.horizontalHeader().setVisible(False)
        self.gui.tableWidget.setCornerButtonEnabled(False)
        self.gui.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.gui.tableWidget.setFocusPolicy(Qt.NoFocus)

        header = self.gui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(self.gui.tableWidget.columnCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        header = self.gui.tableWidget.verticalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(self.gui.tableWidget.rowCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.gui.tableWidget.setVerticalHeaderLabels(['X1', 'Y1', 'X2', 'Y2'])

        # Stats table
        self.gui.tableWidget_2.setColumnCount(1)
        self.gui.tableWidget_2.setRowCount(4)
        self.gui.tableWidget_2.setCornerButtonEnabled(False)
        self.gui.tableWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.gui.tableWidget_2.setFocusPolicy(Qt.NoFocus)
        self.gui.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        header = self.gui.tableWidget_2.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(self.gui.tableWidget_2.columnCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        header = self.gui.tableWidget_2.verticalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(self.gui.tableWidget_2.rowCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.gui.tableWidget_2.setVerticalHeaderLabels(['AVG', 'DISP', 'MODE', 'MEDIAN'])
        self.gui.tableWidget_2.setHorizontalHeaderLabels(['Math stats (Y - axis)'])

    """
    Generates random X numbers and calcultaes Y values
    """

    def generate(self):
        # Check if keys are loaded
        assert len(self.keys) > 0

        self.data_x = [[round(num, 4) for num in np.random.sample(self.gui.spinBox.value())],
                       [round(num, 4) for num in np.random.sample(self.gui.spinBox.value())]]
        self.data_y = []

        for i in range(2):
            array_y = []
            for data_x in self.data_x[i]:
                # Calculate Y
                if self.keys[0][0] <= data_x <= self.keys[0][1]:
                    # if X >= keys_X1[0] && X <= keys_X1[1]
                    # Y = keys_Y1[1] / keys_X1[1] * X
                    array_y.append(self.keys[1][1] / self.keys[0][1] * data_x)
                if self.keys[0][1] < data_x <= self.keys[0][2]:
                    # if X > keys_X1[1] && X <= keys_X1[2]
                    # Y = keys_Y1[2] / keys_X1[2] * X
                    array_y.append(self.keys[1][2] / self.keys[0][2] * data_x)
                if self.keys[0][2] < data_x <= self.keys[0][3]:
                    # if X > keys_X1[2] && X <= keys_X1[3]
                    # Y = keys_Y1[3] / keys_X1[3] * X
                    array_y.append(self.keys[1][3] / self.keys[0][3] * data_x)
                if self.keys[0][3] < data_x <= self.keys[0][4]:
                    # if X > keys_X1[3] && X <= keys_X1[4]
                    # Y = keys_Y1[4] / keys_X1[4] * X
                    array_y.append(self.keys[1][4] / self.keys[0][4] * data_x)

            # Normalize data
            array_y /= max(array_y)

            self.data_y.append(array_y)

        self.update_view()

    """
    Draws keys chart, main chart and bar charts
    """

    def update_view(self):
        # Keys chart
        if self.gui.radioButton.isChecked():
            # X1 Y1
            keys_x = self.keys[0]
            keys_y = self.keys[1]
            data_x = self.data_x[0]
            data_y = self.data_y[0]
        elif self.gui.radioButton_2.isChecked():
            # X1 X2
            keys_x = self.keys[0]
            keys_y = self.keys[2]
            data_x = self.data_x[0]
            data_y = self.data_x[1]
        elif self.gui.radioButton_3.isChecked():
            # X2 Y2
            keys_x = self.keys[2]
            keys_y = self.keys[3]
            data_x = self.data_x[1]
            data_y = self.data_y[1]
        else:
            # X1 Y2
            keys_x = self.keys[1]
            keys_y = self.keys[3]
            data_x = self.data_x[0]
            data_y = self.data_y[1]

        self.gui.graphWidget_4.clear()
        self.gui.graphWidget_4.plot(keys_x, keys_y, pen=pg.mkPen(QtGui.QColor('red')),
                                    symbolBrush=(255, 0, 0),
                                    symbolSize=5)

        # Count how many points in each block
        self.count_blocks(data_x, data_y)

        # Draw blocks (background)
        self.gui.graphWidget.clear()
        for x in range(10):
            for y in range(10):
                self.gui.graphWidget.addItem(
                    RectItem(QtCore.QRectF(x / 10, y / 10, 0.1, 0.1),
                             alpha=valmap(self.blocks[x][y], 0, self.max_block_value, 0, 1)))

        # Draw main chart
        self.gui.graphWidget.plot(data_x, data_y, pen=None,
                                  symbolBrush=(255, 0, 0), symbolSize=5, symbolPen=None)

        # Bar charts
        bar_x = list(range(10))
        self.gui.graphWidget_2.clear()
        self.gui.graphWidget_3.clear()
        bar_top = pg.BarGraphItem(x=bar_x, height=self.bars_x, width=0.9, brush=QtGui.QColor('pink'))
        bar_right = pg.BarGraphItem(x=bar_x, height=self.bars_y, width=0.9, brush=QtGui.QColor('pink'))
        bar_right.rotate(-90)
        self.gui.graphWidget_3.addItem(bar_top)
        self.gui.graphWidget_2.addItem(bar_right)

        # Math stats
        self.count_stats(data_y)

    """
    Counts how many points in each block
    """

    def count_blocks(self, data_x, data_y):
        self.max_block_value = 0
        self.blocks = []
        self.bars_x = [0] * 10
        self.bars_y = [0] * 10
        for x in range(10):
            blocks_column = []
            for y in range(10):
                points_in_block = 0
                for i in range(len(data_x)):
                    if x / 10 <= data_x[i] < (x / 10 + 0.1) \
                            and y / 10 <= data_y[i] < (y / 10 + 0.1):
                        points_in_block += 1
                if points_in_block > self.max_block_value:
                    self.max_block_value = points_in_block

                self.bars_x[x] += points_in_block
                self.bars_y[y] += points_in_block

                blocks_column.append(points_in_block)

            self.blocks.append(blocks_column)
        self.bars_y.reverse()

    """
    Calculates math stats (average, dispertion, mode, median)
    """

    # noinspection PyBroadException
    def count_stats(self, data_y):
        # Average
        average = sum(data_y) / len(data_y)

        # Dispertion
        disp_sum = 0
        for point in data_y:
            disp_sum += (point - average) * (point - average)
        dispertion = disp_sum / sum(data_y)

        # Median
        try:
            mode = statistics.mode(data_y)
        except:
            mode = None

        # Median
        median = statistics.median(data_y)

        # Fill table
        self.gui.tableWidget_2.setItem(0, 0, QTableWidgetItem(str(average)))
        self.gui.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(dispertion)))
        if mode is not None:
            self.gui.tableWidget_2.setItem(0, 2, QTableWidgetItem(str(mode)))
        else:
            self.gui.tableWidget_2.setItem(0, 2, QTableWidgetItem('No Mode'))
        self.gui.tableWidget_2.setItem(0, 3, QTableWidgetItem(str(median)))

    """
    Saves keys to JSON file
    """

    def save_keys(self):
        self.keys = []
        for i in range(self.gui.tableWidget.rowCount()):
            keys_row = []
            for k in range(self.gui.tableWidget.columnCount()):
                keys_row.append(float(self.gui.tableWidget.item(i, k).text()))
            self.keys.append(keys_row)

        with open(PROJECT_FOLDER + '/keys.json', 'w') as f:
            json.dump(self.keys, f)

    """
    Loads keys from JSON file
    """

    def load_keys(self):
        self.keys = np.array(json.load(open(PROJECT_FOLDER + '/keys.json')))

        for i in range(self.gui.tableWidget.rowCount()):
            for k in range(self.gui.tableWidget.columnCount()):
                self.gui.tableWidget.setItem(i, k, QTableWidgetItem(str(self.keys[i][k])))


"""
This class draws rectangles on the chart
"""


class RectItem(pg.GraphicsObject):
    def __init__(self, rect, alpha=1.0, parent=None):
        super().__init__(parent)
        self._rect = rect
        self._alpha = alpha
        self.picture = QtGui.QPicture()
        self._generate_picture()

    @property
    def rect(self):
        return self._rect

    @property
    def alpha(self):
        return self._alpha

    def _generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        color = QtGui.QColor('green')
        color.setAlphaF(self.alpha)
        painter.setPen(pg.mkPen(color))
        painter.setBrush(pg.mkBrush(color))
        painter.drawRect(self.rect)
        painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
