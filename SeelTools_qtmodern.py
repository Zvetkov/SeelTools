import sys
import os
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide2.QtGui import QIcon, QKeySequence, QRadialGradient, QBrush, QColor
from PySide2.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QWidget, QListWidget,
                               QTextEdit, QTabWidget, QMenu, QAction,
                               QMainWindow, QMessageBox, QDockWidget,
                               QListWidgetItem, QTreeWidget, QTreeWidgetItem)
from qtmodern import styles, windows
import parsing_module

from logger import logger

APP_NAME = "SeelTools"
APP_VERSION = 0.01


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = MainWindow(app)
    mw = windows.ModernWindow(window)
    mw.show()
    app.exec_()


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        # setting up application skin and display properties

        self.app = app
        styles.dark(self.app.instance())
        self.createIcons()

        logger.debug("setupMainTabWidget")
        self.setupMainTabWidget()
        self.setCentralWidget(self.mainTabWidget)
        self.createActions()
        self.setupTopMenu()
        self.setupToolBar()
        self.setupDockWindows()
        self.setupStatusBar()
        self.setWindowTitle('{} v{}'.format(APP_NAME, APP_VERSION))

    def setupTopMenu(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openGameFolderAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        self.editMenu = QMenu("&Edit", self)
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)

        self.viewMenu = QMenu("&View", self)

        self.settingsMenu = QMenu("&Settings", self)
        self.settingsMenu.addAction(self.propertiesAction)

        self.aboutMenu = QMenu("&About", self)
        self.aboutMenu.addAction(self.aboutAction)
        self.aboutMenu.addAction(self.aboutQtAction)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.settingsMenu)
        self.menuBar().addMenu(self.aboutMenu)

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
        logger.debug("Undo pressed")
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

    def setupDockWindows(self):
        self.objectViewDock = QDockWidget("Object Viewer")
        self.objectViewDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.objectExploreDock = QDockWidget("Object Explorer")
        self.objectExploreDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.objectProps = QListWidget(self.objectViewDock)
        self.objectProps.addItems((
            "Name:          Торговец Серго (Buyer)",
            "Prototype:     NPC",
            "Parent:        Бар ''Долгий путь'' (TheTown_Bar)",
            "Properties: ",
            "Belong/Faction: Союз фермеров (1008)",
            "Model:         r4_man",
            "Skin:          1",
            "Model Config:  44",
            "Spoken Count:  0"))
        self.objectViewDock.setWidget(self.objectProps)
        self.addDockWidget(Qt.RightDockWidgetArea, self.objectViewDock)
        self.viewMenu.addAction(self.objectViewDock.toggleViewAction())

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
        else:
            styles.light(self.app.instance())
            QAction.setIcon(self.openGameFolderAction, self.fileDirIconDark)
            QAction.setIcon(self.undoAction, self.undoIconDark)
            QAction.setIcon(self.redoAction, self.redoIconDark)
            QAction.setIcon(self.propertiesAction, self.gearIconDark)
            QAction.setIcon(self.saveAction, self.saveIconDark)

    def setupMainTabWidget(self):
        self.mainTabWidget = QTabWidget()
        self.mainTabWidget.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.Preferred)

        tab1 = QWidget()
        # listWidget = QListWidget()
        treeWidget = QTreeWidget()
        treeWidget.setColumnCount(3)
        treeWidget.setHeaderLabels(["Name", "Prototype", "Parent"])

        server = parsing_module.get_server()
        prototypes = server.thePrototypeManager.prototypes
        prototype_types = set([prototype.className for prototype in prototypes])
        for prototype_type in prototype_types:
            tree_object = QTreeWidgetItem(treeWidget)
            tree_object.setText(0, "...")
            tree_object.setText(1, prototype_type)
            tree_object.setText(2, "-")
            # newItem = QListWidgetItemPrototypeInfo(self.redoIconLight, item.prototypeName)
            tree_object.setToolTip(0, "Some tool tip")
            tree_object.setStatusTip(0, "Woohoo, this is status tip!")
            tree_object.setWhatsThis(0, "This is dummy string")
            # listWidget.addItem(newItem)
            addPrototypesOfTypeToTreeItem(treeWidget, tree_object, prototypes, prototype_type)
            tree_object.DontShowIndicatorWhenChildless
            treeWidget.addTopLevelItem(tree_object)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(treeWidget)
        # tab1hbox.addWidget(listWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()
        textEdit.setPlainText(("Name:          Торговец Серго (Buyer)\n"
                               "Prototype:     NPC\n"
                               "Parent:        Бар ''Долгий путь'' (TheTown_Bar)\n"
                               "Properties: \n"
                               "Belong/Faction: Союз фермеров (1008)\n"
                               "Model:         r4_man\n"
                               "Skin:          1\n"
                               "Model Config:  44\n"
                               "Spoken Count:  0\n"))

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.mainTabWidget.addTab(tab1, "&List Explorer")
        self.mainTabWidget.addTab(tab2, "Code &Editor")


def addPrototypesOfTypeToTreeItem(tree_widget: QTreeWidget, parent: QListWidgetItem, prototypes, prot_type):
    prots_of_type = [prot for prot in prototypes if prot.className == prot_type]
    for prot in prots_of_type:
        tree_object = QTreeWidgetItem()
        tree_object.setText(0, prot.prototypeName)
        tree_object.setText(1, prot_type)
        if hasattr(prot, 'parent'):
            tree_object.setText(2, f"{prot.parent.className}: {prot.parent.prototypeName}")
        else:
            tree_object.setText(2, "-")
        tree_object.setToolTip(0, "Some tool tip")
        tree_object.setStatusTip(0, "Woohoo, this is status tip!")
        tree_object.setWhatsThis(0, "This is dummy string")
        parent.addChild(tree_object)


class StringListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(StringListModel, self).__init__(parent)

        self.stringList = []
        self.stringCount = 0

    def rowCount(self, parent=QModelIndex()):
        return len(self.stringList)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= self.stringCount or index.row() < 0:
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.stringList[index.row()]

        if role == Qt.BackgroundRole:
            batch = (index.row() // 100) % 2
            if batch == 0:
                return QApplication.palette().base()

            return QApplication.palette().alternativeBase()
        return None

    def headerData(self, section: int, orientation,
                   role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return f"Column {section}"
        else:
            return f"Row {section}"

    def flags(self, index: QModelIndex):
        if index.isValid():
            return QAbstractListModel.flags(index) | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value, role: Qt.EditRole):
        if index.isValid and role == Qt.EditRole:
            self.stringList[index.row()] = str(value)
            self.dataChanged.emit(index, index)

    def insertRows(self, position, rows, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.stringList.insert(position, "")

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.stringList.removeAt(position)

        self.endRemoveRows()
        return True


class QTreeWidgetItemPrototypeInfo(QTreeWidgetItem):
    def __init__(self):
        QTreeWidgetItem.__init__(self)

    def mouseDoubleClickEvent(self, event):
        logger.debug("MouseDoubleClickEvent")


if __name__ == "__main__":
    sys.exit(main())
