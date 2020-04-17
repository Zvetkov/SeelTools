from lxml import objectify
from os import path

from logger import logger

from em_parse import xml_to_objfy, read_from_xml_node, log_comment
from constants import STATUS_SUCCESS
from prototype_info import PrototypeInfo, thePrototypeInfoClassDict


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
                    return 1
            else:
                logger.error(f"Prototype {prototype_info.prototypeName} "
                             f"of class {prototype_info.className} was not loaded!")
                return 0
        else:
            logger.error("Invalid class name: <{class_name}>!")
            return 0
