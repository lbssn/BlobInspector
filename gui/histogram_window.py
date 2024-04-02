# This file is distributed under the terms of the GNU General Public License v3.0

import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from gui.histogram_window_ui import Ui_wi_HistogramWindow

class HistogramWindow(QtWidgets.QWidget, Ui_wi_HistogramWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        
        self.pb_Quit.clicked.connect(self.close)

if __name__ == "__main":
    app = QtWidgets.QApplication(sys.argv)
    histogram_window = HistogramWindow()
    histogram_window.show()
    sys.exit(app.exec())