from resource_manager import theResourceManager
from em_parse import read_from_xml_node


class PrototypeInfo(object):
    def __init__(self):
        self.bIsUpdating = 1
        self.bVisibleInEncyclopedia = 1
        self.bApplyAffixes = 1
        self.bIsAbstract = 0

        self.className = ""
        self.prototypeName = ""
        self.prototypeId = -1
        self.resourceId = -1
        self.price = 0
        self.parentPrototypeName = ""
        self.protoClassObject = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        self.prototypeName = read_from_xml_node(xmlNode, "???")
        self.className = read_from_xml_node(xmlNode, "Class")
        strResType = read_from_xml_node(xmlNode, "ResourceType")
        self.resourceId = theResourceManager.GetResourceId(strResType)
