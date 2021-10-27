import sys, os
from sys import platform

# from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
# from PyQt5.QtGui import QColor, QIcon, QMouseEvent
# from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QSizeGrip

from PySide2.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QSizeGrip, QPushButton
from PySide2.QtGui import QColor, QIcon, QMouseEvent
from PySide2.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from multiprocessing import cpu_count

import qt_material
import psutil as util
import platform

from splash import Ui_MainWindow as importSplash
from dashboard import Ui_MainWindow as importDashboard
from datetime import date, datetime

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

        for btn in self.ui.frmMenu.findChildren(QPushButton):
            btn.clicked.connect(self.applyBtnStyle)

        self.battery()
        self.sysInfo()
        self.show()

    """BATTERY INFORMATION"""

    def battery(self):
        Battery = util.sensors_battery()
        if not hasattr(util, "sensors battery"):
            self.ui.lblBatteryStatus.setText("Platform not supported!")

        if Battery is None:
            self.ui.lblBatteryStatus.setText("Battery not found")

        if Battery.power_plugged:
            self.ui.lblBatteryCharge.setText(f"{round(Battery.percent, 2)}%")
            self.ui.lblBatteryTimeLeft.setText("Null")
            if Battery.percent < 100:
                self.ui.lblBatteryStatus.setText('Battery Charging!')
            else:
                self.ui.lblBatteryStatus.setText('Battery Charged Fully!')
            self.ui.lblBatteryPlugged.setText('Yes')
        else:
            self.ui.lblBatteryPlugged.setText('No')
            self.ui.lblBatteryStatus.setText(f"{round(Battery.percent, 2)}%")
            self.ui.lblBatteryTimeLeft.setText(self.secsToHours(Battery.secsleft))
            if Battery.percent < 100:
                self.ui.lblBatteryStatus.setText('Battery Discharging')
            else:
                self.ui.lblBatteryStatus.setText('Battery Full')

        self.ui.progBattery.rpb_setMaximum(100)
        self.ui.progBattery.rpb_setValue(Battery.percent)
        # 'Line', 'Donet', 'Hybrid1', 'Pizza', 'Pie' and 'Hybrid2'
        self.ui.progBattery.rpb_setBarStyle('Pizza')
        self.ui.progBattery.rpb_setLineColor((255, 215, 64))
        self.ui.progBattery.rpb_setPieColor((100, 100, 100))
        self.ui.progBattery.rpb_setTextColor((50, 50, 50))
        self.ui.progBattery.rpb_setInitialPos('North')
        self.ui.progBattery.rpb_setTextFormat('Percentage')
        self.ui.progBattery.rpb_setLineWidth(15)
        self.ui.progBattery.rpb_setPathWidth(15)
        self.ui.progBattery.rpb_setLineCap('SquareCap')
        self.ui.progBattery.rpb_setLineStyle('DotLine')

    """RAM AND SYSTEM INFORMATION"""

    def cpu(self):
        div = pow(1024, 3)
        totalram = util.virtual_memory()[0] / div
        self.ui.lblRamTotal.setText(f"{totalram:.4f}GB")

        availram = util.virtual_memory()[1] / div
        self.ui.lblRamAvail.setText(f"{availram:.4f}GB")

        usedram = util.virtual_memory()[3] / div
        self.ui.lblRamUsed.setText(f"{usedram:.4f}GB")

        freeram = util.virtual_memory()[4] / div
        self.ui.lblRamFree.setText(f"{freeram:.4f}GB")

        availram = util.virtual_memory()[2]
        self.ui.lblRamUsage.setText(f"{availram:.1f}%")

        self.ui.progCpu.spb_setMinimum((0, 0, 0))
        self.ui.progCpu.spb_setMaximum((totalram, totalram, totalram))
        self.ui.progCpu.spb_setValue((availram, usedram, freeram))
        print(totalram, availram, usedram, freeram)
        self.ui.progCpu.spb_lineColor(((255, 215, 64), (255, 255, 255), (255, 215, 64)))
        self.ui.progCpu.spb_setInitialPos(('West', 'West', 'West'))
        self.ui.progCpu.spb_lineCap(('RoundCap', 'SquareCap', 'RoundCap'))
        self.ui.progCpu.spb_lineWidth(15)
        self.ui.progCpu.spb_setPathHidden(True)
        self.ui.progCpu.spb_setGap(25)


        self.ui.lblCpuCounter.setText(str(cpu_count()))
        self.ui.lblCpuPer.setText(f"{util.cpu_percent()}")
        self.ui.lblCpuCore.setText(str(util.cpu_count(logical=False)))

        
        self.ui.progRam.rpb_setMaximum(100)
        self.ui.progRam.rpb_setValue(availram)
        self.ui.progRam.rpb_setBarStyle('Pizza')
        self.ui.progRam.rpb_setLineColor((255, 215, 64))
        self.ui.progRam.rpb_setTextColor((49, 54, 59))
        self.ui.progRam.rpb_setInitialPos('North')
        self.ui.progRam.rpb_setLineWidth(13)

    def sysInfo(self):
        self.ui.lblSysDate.setText(datetime.now().strftime("%A, %B the %d, %Y"))
        self.ui.lblSysTime.setText(datetime.now().strftime("%H:%M:%S"))
        
        self.ui.lblSysMachine.setText(platform.machine())
        self.ui.lblSysPlatform.setText(platform.platform())
        self.ui.lblSysVersion.setText(platform.version())
        self.ui.lblSysInfo.setText(platform.system())
        self.ui.lblSysProc.setText(platform.processor())



    # Function to convert seconds to hours
    def secsToHours(self, secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def applyBtnStyle(self):
        for btn in self.ui.frmMenu.findChildren(QPushButton):
            if btn.objectName() != self.sender().objectName():
                btn.setStyleSheet("background-color: none;")

        self.sender().setStyleSheet("background-color: #FFD740")

    def buttonHandle(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(lambda: self.showMinimized())
        self.ui.btnRestore.clicked.connect(self.showRestore)
        self.ui.btnMenu.clicked.connect(self.animateMenu)

        # Show stacked widgets
        # self.ui.btnBattery.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stkBattery))

        self.stackSetter(self.ui.btnStorage, self.ui.stkStorage)
        self.stackSetter(self.ui.btnSensors, self.ui.stkSensors)
        self.stackSetter(self.ui.btnBattery, self.ui.stkBattery, 1)
        self.stackSetter(self.ui.btnActivities, self.ui.stkActivities)
        self.stackSetter(self.ui.btnNetwork, self.ui.stkNetwork)
        self.stackSetter(self.ui.btnSystem, self.ui.stkSystem)
        self.stackSetter(self.ui.btnProcessor, self.ui.stkProcessor, 2)

    def showRestore(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.btnRestore.setIcon(QIcon("files/feather/monitor.svg"))
        else:
            self.showMaximized()
            self.ui.btnRestore.setIcon(QIcon("files/feather/copy.svg"))

    def stackSetter(self, Button, Stack, Queue=None):
        Button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(Stack))
        if Queue == 1:
            self.battery()
        elif Queue == 2:
            self.cpu()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clickPosition = a0.globalPos()

    def animateMenu(self):
        mWidth = self.ui.frmBodyLeft.width()
        if mWidth <= 200:
            nmWidth = 500
        else:
            nmWidth = 100
        self.animate = QPropertyAnimation(self.ui.frmBodyLeft, b'maximumWidth')
        self.animate.setDuration(1000)
        self.animate.setStartValue(mWidth)
        self.animate.setEndValue(nmWidth)
        self.animate.setEasingCurve(QEasingCurve.InOutQuart)
        self.animate.start()


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
