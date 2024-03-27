# This file is distributed under the terms of the GNU General Public License v3.0

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
from gui.save_analysis_window_ui import Ui_SaveAnalysisWindow
from datetime import datetime

class SaveAnalysisWindow(QtWidgets.QWidget, Ui_SaveAnalysisWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)

        self.main_window = main_window
        self.pb_Cancel.clicked.connect(self.close)
        now = datetime.now()
        now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.le_FileName.setText(now_string)

if __name__ == "__main":
    app = QtWidgets.QApplication(sys.argv)
    save_analysis_window = SaveAnalysisWindow()
    save_analysis_window.show()
    sys.exit(app.exec())