from warnings import warn
from resource_manager import ResourceManager
from em_parse import read_from_xml_node, parse_str_to_bool

theResourceManager = ResourceManager()

class PrototypeInfo(object):
    def __init__(self):
        self.className = ""
        self.prototypeName = ""
        self.prototypeId = -1
        self.resourceId = -1
        self.bIsUpdating = 1
        self.bVisibleInEncyclopedia = 1
        self.bApplyAffixes = 1
        self.price = 0
        self.bIsAbstract = 0
        self.parentPrototypeName = ""
        self.protoClassObject = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        if xmlNode.tag == "Prototype":
            self.prototypeName = read_from_xml_node(xmlNode, "Name")
            self.className = read_from_xml_node(xmlNode, "Class")
            strResType = read_from_xml_node(xmlNode, "ResourceType")
            self.resourceId = theResourceManager.GetResourceId(strResType)
            if self.resourceId == -1:
                raise(f"Error: invalid ResourceType: {strResType} for prototype {self.prototypeName}")
            self.protoClassObject = ""  # ??? (m3d::Class *)v5;
            self.bIsUpdating = parse_str_to_bool(read_from_xml_node(xmlNode, "IsUpdating"))
        else:
            warn(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")
