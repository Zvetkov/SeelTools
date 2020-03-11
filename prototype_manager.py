from lxml import objectify
from os import path

from logger import logger

from em_parse import xml_to_objfy, read_from_xml_node
from prototype_info import PrototypeInfo


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

    def InternalGetPrototypeInfo(self, prototypeName):
        return self.prototypesMap.get(prototypeName)  # might be best to completely replace method with direct dict get

    def LoadFromXMLFile(self, fileName):
        self.loadingLock += 1
        self.LoadGameObjectsFolderFromXML(fileName)
        self.loadingLock -= 1
        for prototype in self.prototypes:
            prototype.PostLoad()

    def LoadGameObjectsFolderFromXML(self, fileName):
        xmlFileNode = xml_to_objfy(fileName)
        if xmlFileNode.tag != "Prototypes":
            raise AttributeError(f"Given file {xmlFileNode.base} should contain <Prototypes> tag!")
        directory = path.dirname(fileName)
        self.LoadFromFolder(fileName, xmlFileNode, directory)

    def LoadFromFolder(self, xmlFile, xmlNode, directory):
        for prototype_node in xmlNode.iterchildren():
            is_folder_node = prototype_node.tag == "Folder"
            if not is_folder_node:
                self.ReadNewPrototype(directory, prototype_node)
            else:
                file_attrib = read_from_xml_node(prototype_node, "File", do_not_warn=True)
                if file_attrib is not None:
                    self.LoadGameObjectsFolderFromXML(file_attrib)
                else:
                    self.LoadFromFolder(xmlFile, prototype_node, directory)

    def ReadNewPrototype(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        class_name = read_from_xml_node(xmlNode, "Class")
        prototype_info = self.theServer.CreatePrototypeInfoByClassName(class_name)
        if prototype_info:
            prototype_info.className = class_name
            parent_prot_name = read_from_xml_node(xmlNode, "ParentPrototype")
            if parent_prot_name is not None:
                parent_prot_info = self.InternalGetPrototypeInfo(parent_prot_name)
                dummy = PrototypeInfo()
                if parent_prot_info is None:
                    logger.error(f"Parent prototype for {class_name} is not loade! Expected parent: {parent_prot_name}")
                    parent_prot_info = dummy
                prototype_info.CopyFrom(parent_prot_info)
            prototypes_length = len(self.prototypes)
            prototype_info.prototypeId = prototypes_length
            if prototype_info.LoadFromXML(prototype_info, xmlFile, xmlNode):
                if self.prototypeNamesToIds.get(prototype_info.prototypeName) is not None:
                    logger.critical(f"Duplicate prototype in game objects: {prototype_info.prototypeName}")
                    raise AttributeError("Duplicate prototype, critical error!")
                else:
                    self.prototypeNamesToIds[prototype_info.prototypeName] = prototype_info.prototypeId
                    self.prototypes.append(prototype_info)
                    self.prototypesMap[prototype_info.prototypeName] = prototype_info
                    return 1
            else:
                logger.error(f"Prototype {prototype_info.prototypeName} "
                             f"of class {prototype_info.className} was not loaded!")
                return 0
        else:
            logger.error("Invalid class name: <{class_name}>!")
            return 0
