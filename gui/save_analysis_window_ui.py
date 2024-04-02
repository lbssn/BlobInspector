# -*- coding: utf-8 -*-

# This file is distributed under the terms of the GNU General Public License v3.0

################################################################################
## Form generated from reading UI file 'save_analysis_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)
from resources import resources_rc

class Ui_SaveAnalysisWindow(object):
    def setupUi(self, SaveAnalysisWindow):
        if not SaveAnalysisWindow.objectName():
            SaveAnalysisWindow.setObjectName(u"SaveAnalysisWindow")
        SaveAnalysisWindow.resize(597, 133)
        icon = QIcon()
        icon.addFile(u":/Icons/blob-161097_640.png", QSize(), QIcon.Normal, QIcon.Off)
        SaveAnalysisWindow.setWindowIcon(icon)
        self.gridLayout = QGridLayout(SaveAnalysisWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_SaveAnalysis = QPushButton(SaveAnalysisWindow)
        self.pb_SaveAnalysis.setObjectName(u"pb_SaveAnalysis")

        self.gridLayout.addWidget(self.pb_SaveAnalysis, 2, 4, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 2, 1, 1)

        self.le_FileName = QLineEdit(SaveAnalysisWindow)
        self.le_FileName.setObjectName(u"le_FileName")

        self.gridLayout.addWidget(self.le_FileName, 1, 1, 1, 4)

        self.label_2 = QLabel(SaveAnalysisWindow)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.pb_ChooseDestinationFolder = QPushButton(SaveAnalysisWindow)
        self.pb_ChooseDestinationFolder.setObjectName(u"pb_ChooseDestinationFolder")

        self.gridLayout.addWidget(self.pb_ChooseDestinationFolder, 0, 0, 1, 1)

        self.lb_DestinationFolder = QLabel(SaveAnalysisWindow)
        self.lb_DestinationFolder.setObjectName(u"lb_DestinationFolder")

        self.gridLayout.addWidget(self.lb_DestinationFolder, 0, 1, 1, 4)

        self.pb_Cancel = QPushButton(SaveAnalysisWindow)
        self.pb_Cancel.setObjectName(u"pb_Cancel")

        self.gridLayout.addWidget(self.pb_Cancel, 2, 3, 1, 1)


        self.retranslateUi(SaveAnalysisWindow)

        QMetaObject.connectSlotsByName(SaveAnalysisWindow)
    # setupUi

    def retranslateUi(self, SaveAnalysisWindow):
        SaveAnalysisWindow.setWindowTitle(QCoreApplication.translate("SaveAnalysisWindow", u"Save analysis", None))
        self.pb_SaveAnalysis.setText(QCoreApplication.translate("SaveAnalysisWindow", u"Save analysis", None))
        self.label_2.setText(QCoreApplication.translate("SaveAnalysisWindow", u"File name (without extension)", None))
        self.pb_ChooseDestinationFolder.setText(QCoreApplication.translate("SaveAnalysisWindow", u"Destination folder", None))
        self.lb_DestinationFolder.setText("")
        self.pb_Cancel.setText(QCoreApplication.translate("SaveAnalysisWindow", u"Cancel", None))
    # retranslateUi

