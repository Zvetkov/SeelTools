from warnings import warn
from lxml import objectify

from resource_manager import theResourceManager
from em_parse import read_from_xml_node, parse_str_to_bool


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
            self.bVisibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode, "VisibleInEncyclopedia"))
            self.bApplyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes"))
            if hasattr(xmlNode, "Price"):
                self.price = read_from_xml_node(xmlNode, "Price")
            self.bIsAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract"))
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype")
        else:
            warn(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")


class AffixGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        self.affixDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        for affix in xmlNode["Affix"].iterchildren():
            self.affixDescriptions.append(read_from_xml_node(affix, "AffixName"))

    def GenerateAffixesForObj(self, obj, desiredNumAffixed):
        pass

    # class AffixDescription(object):
    #     def __init__(self):
    #         self.affixName = ""
    # trying to replace with simple dict ??? why do we need this class?

    class ModificationInfo(object):
        def __init__(self):
            self.pass_id = 0
            # raise NotImplementedError('Not implemmented ModificationInfo initiatilization') 


class somethingPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass
