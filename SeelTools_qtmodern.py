import sys
from PySide2.QtCore import Qt, QMetaObject, Signal, Slot
from PySide2.QtGui import QPalette, QColor, QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                               QDial, QDialog, QGridLayout, QGroupBox, QLabel,
                               QDateTimeEdit, QLineEdit, QProgressBar, QSlider,
                               QPushButton, QRadioButton, QScrollBar, QSpinBox,
                               QSizePolicy, QStyleFactory, QWidget, QTextEdit,
                               QTabWidget, QTableWidget, QVBoxLayout, QToolTip,
                               QMenu, QMenuBar, QMainWindow, QToolBar, QMessageBox,
                               QWidget, QToolButton, QAction)
from qtmodern import styles
from qtmodern import windows

app_name = "SeelTools"
app_version = 0.01


def main():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    mw = windows.ModernWindow(window)
    mw.show()
    app.exec_()


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        # setting up application skin and display properties
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app = app
        styles.dark(self.app.instance())
        self.setupMainTabWidget()
        self.setCentralWidget(self.mainTabWidget)
        self.createIcons()
        self.createActions()
        self.setupTopMenu()
        self.setupToolBar()
        self.setupStatusBar()
        self.setWindowTitle('{} v{}'.format(app_name, app_version))

    def setupTopMenu(self):
        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openGameFolderAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)

        editMenu = QMenu("&Edit", self)
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)

        settingsMenu = QMenu("&Settings", self)
        settingsMenu.addAction(self.propertiesAction)

        aboutMenu = QMenu("&About", self)
        aboutMenu.addAction(self.aboutAction)
        aboutMenu.addAction(self.aboutQtAction)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(settingsMenu)
        self.menuBar().addMenu(aboutMenu)

    def createActions(self):
        self.openGameFolderAction = QAction(QIcon.fromTheme('folder-open', self.fileDirIconLight),
                                            "&Open Game Folder...", self, shortcut="Ctrl+O",
                                            statusTip="Open folder where Ex Machina is installed",
                                            triggered=self.openGameFolder)

        self.saveAction = QAction(QIcon.fromTheme('document-save', self.saveIconLight), "&Save...", self,
                                  shortcut=QKeySequence.Save,
                                  statusTip="Save all changes", triggered=self.save)

        self.quitAction = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application",
                                  triggered=self.closeApplication)

        self.undoAction = QAction(QIcon.fromTheme('edit-undo', self.undoIconLight), "&Undo", self,
                                  shortcut=QKeySequence.Undo, statusTip="Undo the last editing action",
                                  triggered=self.undo)

        self.redoAction = QAction(QIcon.fromTheme('edit-redo', self.redoIconLight), "&Redo", self,
                                  shortcut=QKeySequence.Redo, statusTip="Redo the last editing action",
                                  triggered=self.redo)

        self.propertiesAction = QAction(QIcon.fromTheme('application-properties', self.gearIconLight),
                                        "&Properties", self, shortcut="Ctrl+P",
                                        statusTip="Application properties", triggered=self.properties)

        self.aboutAction = QAction("&About SeelTools", self, statusTip="Show the SeelTools About box",
                                   triggered=self.about)

        self.aboutQtAction = QAction("About &Qt", self, statusTip="Show the Qt library's About box",
                                     triggered=QApplication.instance().aboutQt)

    def openGameFolder(self):
        pass

    def save(self):
        pass

    def closeApplication(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def properties(self):
        pass

    def about(self):
        QMessageBox.about(self, "About SeelTools",
                          "Placeholder <b>SeelTools</b> description "
                          "something something")

    def setupToolBar(self):
        self.fileToolBar = self.addToolBar("File&Edit")
        self.fileToolBar.addAction(self.openGameFolderAction)
        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.undoAction)
        self.fileToolBar.addAction(self.redoAction)

        self.optionsToolBar = self.addToolBar("Options")
        self.useDarkMode = QCheckBox("Use &dark mode")
        self.useDarkMode.toggled.connect(self.toggleDarkMode)
        self.useDarkMode.setToolTip("Toggle light and dark interface theme")
        self.useDarkMode.setChecked(True)
        self.optionsToolBar.addWidget(self.useDarkMode)

    def setupStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createIcons(self):
        self.fileDirIconLight = QIcon('./icons/filedir_white.svg')
        self.fileDirIconDark = QIcon('./icons/filedir.svg')
        self.gearIconLight = QIcon('./icons/gear_white.svg')
        self.gearIconDark = QIcon('./icons/gear.svg')
        self.undoIconLight = QIcon('./icons/undo_white.svg')
        self.undoIconDark = QIcon('./icons/undo.svg')
        self.redoIconLight = QIcon('./icons/redo_white.svg')
        self.redoIconDark = QIcon('./icons/redo.svg')
        self.saveIconLight = QIcon('./icons/save_white.svg')
        self.saveIconDark = QIcon('./icons/save.svg')

    def toggleDarkMode(self):
        if self.useDarkMode.isChecked():
            styles.dark(self.app.instance())
            QAction.setIcon(self.openGameFolderAction, self.fileDirIconLight)
            QAction.setIcon(self.undoAction, self.undoIconLight)
            QAction.setIcon(self.redoAction, self.redoIconLight)
            QAction.setIcon(self.propertiesAction, self.gearIconLight)
            QAction.setIcon(self.saveAction, self.saveIconLight)

            print("dark")
        else:
            styles.light(self.app.instance())
            QAction.setIcon(self.openGameFolderAction, self.fileDirIconDark)
            QAction.setIcon(self.undoAction, self.undoIconDark)
            QAction.setIcon(self.redoAction, self.redoIconDark)
            QAction.setIcon(self.propertiesAction, self.gearIconDark)
            QAction.setIcon(self.saveAction, self.saveIconDark)

            print("light")

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


if __name__ == "__main__":
    sys.exit(main())
