import os
import sys

from pathlib import Path

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

sys.path.append('..')  # temp workaround to allow running application from this entry point instead on __maim__.py

from seeltools.qtmodern import styles, windows
from seeltools.server import server_init
from seeltools.utilities.log import logger
from seeltools.utilities.value_classes import AnnotatedValue
from seeltools.utilities.game_path import WORKING_DIRECTORY

APP_NAME = "SeelTools"
APP_VERSION = 0.02


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    mw = windows.ModernWindow(window)
    mw.show()
    mw.resize(1024, 720)
    app.exec_()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        # setting up application skin and display properties
        self.app = app
        styles.dark(self.app.instance())
        self.createIcons()

        logger.debug("setupMainTabWidget")
        self.setupMainTabWidget()

        self.setCentralWidget(self.main_tab_widget)

        self.createActions()

        self.setupTopMenu()

        self.setupToolBar()

        self.setupDockWindows()

        self.setupStatusBar()

        self.setWindowTitle('{} v{}'.format(APP_NAME, APP_VERSION))

    def setupTopMenu(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openGameFolderAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        self.editMenu = QtWidgets.QMenu("&Edit", self)
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)

        self.viewMenu = QtWidgets.QMenu("&View", self)

        self.settingsMenu = QtWidgets.QMenu("&Settings", self)
        self.settingsMenu.addAction(self.propertiesAction)

        self.aboutMenu = QtWidgets.QMenu("&About", self)
        self.aboutMenu.addAction(self.aboutAction)
        self.aboutMenu.addAction(self.aboutQtAction)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.settingsMenu)
        self.menuBar().addMenu(self.aboutMenu)

    def createActions(self):
        self.openGameFolderAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('folder-open', self.fileDirIconLight),
                                                      "&Open Game Folder...", self, shortcut="Ctrl+O",
                                                      statusTip="Open folder where Ex Machina is installed",
                                                      triggered=self.openGameFolder)

        self.saveAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('document-save', self.saveIconLight), "&Save...",
                                            self, shortcut=QtGui.QKeySequence.Save,
                                            statusTip="Save all changes", triggered=self.save)

        self.quitAction = QtWidgets.QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application",
                                            triggered=self.closeApplication)

        self.undoAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('edit-undo', self.undoIconLight), "&Undo", self,
                                            shortcut=QtGui.QKeySequence.Undo, statusTip="Undo the last editing action",
                                            triggered=self.undo)

        self.redoAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('edit-redo', self.redoIconLight), "&Redo", self,
                                            shortcut=QtGui.QKeySequence.Redo, statusTip="Redo the last editing action",
                                            triggered=self.redo)

        self.propertiesAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('application-properties', self.gearIconLight),
                                                  "&Properties", self, shortcut="Ctrl+P",
                                                  statusTip="Application properties", triggered=self.properties)

        self.aboutAction = QtWidgets.QAction("&About SeelTools", self, statusTip="Show the SeelTools About box",
                                             triggered=self.about)

        self.aboutQtAction = QtWidgets.QAction("About &Qt", self, statusTip="Show the Qt library's About box",
                                               triggered=QtWidgets.QApplication.instance().aboutQt)

    def openGameFolder(self):
        pass

    def save(self):
        logger.info(f"Save stared")
        server_init.theServer.save_all()
        logger.info(f"Saved finished")

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
        QtWidgets.QMessageBox.about(self, "About SeelTools",
                                    "Placeholder <b>SeelTools</b> description "
                                    "something something")

    def setupToolBar(self):
        self.fileToolBar = self.addToolBar("File&Edit")
        self.fileToolBar.addAction(self.openGameFolderAction)
        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.undoAction)
        self.fileToolBar.addAction(self.redoAction)

        self.optionsToolBar = self.addToolBar("Options")
        self.useDarkMode = QtWidgets.QCheckBox("Use &dark mode")
        self.useDarkMode.toggled.connect(self.toggleDarkMode)
        self.useDarkMode.setToolTip("Toggle light and dark interface theme")
        self.useDarkMode.setChecked(True)
        self.optionsToolBar.addWidget(self.useDarkMode)

    def setupStatusBar(self):
        self.statusBar().showMessage("Ready")

    def setupDockWindows(self):
        self.objectViewDock = QtWidgets.QDockWidget("QuickLook")
        self.objectViewDock.setMinimumSize(205, 210)
        self.objectViewDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.prot_grid = QtWidgets.QVBoxLayout()

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        inner_frame = QtWidgets.QFrame(scroll_area)
        inner_frame.setLayout(self.prot_grid)

        scroll_area.setWidget(inner_frame)

        quicklook_promt = QtWidgets.QLabel(get_locale_string("QuickLookPromt"))
        self.prot_grid.addWidget(quicklook_promt)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.prot_grid.addItem(spacer)

        self.objectViewDock.setWidget(scroll_area)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.objectViewDock)
        self.viewMenu.addAction(self.objectViewDock.toggleViewAction())

    def createIcons(self):
        module_path = Path(os.path.abspath(__file__))
        ui_path = os.path.join(module_path.parent, 'ui')
        self.fileDirIconLight = QtGui.QIcon(os.path.join(ui_path, 'icons/filedir_white.svg'))
        self.fileDirIconDark = QtGui.QIcon(os.path.join(ui_path, 'icons/filedir.svg'))
        self.gearIconLight = QtGui.QIcon(os.path.join(ui_path, 'icons/gear_white.svg'))
        self.gearIconDark = QtGui.QIcon(os.path.join(ui_path, 'icons/gear.svg'))
        self.undoIconLight = QtGui.QIcon(os.path.join(ui_path, 'icons/undo_white.svg'))
        self.undoIconDark = QtGui.QIcon(os.path.join(ui_path, 'icons/undo.svg'))
        self.redoIconLight = QtGui.QIcon(os.path.join(ui_path, 'icons/redo_white.svg'))
        self.redoIconDark = QtGui.QIcon(os.path.join(ui_path, 'icons/redo.svg'))
        self.saveIconLight = QtGui.QIcon(os.path.join(ui_path, 'icons/save_white.svg'))
        self.saveIconDark = QtGui.QIcon(os.path.join(ui_path, 'icons/save.svg'))

    def toggleDarkMode(self):
        if self.useDarkMode.isChecked():
            styles.dark(self.app.instance())
            QtWidgets.QAction.setIcon(self.openGameFolderAction, self.fileDirIconLight)
            QtWidgets.QAction.setIcon(self.undoAction, self.undoIconLight)
            QtWidgets.QAction.setIcon(self.redoAction, self.redoIconLight)
            QtWidgets.QAction.setIcon(self.propertiesAction, self.gearIconLight)
            QtWidgets.QAction.setIcon(self.saveAction, self.saveIconLight)
        else:
            styles.light(self.app.instance())
            QtWidgets.QAction.setIcon(self.openGameFolderAction, self.fileDirIconDark)
            QtWidgets.QAction.setIcon(self.undoAction, self.undoIconDark)
            QtWidgets.QAction.setIcon(self.redoAction, self.redoIconDark)
            QtWidgets.QAction.setIcon(self.propertiesAction, self.gearIconDark)
            QtWidgets.QAction.setIcon(self.saveAction, self.saveIconDark)

    def setupMainTabWidget(self):
        self.main_tab_widget = QtWidgets.QTabWidget()
        self.main_tab_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        # filtering and sorting model
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setRecursiveFilteringEnabled(True)

        self.load_prototypes_to_source_model()

        # tree view to display in tab
        tab_prot_explorer = QtWidgets.QWidget()
        self.tree_prot_explorer = QtWidgets.QTreeView()
        self.tree_prot_explorer.setModel(self.proxy_model)
        self.tree_prot_explorer.setSortingEnabled(True)
        self.tree_prot_explorer.setColumnWidth(0, 180)
        self.tree_prot_explorer.setColumnWidth(1, 150)

        # case sensitivity setting and filter "search box"
        self.sort_case_sens_check_box = QtWidgets.QCheckBox("Case sensitive sorting")

        self.filter_case_sens_check_box = QtWidgets.QCheckBox("Case sensitive filter")

        self.filter_pattern_line_edit = QtWidgets.QLineEdit()
        self.filter_pattern_label = QtWidgets.QLabel("&Filter pattern:")
        self.filter_pattern_label.setBuddy(self.filter_pattern_line_edit)

        # checkbox to choose search input syntax
        self.filter_syntax_combo_box = QtWidgets.QComboBox()
        self.filter_syntax_combo_box.addItem("Regular expression", QtCore.QRegExp.RegExp)
        self.filter_syntax_combo_box.addItem("Wildcard", QtCore.QRegExp.Wildcard)
        self.filter_syntax_combo_box.addItem("Fixed string", QtCore.QRegExp.FixedString)

        self.filter_syntax_label = QtWidgets.QLabel("Filter &syntax:")
        self.filter_syntax_label.setBuddy(self.filter_syntax_combo_box)

        # filter column setting
        self.filter_column_combo_box = QtWidgets.QComboBox()
        self.filter_column_combo_box.addItem("Name")
        self.filter_column_combo_box.addItem("PrototypeType")
        self.filter_column_combo_box.addItem("Parent")

        self.filter_column_label = QtWidgets.QLabel("Filter &column:")
        self.filter_column_label.setBuddy(self.filter_column_combo_box)

        # connecting setting controls to actions
        self.sort_case_sens_check_box.toggled.connect(self.sort_changed)
        self.filter_case_sens_check_box.toggled.connect(self.filter_reg_exp_changed)
        self.filter_pattern_line_edit.textChanged.connect(self.filter_reg_exp_changed)
        self.filter_syntax_combo_box.currentIndexChanged.connect(self.filter_reg_exp_changed)
        self.filter_column_combo_box.currentIndexChanged.connect(self.filter_column_changed)

        selection_model = self.tree_prot_explorer.selectionModel()
        selection_model.selectionChanged.connect(self.prototype_explorer_item_selected)

        proxy_layout = QtWidgets.QGridLayout()
        proxy_layout.addWidget(self.tree_prot_explorer, 0, 0, 1, 3)
        proxy_layout.addWidget(self.filter_pattern_label, 1, 0)
        proxy_layout.addWidget(self.filter_pattern_line_edit, 1, 1, 1, 2)
        proxy_layout.addWidget(self.filter_syntax_label, 2, 0)
        proxy_layout.addWidget(self.filter_syntax_combo_box, 2, 1, 1, 2)
        proxy_layout.addWidget(self.filter_column_label, 3, 0)
        proxy_layout.addWidget(self.filter_column_combo_box, 3, 1, 1, 2)
        proxy_layout.addWidget(self.filter_case_sens_check_box, 4, 0, 1, 2)
        proxy_layout.addWidget(self.sort_case_sens_check_box, 4, 2)

        tab_prot_explorer.setLayout(proxy_layout)
        self.tree_prot_explorer.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.main_tab_widget.addTab(tab_prot_explorer, "&Prototype Explorer")

    def filter_reg_exp_changed(self):
        syntax_nr = self.filter_syntax_combo_box.itemData(self.filter_syntax_combo_box.currentIndex())
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)

        if self.filter_case_sens_check_box.isChecked():
            case_sensitivity = QtCore.Qt.CaseSensitive
        else:
            case_sensitivity = QtCore.Qt.CaseInsensitive

        regExp = QtCore.QRegExp(self.filter_pattern_line_edit.text(),
                                case_sensitivity, syntax)
        self.proxy_model.setFilterRegExp(regExp)

    def filter_column_changed(self):
        self.proxy_model.setFilterKeyColumn(self.filter_column_combo_box.currentIndex())

    def sort_changed(self):
        if self.sort_case_sens_check_box.isChecked():
            case_sensitivity = QtCore.Qt.CaseSensitive
        else:
            case_sensitivity = QtCore.Qt.CaseInsensitive

        self.proxy_model.setSortCaseSensitivity(case_sensitivity)

    def load_prototypes_to_source_model(self):
        source_model = create_prototype_model(self)
        self.proxy_model.setSourceModel(source_model)

    def prototype_explorer_item_selected(self, prototypeName):
        item_name, item_class = self.get_selected_item_name_and_class()

        if item_class is None:
            clear_layout(self.prot_grid)
            folder_label = QtWidgets.QLabel(item_name)
            string_folder_descr = get_locale_string("FolderDescription")
            folder_descr = QtWidgets.QTextEdit()
            folder_descr.setText(f"{string_folder_descr} {item_name}")
            # folder_descr.setMinimumHeight()
            folder_label.setBuddy(folder_descr)
            self.prot_grid.addWidget(folder_label)
            self.prot_grid.addWidget(folder_descr)
            spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.prot_grid.addItem(spacer)
        else:
            self.load_prot_to_quicklook(item_name)

        # font_metrics = self.prototype_name.fontMetrics()
        # text_width = font_metrics.boundingRect(display_text).width()

        # logger.info(text_width)
        # if text_width < 90:
        #     self.prototype_name.resize(100, 20)
        # else:
        #     self.prototype_name.resize(text_width + 10, 20)

    def get_selected_item_name_and_class(self):
        indexes = self.tree_prot_explorer.selectedIndexes()
        logger.debug(f"Indexes: {indexes}")
        prot_name = self.tree_prot_explorer.model().data(indexes[0])
        prot_class = self.tree_prot_explorer.model().data(indexes[1])
        if prot_class is None:
            return prot_name, None
        else:
            return prot_name, prot_class

    def load_prot_to_quicklook(self, prot_name):
        clear_layout(self.prot_grid)

        server = server_init.theServer
        prototype_manager = server.thePrototypeManager
        prot = prototype_manager.InternalGetPrototypeInfo(prot_name)
        prot_attribs = vars(prot)
        for attrib in prot_attribs.values():
            if isinstance(attrib, AnnotatedValue):
                attrib_label = QtWidgets.QLabel(get_display_name(prot, attrib))
                attrib_value = QtWidgets.QLineEdit()
                attrib_value.setText(str(attrib.value))
                attrib_value.setFixedHeight(20)
                if attrib.value == attrib.default_value:
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(253, 174, 37))
                    attrib_value.setPalette(palette)
                attrib_value.setReadOnly(True)
                attrib_value.setToolTip(get_description(prot, attrib))
                attrib_label.setBuddy(attrib_value)
                attrib_label.setFixedHeight(20)
                self.prot_grid.addWidget(attrib_label)
                self.prot_grid.addWidget(attrib_value)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.prot_grid.addItem(spacer)


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def get_display_name(object, attrib):
    # placeholder
    return attrib.name


def get_description(object, attrib):
    # placeholder
    return f"Dummy description {attrib.name}"


def get_locale_string(string):
    # placeholder
    return string


def create_prototype_model(parent):
    model = QtGui.QStandardItemModel(0, 3, parent)

    model.setHeaderData(0, QtCore.Qt.Horizontal, "Prototype Name")
    model.setHeaderData(1, QtCore.Qt.Horizontal, "Class")
    model.setHeaderData(2, QtCore.Qt.Horizontal, "Parent Name")

    server = server_init.theServer
    prototypes = server.thePrototypeManager.prototypes
    prototype_types = set([prototype.className.value for prototype in prototypes])

    for prototype_type in prototype_types:
        prots_of_type = [prot for prot in prototypes if prot.className.value == prototype_type]
        add_prototype_folder(parent, model, prototype_type, prots_of_type)

    return model


def add_prototype_folder(window, model, folder_name, child_prototypes):
    folder_item = QtGui.QStandardItem(QtGui.QIcon(window.fileDirIconLight), folder_name)
    folder_item.checkState()
    folder_item.setEditable(False)
    for child in child_prototypes:
        prot_name = child.prototypeName.value
        if hasattr(child, 'parent'):
            parent_prot = f"{child.parent.className.value}: {child.parent.prototypeName.value}"
        else:
            parent_prot = ""
        add_prototype(window, folder_item, prot_name, folder_name, parent_prot)
    model.appendRow(folder_item)


def add_prototype(window, parent_item: QtGui.QStandardItemModel, prot_name, prot_class, parent_name):
    prototype_name = QtGui.QStandardItem(QtGui.QIcon(window.gearIconLight), prot_name)
    prototype_name.setEditable(False)
    prototype_class = QtGui.QStandardItem(prot_class)
    prototype_class.setEditable(False)
    prototype_parent = QtGui.QStandardItem(parent_name)
    prototype_parent.setEditable(False)
    parent_item.appendRow([prototype_name, prototype_class, prototype_parent])


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setMargin(margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton,
                                                                QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton,
                                                                QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


if __name__ == "__main__":
    sys.exit(main())
