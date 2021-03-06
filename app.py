import sys, os
import traceback

from PySide2.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QSizeGrip, QPushButton, QTableWidgetItem, QMessageBox, QProgressBar, QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QColor, QIcon, QMouseEvent
from PySide2.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QObject, Signal, QRunnable, Slot, QThreadPool


from multiprocessing import cpu_count
from desk_functions import myMsgBox
from sys import platform
from datetime import date, datetime
from time import sleep

import psutil as util
import platform

from splash import Ui_MainWindow as importSplash
from dashboard import Ui_MainWindow as importDashboard
import qt_material

# Global Variables
counter = 0
theme_color_tuple = (139, 195, 74)
theme_color_str = "106, 106, 106"
in_tray = False



class Work(QObject):
    progress = Signal(int)
    result = Signal(object)
    err = Signal(tuple)
    finished = Signal()


class Runner(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Runner, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Work()
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as err:
            traceback.print_exc()
            exc_type, val = sys.exc_info()[:2]
            self.signals.err.emit((exc_type, val, traceback.format_exc()))
        else:
            self.signals.err.emit(result)
        finally:
            self.signals.finished.emit()


class Dashboard(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = importDashboard()
        self.ui.setupUi(self)
        qt_material.apply_stylesheet(self, theme="dark_lightgreen.xml")
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

        self.thread_pool = QThreadPool()
        self.show()

        self.sysInfo()
        self.activities()
        self.storage()
        self.sensors()
        self.network()
        self.util_thread()

    def util_thread(self):
        work = Runner(self.cpu)
        work.signals.result.connect(self.print_output)
        work.signals.finished.connect(self.thread_complete)
        work.signals.progress.connect(self.progress_fn)

        self.thread_pool.start(work)

        work_battery = Runner(self.battery)
        work_battery.signals.result.connect(self.print_output)
        work_battery.signals.finished.connect(self.thread_complete)
        work_battery.signals.progress.connect(self.progress_fn)

        self.thread_pool.start(work_battery)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print('Thread Done')

    def progress_fn(self, n):
        print("%d%% done" % n)

    """BATTERY INFORMATION"""

    def battery(self, progress_callback):
        while True:
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
            self.ui.progBattery.rpb_setLineColor(theme_color_tuple)
            self.ui.progBattery.rpb_setPieColor((100, 100, 100))
            self.ui.progBattery.rpb_setTextColor((50, 50, 50))
            self.ui.progBattery.rpb_setInitialPos('North')
            self.ui.progBattery.rpb_setTextFormat('Percentage')
            self.ui.progBattery.rpb_setLineWidth(15)
            self.ui.progBattery.rpb_setPathWidth(15)
            self.ui.progBattery.rpb_setLineCap('SquareCap')
            self.ui.progBattery.rpb_setLineStyle('DotLine')

            sleep(1)

    """RAM AND SYSTEM INFORMATION"""

    def cpu(self, progress_callback):
        while True:
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
            self.ui.progCpu.spb_setValue((usedram, usedram, freeram))
            self.ui.progCpu.spb_lineColor((theme_color_tuple, (255, 255, 255), theme_color_tuple))
            self.ui.progCpu.spb_setInitialPos(('West', 'West', 'West'))
            self.ui.progCpu.spb_lineCap(('RoundCap', 'SquareCap', 'RoundCap'))
            self.ui.progCpu.spb_lineWidth(15)
            self.ui.progCpu.spb_setPathHidden(True)
            self.ui.progCpu.spb_setGap(25)

            self.ui.lblCpuCounter.setText(str(cpu_count()))
            self.ui.lblCpuCore.setText(str(util.cpu_count(logical=False)))

            self.ui.progRam.rpb_setMaximum(100)
            self.ui.progRam.rpb_setValue(util.cpu_percent())
            self.ui.progRam.rpb_setBarStyle('Pizza')
            self.ui.progRam.rpb_setLineColor(theme_color_tuple)
            self.ui.progRam.rpb_setTextColor((49, 54, 59))
            self.ui.progRam.rpb_setInitialPos('North')
            self.ui.progRam.rpb_setLineWidth(13)

            sleep(0.5)

    """PROCESSES AND PIDS"""

    def createTable(self, row, column, text, tblName):
        tableWidget = QTableWidgetItem()
        getattr(self.ui, tblName).setItem(row, column, tableWidget)
        tableWidget = getattr(self.ui, tblName).item(row, column)
        tableWidget.setText(text)

    def createTableButton(self, name, color, row, col):
        Btn = QPushButton(self.ui.tblActivities)
        Btn.setText(name)
        Btn.setStyleSheet(f"color: {color}")
        self.ui.tblActivities.setCellWidget(row, col, Btn)

    def activities(self):
        for pids in util.pids():
            rowPosition = self.ui.tblActivities.rowCount()
            self.ui.tblActivities.insertRow(rowPosition)

            try:
                process = util.Process(pids)
                self.createTable(rowPosition, 0, f"{process.pid}", "tblActivities")
                self.createTable(rowPosition, 1, f"{process.name()}", "tblActivities")
                self.createTable(rowPosition, 2, f"{process.status()}", "tblActivities")
                self.createTable(rowPosition, 3, f"{datetime.utcfromtimestamp(process.create_time()).strftime('%H:%M:%S | %A %B %d, %Y ')}", "tblActivities")

                self.ui.tblActivities.verticalHeader().setDefaultSectionSize(55)

                self.createTableButton('Suspend', f'rgb({theme_color_str})', rowPosition, 4)
                self.createTableButton('Resume', 'rgb(72, 168, 104)', rowPosition, 5)
                self.createTableButton('Terminate', 'rgb(220, 20, 60)', rowPosition, 6)
                self.createTableButton('Kill ', 'rgb(255, 255, 255)', rowPosition, 7)

            except Exception as err:
                myMsgBox(str(err), 'Table Error', QMessageBox.Warning)

            self.ui.txtActivities.textChanged.connect(self.findName)

    def findName(self):
        name = self.ui.txtActivities.text().lower()
        for row in range(self.ui.tblActivities.rowCount()):
            item = self.ui.tblActivities.item(row, 1)
            id = self.ui.tblActivities.item(row, 0)

            # If search is not in the item, do not hide the row
            self.ui.tblActivities.setRowHidden(row, name not in item.text().lower())

    '''SYSTEM INFORMATION'''

    def sysInfo(self):
        self.ui.lblSysDate.setText(datetime.now().strftime("%A, %B the %d, %Y"))
        self.ui.lblSysTime.setText(datetime.now().strftime("%H:%M:%S"))

        self.ui.lblSysMachine.setText(platform.machine())
        self.ui.lblSysPlatform.setText(platform.platform())
        self.ui.lblSysVersion.setText(platform.version())
        self.ui.lblSysInfo.setText(platform.system())
        self.ui.lblSysProc.setText(platform.processor())

    '''STORAGE INFORMATION'''

    def storage(self):
        div = pow(1024, 3)
        stores = util.disk_partitions(False)
        x = 0
        # Device, Mount point, OPTS, Max file, Max Path, Total used & free storage
        for store in stores:
            rowPosition = self.ui.tblStorage.rowCount()
            self.ui.tblStorage.insertRow(rowPosition)

            self.createTable(rowPosition, 0, store.device, "tblStorage")
            self.createTable(rowPosition, 1, store.mountpoint, "tblStorage")
            self.createTable(rowPosition, 2, store.fstype, "tblStorage")
            self.createTable(rowPosition, 3, str(store.opts), 'tblStorage')

            if sys.platform.find('linux') >= 0:
                self.createTable(rowPosition, 4, str(store.maxpath), 'tblStorage')
                self.createTable(rowPosition, 5, str(store.maxfile), 'tblStorage')
            else:
                self.createTable(rowPosition, 4, f"Not Available", 'tblStorage')
                self.createTable(rowPosition, 5, f"Not Available", 'tblStorage')

            try:
                disk = util.disk_usage(store.mountpoint)
                self.createTable(rowPosition, 6, f"{disk.total / div:.2f} GB", 'tblStorage')
                self.createTable(rowPosition, 7, f"{disk.used / div:.2f} GB", 'tblStorage')
                self.createTable(rowPosition, 8, f"{disk.free / div:.2f} GB", 'tblStorage')

                fulldisk = (disk.used / disk.total) * 100
                progBar = QProgressBar(self.ui.tblStorage)
                progBar.setObjectName(u"progStorage")
                progBar.setValue(fulldisk)
                self.ui.tblStorage.setCellWidget(rowPosition, 9, progBar)
            except Exception as err:
                # myMsgBox(str(err), 'Disk Error')
                print(err)

    ''' SENSORS FOR LINUX'''

    def sensors(self):
        if sys.platform.find('linux') >= 0:
            try:
                for temp in util.sensors_temperatures():
                    for tmp in util.sensors_temperatures()[temp]:
                        rowPos = self.ui.tblSensors.rowCount()
                        self.ui.tblSensors.insertRow(rowPos)

                        self.createTable(rowPos, 0, temp, 'tblSensors')
                        self.createTable(rowPos, 1, tmp.label, 'tblSensors')
                        self.createTable(rowPos, 2, str(tmp.current), 'tblSensors')
                        self.createTable(rowPos, 3, str(tmp.high), 'tblSensors')
                        self.createTable(rowPos, 4, str(tmp.critical), 'tblSensors')

                        per_tmp = (tmp.current / tmp.high) * 100
                        progBar = QProgressBar(self.ui.tblSensors)
                        progBar.objectName(u"progSensors")
                        progBar.setValue(per_tmp)
                        self.ui.tblSensors.setCellWidget(rowPos, 5, progBar)
            except Exception as err:
                myMsgBox(str(err), 'Sensory Error')
        else:
            rowPos = self.ui.tblSensors.rowCount()
            self.ui.tblSensors.insertRow(rowPos)

            self.createTable(rowPos, 0, 'Unavailable', 'tblSensors')
            self.createTable(rowPos, 1, 'Null', 'tblSensors')
            self.createTable(rowPos, 2, 'Null', 'tblSensors')
            self.createTable(rowPos, 3, 'Null', 'tblSensors')
            self.createTable(rowPos, 4, 'Null', 'tblSensors')
            self.createTable(rowPos, 5, 'Null', 'tblSensors')

    '''NETWORK'''

    def network(self):
        # For Netstats
        NetStats = util.net_if_stats()
        for net in NetStats:
            rowPos = self.ui.tblNetStats.rowCount()
            self.ui.tblNetStats.insertRow(rowPos)

            self.createTable(rowPos, 0, net, 'tblNetStats')
            self.createTable(rowPos, 1, f"{NetStats[net].isup}", 'tblNetStats')
            self.createTable(rowPos, 2, f"{NetStats[net].duplex}", 'tblNetStats')
            self.createTable(rowPos, 3, f"{NetStats[net].speed}", 'tblNetStats')
            self.createTable(rowPos, 4, f"{NetStats[net].mtu}", 'tblNetStats')

        # NET CONNECTIONS

        for net in util.net_connections():
            rowPos = self.ui.tblNetConn.rowCount()
            self.ui.tblNetConn.insertRow(rowPos)

            self.createTable(rowPos, 0, str(net.fd), 'tblNetConn')
            self.createTable(rowPos, 1, str(net.family), 'tblNetConn')
            self.createTable(rowPos, 2, str(net.type), 'tblNetConn')
            self.createTable(rowPos, 3, str(net.laddr), 'tblNetConn')
            self.createTable(rowPos, 4, str(net.raddr), 'tblNetConn')
            self.createTable(rowPos, 5, str(net.status), 'tblNetConn')
            self.createTable(rowPos, 6, str(net.pid), 'tblNetConn')

        # FOR NET COUNTERS
        NetCount = util.net_io_counters(pernic=True)
        for net in NetCount:
            rowPos = self.ui.tblNetCounters.rowCount()
            self.ui.tblNetCounters.insertRow(rowPos)

            self.createTable(rowPos, 0, str(net), 'tblNetCounters')
            self.createTable(rowPos, 1, f"{NetCount[net].bytes_sent}", 'tblNetCounters')
            self.createTable(rowPos, 2, f"{NetCount[net].bytes_recv}", 'tblNetCounters')
            self.createTable(rowPos, 3, f"{NetCount[net].packets_sent}", 'tblNetCounters')
            self.createTable(rowPos, 4, f"{NetCount[net].packets_recv}", 'tblNetCounters')
            self.createTable(rowPos, 5, f"{NetCount[net].errin}", 'tblNetCounters')
            self.createTable(rowPos, 6, f"{NetCount[net].errout}", 'tblNetCounters')
            self.createTable(rowPos, 7, f"{NetCount[net].dropin}", 'tblNetCounters')
            self.createTable(rowPos, 8, f"{NetCount[net].dropout}", 'tblNetCounters')

        # NET ADDRESS

        NetAddr = util.net_if_addrs()
        for net in NetAddr:
            for addr in NetAddr[net]:
                rowPos = self.ui.tblNetAddr.rowCount()
                self.ui.tblNetAddr.insertRow(rowPos)

                self.createTable(rowPos, 0, str(net), 'tblNetAddr')
                self.createTable(rowPos, 1, str(addr.family), 'tblNetAddr')
                self.createTable(rowPos, 2, str(addr.address), 'tblNetAddr')
                self.createTable(rowPos, 3, str(addr.netmask), 'tblNetAddr')
                self.createTable(rowPos, 4, str(addr.broadcast), 'tblNetAddr')
                self.createTable(rowPos, 5, str(addr.ptp), 'tblNetAddr')

    # Function to convert seconds to hours
    def secsToHours(self, secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def applyBtnStyle(self):
        for btn in self.ui.frmMenu.findChildren(QPushButton):
            if btn.objectName() != self.sender().objectName():
                btn.setStyleSheet("background-color: none;")

        self.sender().setStyleSheet(f"background-color: rgb{theme_color_tuple}")

    def buttonHandle(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(lambda: self.showMinimized())
        self.ui.btnRestore.clicked.connect(self.showRestore)
        self.ui.btnMenu.clicked.connect(self.animateMenu)
        self.ui.chkTray.stateChanged.connect(self.sendToTray)
        self.ui.chkSaveData.stateChanged.connect(self.saveData)

        # Show stacked widgets
        # self.ui.btnBattery.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stkBattery))

        self.stackSetter(self.ui.btnStorage, self.ui.stkStorage)
        self.stackSetter(self.ui.btnSensors, self.ui.stkSensors)
        self.stackSetter(self.ui.btnBattery, self.ui.stkBattery, 1)
        self.stackSetter(self.ui.btnActivities, self.ui.stkActivities)
        self.stackSetter(self.ui.btnNetwork, self.ui.stkNetwork)
        self.stackSetter(self.ui.btnSystem, self.ui.stkSystem)
        self.stackSetter(self.ui.btnProcessor, self.ui.stkProcessor, 2)

    def sendToTray(self):
        if self.ui.chkTray.isChecked():
            self.tray = QSystemTrayIcon(QIcon('files/feather/cpu.svg'), parent=app)
            self.tray.setToolTip('Check out my tray')
            self.tray.show()

            menu = QMenu()

            restoreAct = menu.addAction('Restore')
            restoreAct.triggered.connect(self.hideTray)
            exitAct = menu.addAction('Exit')
            exitAct.triggered.connect(app.quit)

            self.tray.setContextMenu(menu)
            self.hide()

    def hideTray(self):
        self.show()
        self.tray.hide()
        self.ui.chkTray.setChecked(False)

    def saveData(self):
        isSaving = False
        if self.ui.chkSaveData.isChecked():
            if not isSaving:
            # os.system(f'{os.getcwd()}\\files\\stop.bat')
                try:
                    # Code to save data here
                    isSaving = True
                except Exception as err:
                    print('Error:', err)
        else:
            reply = myMsgBox("Are you sure you want to turn off Data Saver?", "Turn off Saver?!", QMessageBox.Question, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                print("Wakaa")
            else:
                # Todo: make save checkbox respond well
                self.ui.chkSaveData.setChecked(True)

    def showRestore(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.btnRestore.setIcon(QIcon("files/feather/monitor.svg"))
        else:
            self.showMaximized()
            self.ui.btnRestore.setIcon(QIcon("files/feather/copy.svg"))

    def stackSetter(self, Button, Stack, Queue=None):
        Button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(Stack))

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
