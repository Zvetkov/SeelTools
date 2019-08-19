import sys
from PySide2.QtCore import Qt  # , QDateTime, QTimer
from PySide2.QtGui import QPalette, QColor
import lib.qtmodern.styles
import lib.qtmodern.windows
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                               QDial, QDialog, QGridLayout, QGroupBox, QLabel,
                               QDateTimeEdit, QLineEdit, QProgressBar, QSlider,
                               QPushButton, QRadioButton, QScrollBar, QSpinBox,
                               QSizePolicy, QStyleFactory, QWidget, QTextEdit,
                               QTabWidget, QTableWidget, QVBoxLayout, QToolTip,
                               QMenu, QMenuBar, QMainWindow, QToolBar, QMessageBox)
app_name = "SeelTools"
app_version = 0.01


def main():
    app = QApplication(sys.argv)
    lib.qtmodern.styles.dark(app)
    window = MainWindow(app)
    mw = lib.qtmodern.windows.ModernWindow(window)
    mw.show()
    window.show()
    app.exec_()
    lib.qtmodern.styles


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        # setting up application skin and display properties
        #QApplication.setStyle(QStyleFactory.create('Fusion'))
        #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app = app
        self.setupTopMenu()
        self.setupToolbar()
        self.setupMainTabWidget()
        self.setCentralWidget(self.mainTabWidget)



        #self.toggleDarkMode()
        #self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowTitle('{} v{}'.format(app_name, app_version))
        #self.setWindowFlags(Qt.WindowTitleHint)

    def setupTopMenu(self):
        fileMenu = QMenu("&File", self)
        settingsMenu = QMenu("&Edit", self)
        aboutMenu = QMenu("&About", self)
        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(settingsMenu)
        self.menuBar().addMenu(aboutMenu)
        fileMenu.addAction("&Open Game Folder...", self.dummyAction, "Ctrl+O")
        fileMenu.addAction("&Save...", self.dummyAction, "Ctrl+S")
        fileMenu.addAction("Q&uit", self.dummyAction, "Ctrl+Q")
        settingsMenu.addAction("&Undo", self.dummyAction, "Ctrl+Z")
        settingsMenu.addAction("&Redo", self.dummyAction, "Shift+Ctrl+Z")
        settingsMenu.addAction("&Properties", self.dummyAction, "Ctrl+P")
        aboutMenu.addAction("&About SeelTools", self.about)
        aboutMenu.addAction("About &Qt", QApplication.instance().aboutQt)

    def dummyAction(self):
        pass

    def about(self):
        QMessageBox.about(self, "About SeelTools",
                          "Placeholder <b>SeelTools</b> description "
                          "something something")

    def setupToolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.usedarkMode = QCheckBox("Use &dark mode")
        self.usedarkMode.setChecked(True)
        self.usedarkMode.toggled.connect(self.toggleDarkMode)
        self.usedarkMode.setToolTip("Toggle light and dark interface theme")
        toolbar.addWidget(self.usedarkMode)

    def setupMainTabWidget(self):
        self.mainTabWidget = QTabWidget()
        self.mainTabWidget.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.Preferred)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.mainTabWidget.addTab(tab1, "&Table")
        self.mainTabWidget.addTab(tab2, "Text &Edit")
        self.setCentralWidget(self.mainTabWidget)

    def toggleDarkMode(self):
        if (self.usedarkMode.isChecked()):
            dark_palette = QApplication.palette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(255, 165, 0))
            dark_palette.setColor(QPalette.Highlight, QColor(255, 165, 0))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            self.app.setPalette(dark_palette)
            styleSheet = ("QToolTip { color: #FFAC14; background-color: #191919; border: 1px solid black; }")
            self.app.setStyleSheet(styleSheet)
        else:
            self.app.setPalette(QApplication.style().standardPalette())
            self.app.setStyleSheet("")


if __name__ == "__main__":
    sys.exit(main())
