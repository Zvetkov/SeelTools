from lxml import objectify
from os import path

from seeltools.utilities.log import logger

from seeltools.utilities.parse import xml_to_objfy, read_from_xml_node, log_comment
from seeltools.utilities.constants import STATUS_SUCCESS
from seeltools.gameobjects.prototype_info import PrototypeInfo, thePrototypeInfoClassDict


from seeltools.utilities.game_path import WORKING_DIRECTORY
from seeltools.utilities.file_ops import save_to_file
from lxml import etree


class PrototypeManager(object):
    def __init__(self, server):
        # self.Clear()
        self.theServer = server
        self.prototypes = []
        self.prototypesMap = {}
        self.prototypeNamesToIds = {}  # int: int
        self.prototypeFullNamesLocalizedForms = {}  # unsgn_int:unsgn_int
        self.prototypeFullNames = {}  # str:str
        self.loadingLock = 0
        self.prototypeClasses = []

    def InternalGetPrototypeInfo(self, prototypeName):
        return self.prototypesMap.get(prototypeName)  # might be best to completely replace method with direct dict get

    def IsPrototypeOf(prototype_info: PrototypeInfo, class_name):
        logger.info(f"Checking if {prototype_info.className} is of {class_name}")
        return type(prototype_info) == thePrototypeInfoClassDict[class_name]

    def GetPrototypeId(self, prototypeName):
        prot_id = -1
        prot_id_from_loaded = self.prototypeNamesToIds.get(prototypeName)
        if prot_id_from_loaded is None and prototypeName:
            logger.error(f"No prototype with name '{prototypeName}' registred by PrototypeManager!")
        else:
            prot_id = prot_id_from_loaded
        return prot_id

    def LoadFromXMLFile(self, fileName):
        self.loadingLock += 1
        self.LoadGameObjectsFolderFromXML(fileName)
        self.loadingLock -= 1
        for prototype in self.prototypes:
            logger.debug(f"PostLoad for prototype {prototype.prototypeName}")
            prototype.PostLoad(self)

    def LoadGameObjectsFolderFromXML(self, fileName):
        xmlFileNode = xml_to_objfy(fileName)
        if xmlFileNode.tag != "Prototypes":
            raise AttributeError(f"Given file {xmlFileNode.base} should contain <Prototypes> tag!")
        directory = path.dirname(fileName)
        self.LoadFromFolder(fileName, xmlFileNode, directory)

    def LoadFromFolder(self, xmlFile, xmlNode, directory):
        for prototype_node in xmlNode.iterchildren():
            is_folder_node = prototype_node.tag == "Folder"
            if prototype_node.tag != "comment":
                if not is_folder_node:
                    self.ReadNewPrototype(directory, prototype_node)
                else:
                    file_attrib = read_from_xml_node(prototype_node, "File", do_not_warn=True)
                    if file_attrib is not None:
                        self.LoadGameObjectsFolderFromXML(f"{directory}/{file_attrib}")
                    else:
                        self.LoadFromFolder(xmlFile, prototype_node, directory)
            else:
                log_comment(prototype_node, xmlNode)

    def ReadNewPrototype(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        class_name = read_from_xml_node(xmlNode, "Class")
        logger.debug(f"Loading {class_name} prototype from {xmlNode.base}")
        prototype_info = self.theServer.CreatePrototypeInfoByClassName(class_name)(self.theServer)
        if prototype_info:
            prototype_info.className = class_name
            parent_prot_name = read_from_xml_node(xmlNode, "ParentPrototype", do_not_warn=True)
            if parent_prot_name is not None:
                parent_prot_info = self.InternalGetPrototypeInfo(parent_prot_name)
                dummy = PrototypeInfo(self.theServer)
                if parent_prot_info is None:
                    logger.error(f"Parent prototype of {class_name} is not loaded! Expected parent: {parent_prot_name}")
                    parent_prot_info = dummy
                prototype_info.CopyFrom(parent_prot_info)
            prototypes_length = len(self.prototypes)
            prototype_info.prototypeId = prototypes_length
            if prototype_info.LoadFromXML(xmlFile, xmlNode) == STATUS_SUCCESS:
                if self.prototypeNamesToIds.get(prototype_info.prototypeName) is not None:
                    logger.critical(f"Duplicate prototype in game objects: {prototype_info.prototypeName}")
                    raise AttributeError("Duplicate prototype, critical error!")
                else:
                    self.prototypeNamesToIds[prototype_info.prototypeName] = prototype_info.prototypeId
                    self.prototypes.append(prototype_info)
                    self.prototypesMap[prototype_info.prototypeName] = prototype_info
                    if prototype_info.className not in self.prototypeClasses:
                        self.prototypeClasses.append(prototype_info.className)
                    return 1
            else:
                logger.error(f"Prototype {prototype_info.prototypeName} "
                             f"of class {prototype_info.className} was not loaded!")
                return 0
        else:
            logger.error("Invalid class name: <{class_name}>!")
            return 0

    def save_to_xml(self, gameObjectsFilePath):
        full_path = path.join(WORKING_DIRECTORY, gameObjectsFilePath)
        full_path = self.tempFuncRenameFile(full_path)
        folder_path = path.split(full_path)[0]

        self.generateGameObjectsFile(full_path)
        for prototype_class in self.prototypeClasses:
            self.generateSpecificPrototypesFile(prototype_class, folder_path)

    def generateGameObjectsFile(self, fullPath):
        prototypesTree = etree.Element("Prototypes")

        for prototype_class in self.prototypeClasses:
            folder = etree.Element("Folder")
            folder.set("Name", prototype_class)
            folder.set("Path", 'new_%s.xml' % prototype_class)
            prototypesTree.append(folder)

        save_to_file(prototypesTree, fullPath)

    def generateSpecificPrototypesFile(self, className, pathToFolder):
        filename = 'new_%s.xml' % className
        fullPath = path.join(pathToFolder, filename)

        prototypesTree = etree.Element("Prototypes")
        filteredPrototypes = [x for x in self.prototypes if x.className == className]
        filteredPrototypes.sort(key=lambda x: x.prototypeName, reverse=False)
        for prototype in filteredPrototypes:
            prototypesTree.append(prototype.get_etree_prototype())
        save_to_file(prototypesTree, fullPath)

    def tempFuncRenameFile(self, docfile):
        pathN, filename = path.split(docfile)
        filename = path.splitext(filename)[0]
        newfilename = 'new_%s.xml' % filename
        newpath = path.join(pathN, newfilename)
        return newpath
