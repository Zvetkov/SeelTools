from qtmodern import styles, windows, resources
from server import server_init

from utilities.log import logger
from utilities.value_classes import AnnotatedValue, DisplayType
from utilities.ui_data_sources import DisplayTypeDataSource

# from gameobjects.prototype_info import thePrototypeInfoClassDict

import os
import sys

from pathlib import Path

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

sys.path.append("..")  # temp workaround to allow running application from this entry point instead on __maim__.py


APP_NAME = "SeelTools"
APP_VERSION = 0.02


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    mw = windows.ModernWindow(window)

    mw.resize(1024, 720)
    mw.move(QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
            - mw.rect().center())

    mw.show()
    app.exec()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        # setting up application skin and display properties
        self.app = app
        styles._apply_base_theme(self.app.instance())
        styles.dark(self.app.instance())
        self.createIcons()

        logger.debug("setupMainTabWidget")
        self.setupMainTabWidget()

        self.setCentralWidget(self.main_tab_widget)

        self.createActions()

        self.setupTopMenu()

        self.setupToolBar()

        self.setupQuickLook()

        # self.setupPrototypeEditor()

        self.setupStatusBar()

        self.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))

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
        self.openGameFolderAction = QtGui.QAction(QtGui.QIcon.fromTheme("folder-open", self.fileDirIconLight),
                                                  "&Open Game Folder...", self, shortcut="Ctrl+O",
                                                  statusTip="Open folder where Ex Machina is installed",
                                                  triggered=self.openGameFolder)

        self.saveAction = QtGui.QAction(QtGui.QIcon.fromTheme("document-save", self.saveIconLight), "&Save...",
                                        self, shortcut=QtGui.QKeySequence.Save,
                                        statusTip="Save all changes", triggered=self.save)

        self.quitAction = QtGui.QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application",
                                        triggered=self.closeApplication)

        self.undoAction = QtGui.QAction(QtGui.QIcon.fromTheme("edit-undo", self.undoIconLight), "&Undo", self,
                                        shortcut=QtGui.QKeySequence.Undo, statusTip="Undo the last editing action",
                                        triggered=self.undo)

        self.redoAction = QtGui.QAction(QtGui.QIcon.fromTheme("edit-redo", self.redoIconLight), "&Redo", self,
                                        shortcut=QtGui.QKeySequence.Redo, statusTip="Redo the last editing action",
                                        triggered=self.redo)

        self.propertiesAction = QtGui.QAction(QtGui.QIcon.fromTheme("application-properties", self.gearIconLight),
                                              "&Properties", self, shortcut="Ctrl+P",
                                              statusTip="Application properties", triggered=self.properties)

        self.aboutAction = QtGui.QAction("&About SeelTools", self, statusTip="Show the SeelTools About box",
                                         triggered=self.about)

        self.aboutQtAction = QtGui.QAction("About &Qt", self, statusTip="Show the Qt library's About box",
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
        self.useDarkMode.setChecked(True)
        self.useDarkMode.stateChanged.connect(self.toggleDarkMode)
        self.useDarkMode.setToolTip("Toggle light and dark interface theme")
        self.optionsToolBar.addWidget(self.useDarkMode)

    def setupStatusBar(self):
        self.statusBar().showMessage("Ready")

    def setupQuickLook(self):
        self.objectViewDock = QtWidgets.QDockWidget(get_locale_string("QuickLook"))
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

    # def setupPrototypeEditor(self):
    #     self.prototypeEditorDock = QtWidgets.QDockWidget(get_locale_string("PrototypeEditor"))
    #     self.prototypeEditorDock.setMinimumSize(205, 210)
    #     self.prototypeEditorDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

    #     self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.prototypeEditorDock)
    #     self.viewMenu.addAction(self.prototypeEditorDock.toggleViewAction())

    def createIcons(self):
        module_path = Path(os.path.abspath(__file__))
        ui_path = os.path.join(module_path.parent, "ui")
        self.fileDirIconLight = QtGui.QIcon(os.path.join(ui_path, "icons/filedir_white.svg"))
        self.fileDirIconDark = QtGui.QIcon(os.path.join(ui_path, "icons/filedir.svg"))
        self.gearIconLight = QtGui.QIcon(os.path.join(ui_path, "icons/gear_white.svg"))
        self.gearIconDark = QtGui.QIcon(os.path.join(ui_path, "icons/gear.svg"))
        self.undoIconLight = QtGui.QIcon(os.path.join(ui_path, "icons/undo_white.svg"))
        self.undoIconDark = QtGui.QIcon(os.path.join(ui_path, "icons/undo.svg"))
        self.redoIconLight = QtGui.QIcon(os.path.join(ui_path, "icons/redo_white.svg"))
        self.redoIconDark = QtGui.QIcon(os.path.join(ui_path, "icons/redo.svg"))
        self.saveIconLight = QtGui.QIcon(os.path.join(ui_path, "icons/save_white.svg"))
        self.saveIconDark = QtGui.QIcon(os.path.join(ui_path, "icons/save.svg"))

    def toggleDarkMode(self):
        if self.useDarkMode.isChecked():
            styles.dark(self.app.instance())
            QtGui.QAction.setIcon(self.openGameFolderAction, self.fileDirIconLight)
            QtGui.QAction.setIcon(self.undoAction, self.undoIconLight)
            QtGui.QAction.setIcon(self.redoAction, self.redoIconLight)
            QtGui.QAction.setIcon(self.propertiesAction, self.gearIconLight)
            QtGui.QAction.setIcon(self.saveAction, self.saveIconLight)
        else:
            styles.light(self.app.instance())
            QtGui.QAction.setIcon(self.openGameFolderAction, self.fileDirIconDark)
            QtGui.QAction.setIcon(self.undoAction, self.undoIconDark)
            QtGui.QAction.setIcon(self.redoAction, self.redoIconDark)
            QtGui.QAction.setIcon(self.propertiesAction, self.gearIconDark)
            QtGui.QAction.setIcon(self.saveAction, self.saveIconDark)

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
        self.filter_syntax_combo_box.addItem("Regular expression", QtCore.QRegularExpression)
        self.filter_syntax_combo_box.addItem("Wildcard", QtCore.QRegularExpression.fromWildcard)
        self.filter_syntax_combo_box.addItem("Fixed string", QtCore.QRegularExpression.escape)

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

        self.prot_editor = PrototypeEditor()
        self.tree_prot_explorer.doubleClicked.connect(self.prototype_explorer_item_doubleclicked)

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

    def prototype_explorer_item_doubleclicked(self, prototypeName):
        item_name, item_class = self.get_selected_item_name_and_class()

        if item_class is not None:
            self.load_prot_to_editor(item_name)

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

    def load_prot_to_editor(self, prot_name):
        self.prot_editor.add_tab(prot_name)


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
        if hasattr(child, "parent"):
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


class PrototypeEditor(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.mw = windows.ModernWindow(self)
        self.grid_layout = QtWidgets.QVBoxLayout()
        self.mw.setWindowTitle("Prototype Editor")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)

        self.setLayout(self.grid_layout)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.tab_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.grid_layout.addWidget(self.tab_widget)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(lambda index: self.close_tab(index))

        # prot_editor_layout.addWidget(self.filter_pattern_label, 1, 0)
        # prot_editor_layout.addWidget(self.filter_pattern_line_edit, 1, 1, 1, 2)

        self.opened_prots = {}

    def show(self):
        if not self.isVisible():
            self.mw.show()
            self.setVisible(True)
            self.tab_widget.setVisible(True)
            self.mw.resize(250, 150)
            self.mw.move(QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
                      - self.rect().center())
        else:
            logger.debug("Already visible")

    def add_tab(self, prototype_name):
        logger.info("Adding tab")
        self.show()
        if prototype_name not in self.opened_prots.keys():
            prot_tab_widget = QtWidgets.QWidget()
            prot_tab_layout = QtWidgets.QGridLayout()
            prot_tab_widget.setLayout(prot_tab_layout)

            self.opened_prots[prototype_name] = prot_tab_widget
            self.tab_widget.addTab(prot_tab_widget, prototype_name)
            self.populate_tab(prototype_name)
            tab_index = self.tab_widget.indexOf(prot_tab_widget)
            self.tab_widget.setCurrentIndex(tab_index)

        else:
            logger.info("Prototype already opened")
            prot_tab_widget = self.opened_prots[prototype_name]
            tab_index = self.tab_widget.indexOf(prot_tab_widget)
            self.tab_widget.setCurrentIndex(tab_index)

    def populate_tab(self, prototype_name):
        working_widget = self.opened_prots[prototype_name]
        working_layout = working_widget.layout()
        server = server_init.theServer
        prototype_manager = server.thePrototypeManager
        prot = prototype_manager.InternalGetPrototypeInfo(prototype_name)
        prot_attribs = vars(prot)

        mock1_widget = QtWidgets.QWidget()
        mock1_layout = QtWidgets.QGridLayout()
        mock1_widget.setLayout(mock1_layout)

        mock1_label = QtWidgets.QLabel("Display Name")
        mock1_label.setFixedHeight(20)
        mock1_value = QtWidgets.QLineEdit()
        prot_full_name = server.thePrototypeManager.prototypeFullNames.get(prototype_name)
        if prot_full_name is not None:
            mock1_value.setText(prot_full_name)
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(253, 174, 37))
            mock1_value.setPalette(palette)
            mock1_value.setText("NO_NAME")

        mock1_layout.addWidget(mock1_label, 0, 0, QtCore.Qt.AlignRight)
        mock1_layout.addWidget(mock1_value, 0, 1, QtCore.Qt.AlignLeft)

        mock2_widget = QtWidgets.QWidget()
        mock2_layout = QtWidgets.QGridLayout()
        mock2_widget.setLayout(mock2_layout)

        mock2_label = QtWidgets.QLabel("Description")
        mock2_value = QtWidgets.QTextEdit()
        mock2_value.setText("DescriptionPlaceholder")

        mock2_layout.addWidget(mock2_label, 0, 0, QtCore.Qt.AlignRight)
        mock2_layout.addWidget(mock2_value, 0, 1, QtCore.Qt.AlignLeft)

        working_layout.addWidget(mock1_widget)
        working_layout.addWidget(mock2_widget)

        for attrib in prot_attribs.values():
            if isinstance(attrib, AnnotatedValue):
                attrib_grid = QtWidgets.QWidget()
                attrib_layout = QtWidgets.QGridLayout()
                attrib_grid.setLayout(attrib_layout)

                # attrib_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding,
                #                                       QtWidgets.QSizePolicy.Expanding)
                # attrib_layout.addItem(attrib_spacer)

                attrib_label = QtWidgets.QLabel(get_display_name(prot, attrib))

                # display_type_mapping = {DisplayType.CLASS_NAME: QtWidgets.QComboBox,
                #                         DisplayType.RESOURCE_ID: QtWidgets.QComboBox,
                #                         DisplayType.SKIN_NUM: QtWidgets.QComboBox,
                #                         DisplayType.MODIFICATION_INFO: QtWidgets.QLineEdit,
                #                         DisplayType.VEHICLE_DESCRIPTION: QtWidgets.QLineEdit,
                #                         DisplayType.AFFIX_LIST: QtWidgets.QLineEdit,
                #                         DisplayType.WARES_LIST: QtWidgets.QLineEdit}

                # if display_type_mapping[attrib.display_type] == QtWidgets.QComboBox:
                if attrib.display_type == DisplayType.CLASS_NAME:
                    attrib_value = QtWidgets.QComboBox()
                    attrib_value.addItems(DisplayTypeDataSource[attrib.display_type])
                    attrib_value.setCurrentIndex(attrib_value.findText(attrib.value))
                elif attrib.display_type == DisplayType.RESOURCE_ID:
                    attrib_value = QtWidgets.QComboBox()
                    attrib_value.addItems(server.theResourceManager.resourceMap.keys())
                    if prot.resourceId.value != -1:
                        attrib_value.setCurrentIndex(attrib_value.findText(
                                                     server.theResourceManager.GetResourceName(prot.resourceId.value)))
                    else:
                        attrib_value.setCurrentIndex(attrib_value.findText("[NO RESOURCE]"))
                # TODO: to implement after skin reading from gam files is complete
                # elif attrib.display_type == DisplayType.SKIN_NUM:
                #     attrib_value = QtWidgets.QComboBox()
                #     attrib_value.addItems(server.theResourceManager.resourceMap.keys())
                #     attrib_value.setCurrentIndex(attrib_value.findText(
                #                                  server.theResourceManager.GetResourceName(prot.resourceId.value)))
                elif attrib.display_type == DisplayType.MODIFICATION_INFO:
                    # attrib_value = QtWidgets.QWidget()
                    # attrib_value_layout = QtWidgets.QHBoxLayout()
                    # for mod in attrib.value:
                    #     mod_label = QtWidgets.QLabel(mod.propertyName)
                    #     mod_info = QtWidgets.QLineEdit()
                    #     mod_info.setText(mod.value)
                    #     mod_info.setFixedHeight(20)
                    #     attrib_value_layout.addWidget(mod_label)
                    #     attrib_value_layout.addWidget(mod_info)
                    # attrib_value.setLayout(attrib_value_layout)
                    attrib_value = QtWidgets.QWidget()
                    attrib_value_layout = QtWidgets.QVBoxLayout()

                    for mod_info in attrib.value:
                        mod_info_widget = QtWidgets.QWidget()
                        mod_info_layout = QtWidgets.QHBoxLayout()
                        mod_info_widget.setLayout(mod_info_layout)

                        mod_info_label = QtWidgets.QLabel(mod_info.propertyName)
                        mod_info_value = QtWidgets.QLineEdit()
                        mod_info_value.setText(str(mod_info.value))

                        mod_info_layout.addWidget(mod_info_label)
                        mod_info_layout.addWidget(mod_info_value)

                        attrib_value_layout.addWidget(mod_info_widget)
                        # TODO: create new window for ModificationManager,
                        # it's too complicated to deal with inside PrototypeEditor
                        # See ModificationInfo in prototype_info

                    attrib_value.setLayout(attrib_value_layout)

                elif isinstance(attrib.value, bool):
                    attrib_value = QtWidgets.QCheckBox()
                    if attrib.value:
                        attrib_value.setChecked(True)
                    if attrib.read_only:
                        attrib_value.setDisabled(True)
                else:
                    attrib_value = QtWidgets.QLineEdit()
                    attrib_value.setText(str(attrib.value))
                    attrib_value.setFixedHeight(20)

                if attrib.value == attrib.default_value:
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(253, 174, 37))
                    attrib_value.setPalette(palette)

                attrib_layout.addWidget(attrib_label, 0, 0, QtCore.Qt.AlignRight)
                attrib_layout.addWidget(attrib_value, 0, 1, QtCore.Qt.AlignLeft)

                attrib_value.setToolTip(get_description(prot, attrib))
                attrib_label.setBuddy(attrib_value)
                attrib_label.setFixedHeight(20)

                working_layout.addWidget(attrib_grid)
                # working_layout.addWidget(attrib_label)
                # working_layout.addWidget(attrib_value)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        working_layout.addItem(spacer)

    def close_tab(self, index):
        prot_name = self.tab_widget.tabText(index)
        self.opened_prots.pop(prot_name)
        self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        close_dialog = QtWidgets.QMessageBox()
        reply = close_dialog.question(self,
                                      get_locale_string("close_window_warning_title"),
                                      get_locale_string("close_window_warning_text"))
        if reply == QtWidgets.QMessageBox.Yes:
            for tab_index in reversed(range(self.tab_widget.count())):
                self.close_tab(tab_index)
            event.accept()
        else:
            event.ignore()


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
