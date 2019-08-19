import sys
from PySide2.QtCore import QDateTime, Qt, QTimer
from PySide2.QtGui import QPalette, QColor
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                               QDial, QDialog, QGridLayout, QGroupBox, QLabel,
                               QDateTimeEdit,QLineEdit, QProgressBar, QSlider,
                               QPushButton, QRadioButton, QScrollBar, QSpinBox,
                               QSizePolicy, QStyleFactory, QWidget, QTextEdit,
                               QTabWidget, QTableWidget, QVBoxLayout, QToolTip,
                               QMenu, QMenuBar, QMainWindow)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()

        self.dark_palette = QApplication.palette()

        self.useStylePaletteCheckBox = QCheckBox("&Use dark mode")
        self.useStylePaletteCheckBox.setChecked(True)

        self.createMainTabWidget()

        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)

        topLayout = QHBoxLayout()
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.mainTabWidget, 0, 0, 2, 2)
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("SeelTools")

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.changePalette()

    def setupFileMenu(self):
        fileMenu = QMenu("&File", self)
        self.menuBar().addMenu(fileMenu)
        fileMenu.addAction("&Open Game Folder...", self.openDialog, "Ctrl+O")
        fileMenu.addAction("&Save...", self.saveDialog, "Ctrl+N")
        fileMenu.addAction("E&xit", self.closeDialog, "Ctrl+Q")

    def openDialog(self):
        pass

    def saveDialog(self):
        pass

    def closeDialog(self):
        pass
        

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            dark_palette = self.dark_palette
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
            QApplication.setPalette(dark_palette)
            # styleSheet = "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
            # QApplication.setStyleSheet(styleSheet)
        else:
            QApplication.setPalette(QApplication.style().standardPalette())


    def createMainTabWidget(self):
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