from utilities.parse import check_mono_xml_node, xml_to_objfy, read_from_xml_node, child_from_xml_node
from utilities.log import logger

from gameobjects.object_classes import Object
from level.level import Level


class ObjContainer(Object):
    def __init__(self) -> None:
        Object.__init__(self)
        # InnerContainer logic
        self.nameToIdMap = []
        self.objectsFullNames = {}
        # self.objIdsToUpdate = []
        # self.objIdsToNotUpdate = []
        # self.objIdsToRemove = []

    def LoadObjectNamesFromXML(self, level: Level) -> None:
        xmlFile = level.objectsFullNames
        if "data/" not in xmlFile or "data\\" not in xmlFile:
            xmlFile = level.levelPath + level.objectsFullNames

        xmlNode = xml_to_objfy(xmlFile)
        if xmlNode.tag != "ObjectNames":
            raise ValueError("ObjectNames file is not valid, should contain root tag 'ObjectNames'")
        check_mono_xml_node(xmlNode, "Object", ignore_comments=True)
        object_nodes = child_from_xml_node(xmlNode, "Object")
        if object_nodes is not None:
            for object_name_node in object_nodes:
                object_name = read_from_xml_node(object_name_node, "Name")
                object_full_name = read_from_xml_node(object_name_node, "FullName")
                if self.objectsFullNames.get(object_name) is not None:
                    logger.warning(f"FullName for object with name '{object_name}' already specified!")
                self.objectsFullNames[object_name] = object_full_name
