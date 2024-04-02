# This file is distributed under the terms of the GNU General Public License v3.0

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTimer
import sys
from gui.batch_analysis_window_ui import Ui_BatchAnalysisWindow

class BatchAnalysisWindow(QtWidgets.QWidget, Ui_BatchAnalysisWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)

        self.main_window = main_window
        self.pb_Cancel.clicked.connect(self.close)

        self.timer = QTimer(self)


if __name__ == "__main":
    app = QtWidgets.QApplication(sys.argv)
    batch_analysis_window = BatchAnalysisWindow()
    batch_analysis_window.show()
    sys.exit(app.exec())