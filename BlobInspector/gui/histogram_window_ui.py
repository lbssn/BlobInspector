# -*- coding: utf-8 -*-

# This file is distributed under the terms of the GNU General Public License v3.0

################################################################################
## Form generated from reading UI file 'histogram_window.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)
from resources import resources_rc

class Ui_wi_HistogramWindow(object):
    def setupUi(self, wi_HistogramWindow):
        if not wi_HistogramWindow.objectName():
            wi_HistogramWindow.setObjectName(u"wi_HistogramWindow")
        wi_HistogramWindow.resize(695, 400)
        icon = QIcon()
        icon.addFile(u":/Icons/blob-161097_640.png", QSize(), QIcon.Normal, QIcon.Off)
        wi_HistogramWindow.setWindowIcon(icon)
        self.gridLayout = QGridLayout(wi_HistogramWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_Quit = QPushButton(wi_HistogramWindow)
        self.pb_Quit.setObjectName(u"pb_Quit")
        self.pb_Quit.setMaximumSize(QSize(100, 16777215))

        self.gridLayout.addWidget(self.pb_Quit, 1, 1, 1, 1)

        self.wi_Histogram = QWidget(wi_HistogramWindow)
        self.wi_Histogram.setObjectName(u"wi_Histogram")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wi_Histogram.sizePolicy().hasHeightForWidth())
        self.wi_Histogram.setSizePolicy(sizePolicy)
        self.wi_Histogram.setMinimumSize(QSize(0, 200))
        self.wi_Histogram.setBaseSize(QSize(400, 200))
        self.layout_Histogram = QVBoxLayout(self.wi_Histogram)
        self.layout_Histogram.setObjectName(u"layout_Histogram")

        self.gridLayout.addWidget(self.wi_Histogram, 0, 0, 1, 2)


        self.retranslateUi(wi_HistogramWindow)

        QMetaObject.connectSlotsByName(wi_HistogramWindow)
    # setupUi

    def retranslateUi(self, wi_HistogramWindow):
        wi_HistogramWindow.setWindowTitle(QCoreApplication.translate("wi_HistogramWindow", u"Histogram window", None))
        self.pb_Quit.setText(QCoreApplication.translate("wi_HistogramWindow", u"Quit", None))
    # retranslateUi
