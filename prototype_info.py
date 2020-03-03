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


class AffixGroup(object):
    def __init__(self):
        self.theAffixManager = AffixManager()
        self.affixGroupId = -1
        self.name = ""
        self.order = -1
        self.targetResourceId = -1
        self.affixIds = []

    def AddAffix(affix: Affix):
        if self.theAffixManager.GetAffixByNameAndResource(self, affix.name, self.targetResourceId) != -1:
            warn(f"Affix {affix.name} already exists for resource!")
        else:
            pass


class AffixManager(object):
    def __init__(self):
        self.affixGroups = []
        self.affixes = []
        self.affix_map = {}
        self.affixGroup_map = {}

    def GetAffixById(self, affixId: int):
        if affixId < 0 or affixId > len(self.affixes):
            return 0  # ??? maybe replace with None
        else:
            return self.affixes[affixId]

    def GetAffixGroupById(self, affixId):
        if affixId < 0 or affixId > len(self.affixes):
            return 0  # ??? maybe replace with None
        else:
            return self.affixGroups[affixId]

    def GetAffixGroupIdByName(self, affixName):
        if not self.affixGroups:
            return -1
        else:
            return self.affixGroup_map[affixName]

    def GetAffixGroupsByResourceId(self, resourceId):
        if not self.affixGroups:
            return -1
        else:
            if resourceId != -1:
                valid_afx_gr = [afx_gr for afx_gr in self.affixGroups
                                if theResourceManager.ResourceIsKindOf(resourceId, afx_gr.targetResourceId)]
                if len(valid_afx_gr) > 1:
                    warn(f"There is more than one available affixGroup for reource id {resourceId}!")
                return valid_afx_gr[0]

            else:
                raise ValueError(f"Invalid resourceId given, can't return AffixGroup!")

    def GetAffixIdByNameAndResource(self, affixName, resourceId):
        if resourceId == -1 or not self.affixes:
            return -1
        else:
            afx = self.affix_map[affixName]
            if theResourceManager.ResourceIsKindOf(resourceId, afx.AffixGroup.targerResourceId):
                return afx.affixId
            else:
                raise TypeError(f"Affix {affixName} has unexpected resource type {afx.AffixGroup.targerResourceId}, "
                                f"compared to given resourceId {resourceId}")

    def GetNumAffixes(self):
        return len(self.affixes)


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


class Affix(object):
    pass


class somethingPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass
