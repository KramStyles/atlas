import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect

from splash import Ui_MainWindow as importSplash
from main import Ui_MainWindow as importMain

# Global Variables
counter = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = importMain()
        self.ui.setupUi(self)

        QTimer.singleShot(2000, lambda: self.ui.lblTitle.setText("<b>Coming </b>Soon"))
        QTimer.singleShot(2000, lambda:self.setStyleSheet("background: #333; color: #eee;"))


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
            self.main = MainWindow()
            self.main.show()

            self.close()

        counter += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = Splash()
    sys.exit(app.exec_())
