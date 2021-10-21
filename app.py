import sys, os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QIcon, QMouseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QSizeGrip

import qt_material

from splash import Ui_MainWindow as importSplash
from dashboard import Ui_MainWindow as importDashboard

# from main import Ui_MainWindow as importMain

# Global Variables
counter = 0


class Dashboard(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = importDashboard()
        self.ui.setupUi(self)
        qt_material.apply_stylesheet(self, theme="dark_amber.xml")
        # print(qt_material.list_themes())

        # Remove title bar and add translucent backgrouond
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Function to move window around
        def moveWindow(event):
            if not self.isMaximized():
                if event.buttons() == Qt.LeftButton:
                    self.move(self.pos() + event.globalPos() - self.clickPosition)
                    self.clickPosition = event.globalPos()
                    event.accept()

        self.ui.frmHeader.mouseMoveEvent = moveWindow

        # Shadow Effect Style
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setYOffset(0)
        self.shadow.setXOffset(0)
        self.shadow.setColor(QColor(0, 92, 157, 550))
        self.ui.centralwidget.setGraphicsEffect(self.shadow)

        self.setWindowIcon(QIcon("files/feather/cpu.svg"))
        self.setWindowTitle('Atlas')

        # Grip to resize the window
        QSizeGrip(self.ui.frmSizeGrip)
        self.buttonHandle()

        self.show()

    def buttonHandle(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(lambda: self.showMinimized())
        self.ui.btnRestore.clicked.connect(self.showRestore)

        # Show stacked widgets
        # self.ui.btnBattery.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stkBattery))

        self.stackSetter(self.ui.btnStorage, self.ui.stkStorage)
        self.stackSetter(self.ui.btnSensors, self.ui.stkSensors)
        self.stackSetter(self.ui.btnBattery, self.ui.stkBattery)
        self.stackSetter(self.ui.btnActivities, self.ui.stkActivities)
        self.stackSetter(self.ui.btnNetwork, self.ui.stkNetwork)
        self.stackSetter(self.ui.btnSystem, self.ui.stkSystem)
        self.stackSetter(self.ui.btnProcessor, self.ui.stkProcessor)

    def showRestore(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.btnRestore.setIcon(QIcon("files/feather/monitor.svg"))
        else:
            self.showMaximized()
            self.ui.btnRestore.setIcon(QIcon("files/feather/copy.svg"))

    def stackSetter(self, Button, Stack):
        Button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(Stack))

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clickPosition = a0.globalPos()


# class MainWindow(QMainWindow):
#     def __init__(self):
#         try:
#             super(MainWindow, self).__init__()
#             self.ui = importMain()
#             self.ui.setupUi(self)
#
#             QTimer.singleShot(2000, lambda: self.ui.lblTitle.setText("<b>Coming </b>Soon"))
#             QTimer.singleShot(2000, lambda: self.setStyleSheet("background: #333; color: #eee;"))
#         except Exception as err:
#             print(err)


class Splash(QMainWindow):
    def __init__(self):
        # super(Splash, self).__init__()
        # loadUi('files/splash.ui', self)
        QMainWindow.__init__(self)

        self.ui = importSplash()
        self.ui.setupUi(self)

        # Remove title Bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # DropShadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.ui.dropShadow.setGraphicsEffect(self.shadow)

        # Start QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

        QTimer.singleShot(2000, lambda: self.ui.lblDesc.setText("<b>Loading </b>Database"))
        QTimer.singleShot(3000, lambda: self.ui.lblDesc.setText("<b>Processing </b>Interface"))
        QTimer.singleShot(4000, lambda: self.ui.lblDesc.setText("<b>Updating </b>User Details"))
        QTimer.singleShot(5000, lambda: self.ui.lblDesc.setText("<b>Almost </b>Done"))

        self.show()

    def progress(self):
        global counter
        self.ui.progressBar.setValue(counter)
        if counter > 100:
            self.timer.stop()
            self.main = Dashboard()
            self.main.show()

            self.close()

        counter += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = Dashboard()
    sys.exit(app.exec_())
