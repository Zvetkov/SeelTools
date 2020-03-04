from warnings import warn
from lxml import objectify

from resource_manager import theResourceManager
from em_parse import read_from_xml_node, parse_str_to_bool


class Relationship(object):
    def __init__(self):
        self.toleranceMap  # ??? can this be useful?
        self.tolerance = 0
        self.playerDefaultTolerance = 0
        self.minID = 0
        self.maxId = -1
        self.defaultTolerance = 1
        self.toleranceList = {"enemy", "neutral", "ally", "own"}

        self.toleranceList["enemy"] = {"name": "",
                                       "tolerance": 1}
        self.toleranceList["neutral"] = {"name": "",
                                         "tolerance": 2}
        self.toleranceList["ally"] = {"name": "",
                                      "tolerance": 3}
        self.toleranceList["own"] = {"name": "",
                                     "tolerance": 4}


    def LoadFromXmlFile(self, saveType, xmlFile):
        '''Replacing LoadFromXmlFile'''
        pass

    def LoadDefaultFromXmlFile(self, saveType, xmlFile):
        '''Replacing LoadDefaultFromXmlFile'''
        pass

    def LoadFromXML(self, xmlFile, xmlNode, default: bool = True):
        self.tolerance = {}
        self.minID = int(xmlNode.attrib["MinPlayerID"])
        self.maxID = int(xmlNode.attrib["MaxPlayerID"])
        self.playerDefaultTolerance = xmlNode.attrib["DefaultTolerance"]

        if self.minID <= self.maxID:
            if self.maxID - self.minID + 1 > 1000:
                self.maxID = self.minID + 1001
                warn(f"There can't be more that 1001 belongs, for example 1000-2001 is valid. Reseting max value to be {self.maxID}")
                belongs_number = self.maxID - self.minID
                tolerance_range = range(self.minID, self.maxID)
                for tolerance in tolerance_range:
                    format_type = xmlNode.attrib.get("FormatType")
                    if format_type is not None:
                        raise NotImplementedError("Can't work with saves yet, do not load from currentmap.xml")
                        # format_type = int(format_type)
                        # if format_type == 1:
                        #     self.LoadFormat(xmlFile, xmlNode, 1)
                    else:
                        self.LoadFormat(xmlFile, xmlNode, 0)
        else:
            raise ValueError("Relationship MinPlayerID should be less than MaxPlayerID")

    def LoadFormat(self, xmlFile, xmlNode):
        for rel in xmlNode.iterchildren():
            if rel.tag != "set":
                warn(f"Invalid tag {rel.tag} in Relationship map {xmlNode.base}")
            else:
                tolerance = self.GetToleranceByName(rel.attrib["tolerance"])
                self.SetTolerance(rel.attrib["forwhom"], rel.attrib["who"], tolerance)

    def GetToleranceByName(self, tol_name):
        tol = self.toleranceMap.get(tol_name)
        if tol is not None:
            return tol
        else:
            return self.playerDefaultTolerance

    def SetTolerance(self, for_whom, who, tolerance):
        invalid_belongs = []
        min_id = self.minID
        max_id = self.maxID
        for_whom = [int(belong) for belong in for_whom.split()]
        invalid_belongs.extend([bel for bel in for_whom if bel > self.maxID or bel < self.minID])
        who = [int(belong) for belong in who.split()]
        invalid_belongs.extend([bel for bel in who if bel > self.maxID or bel < self.minID])
        if invalid_belongs:
            for belong in invalid_belongs:
                warn(f"Invalid belong {belong} listed in relationship map! "
                     f"Belong should be between {self.minID} and {self.maxID}")

        for who_belong in who:
            for whom_belong in for_whom:
                if who_belong != who_belong:
                    # ??? what the fuck is this?
                    self.tolerance[whom_belong + (who_belong - min_id) * (max_id - min_id + 1) - min_id] = tolerance
                    self.tolerance[who_belong + (whom_belong - min_id) * (max_id - min_id + 1) - min_id] = tolerance
                else:
                    warn(f"Belong {who_belong} is in both 'forwhom' and 'who' attribs of set!")


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

    def AddAffix(self, affix: Affix):
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

    def LoadFromXML(self):
        pass

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
    def __init__(self, affixGroup):
        self.affixGroup = affixGroup
        self.affixId = -1
        self.name = ""
        self.modifications = []

    def ApplyToObj(self, obj):
        if self.modifications:
            for mod in self.modifications:
                if not ModificationInfo.ApplyToObj(self.modifications, self, obj):
                    return 0
            return 1

    def GetLocalizedName(self, localizationIndex):
        local_name = theLocalizationManager.GetStringByStringId(localizationIndex, 0)
        return local_name

    class ModificationInfo(object):
        def __init__(self):
            pass


class somethingPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass


class StringManager(object):
    '''Replacement for m3d::ui::WndStation and m3d::CStrHash'''
    def __init__(self):
        self.string_dict = {}

    def GetStringByStringId(self, str_id, localizationIndex: str = ""):
        if len(localizationIndex) > 0:
            if localizationIndex in ["0", "1"]:
                localizationIndex = f"_localizedform_{localizationIndex}"
            else:
                warn("Invalid localization index, only empty, 0 and 1 available")

        string = self.string_dict.get(f"{str_id}{localizationIndex}")
        if string is not None:
            return string
        else:
            warn(f"String name given is not in String Dictionary: {string}")
