import logging
from warnings import warn
from lxml import objectify

from resource_manager import ResourceManager
from engine_config import theEngineConfig

from em_parse import xml_to_objfy, read_from_xml_node, child_from_xml_node, check_mono_xml_node


class ModificationInfo(object):
    def __init__(self, mod: str):
        mod_params = mod.split()
        self.propertyName = mod_params[0]
        self.lowCoeff = int(mod_params[1]) * 0.01  # percentage points
        self.highCoeff = int(mod_params[2]) * 0.01  # percentage points

    def ApplyToObj(self, a2: int, affix, obj):
        raise NotImplementedError("ToDo: implement ModificatonInfo ApplyToObj!")


class Affix(object):
    def __init__(self, affixGroup):
        self.affixGroup = affixGroup
        self.affixId = -1
        self.name = ""
        self.modifications = []

    def LoadFromXML(self, xmlFile, xmlNode):
        self.name = read_from_xml_node(xmlNode, "Name")
        forms_quantity = 1
        is_prefix = self.affixGroup.affixType == 0
        if is_prefix:
            forms_quantity = theEngineConfig.loc_forms_quantity
        if forms_quantity > 0:
            for localization_index in range(forms_quantity):
                localized_string = theStringManager.GetStringByStringId(self.name, localization_index)
                logging.log(f"localized string {localized_string} found for {self.name}")
        modifications_str = read_from_xml_node(xmlNode, "modifications")
        modifications_str = modifications_str.split(";")
        for mod in modifications_str:
            modification = ModificationInfo(mod.strip())
            self.modifications.append(modification)

    def ApplyToObj(self, obj):
        if self.modifications:
            for mod in self.modifications:
                if not self.ModificationInfo.ApplyToObj(self.modifications, self, obj):
                    return 0
            return 1

    def GetLocalizedName(self, localizationIndex):
        local_name = theStringManager.GetStringByStringId(localizationIndex, 0)
        return local_name


class AffixGroup(object):
    def __init__(self, affixManager):
        self.theAffixManager = affixManager  # ??? should it be here?
        self.affixGroupId = -1
        self.name = ""
        self.order = -1
        self.targetResourceId = -1
        self.affixIds = []

    def LoadFromXML(self, xmlFile, xmlNode):
        localizationPath = theEngineConfig.loc_forms_quantity
        self.name = read_from_xml_node(xmlNode, "Name")
        self.order = int(read_from_xml_node(xmlNode, "order"))
        check_mono_xml_node(xmlNode, "Affix")
        for affix_node in xmlNode["Affix"]:
            affix = Affix(self)
            affix.LoadFromXML(xmlFile, affix_node)


class AffixManager(object):
    def __init__(self, theResourceManager: ResourceManager):
        self.affixGroups = []
        self.affixes = []
        self.affix_map = {}
        self.affixGroup_map = {}
        self.theResourceManager = theResourceManager

    def LoadFromXML(self, fileName):
        xmlFile = xml_to_objfy(fileName)
        if xmlFile.tag == "Affixes":

            for resource_node in xmlFile.iterchildren():
                if resource_node.tag == "ForResource":
                    resource_name = read_from_xml_node(resource_node, "Name")
                    resource_id = self.theResourceManager.GetResourceId(resource_name)
                    if resource_id == -1:
                        warn(f"Error loading affixes: invalid resource name: {resource_name}")
                    else:
                        prefixes = child_from_xml_node(resource_node, "Prefixes")
                        suffixes = child_from_xml_node(resource_node, "Suffixes")

                        if prefixes is not None:
                            check_mono_xml_node(prefixes, "AffixGroup")
                            for affix_group_node in child_from_xml_node(prefixes, "AffixGroup"):
                                affix_group = AffixGroup(self)
                                affix_group.affixType = 0
                                affix_group.LoadFromXML(xmlFile, affix_group_node)

                                affix_groups_list_size = len(self.affixGroups)
                                affix_group.affixGroupId = affix_groups_list_size
                                affix_group.targetResourceId = resource_id

                                self.affixGroups.append(affix_group)
                        if suffixes is not None:
                            check_mono_xml_node(suffixes, "AffixGroup")
                            for affix_group_node in child_from_xml_node(suffixes, "AffixGroup"):
                                affix_group = AffixGroup(self)
                                affix_group.affixType = 1
                                affix_group.LoadFromXML(xmlFile, affix_group_node)

                                affix_groups_list_size = len(self.affixGroups)
                                affix_group.affixGroupId = affix_groups_list_size
                                affix_group.targetResourceId = resource_id

                                self.affixGroups.append(affix_group)
                else:
                    warn(f"Unexpected node with name {resource_node.tag} found in Affixes xml!")
        else:
            raise NameError("Affixes file should contain root Affixes tag")

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
                                if self.theResourceManager.ResourceIsKindOf(resourceId, afx_gr.targetResourceId)]
                if len(valid_afx_gr) > 1:
                    warn(f"There is more than one available affixGroup for resource id {resourceId}!")
                return valid_afx_gr[0]

            else:
                raise ValueError(f"Invalid resourceId given, can't return AffixGroup!")

    def GetAffixIdByNameAndResource(self, affixName, resourceId):
        if resourceId == -1 or not self.affixes:
            return -1
        else:
            afx = self.affix_map[affixName]
            if self.theResourceManager.ResourceIsKindOf(resourceId, afx.AffixGroup.targerResourceId):
                return afx.affixId
            else:
                raise TypeError(f"Affix {affixName} has unexpected resource type {afx.AffixGroup.targerResourceId}, "
                                f"compared to given resourceId {resourceId}")

    def GetNumAffixes(self):
        return len(self.affixes)

    def AddAffix(self, affix: Affix):
        if self.GetAffixByNameAndResource(self, affix.name, self.targetResourceId) != -1:
            warn(f"Affix {affix.name} already exists for resource!")
        else:
            self.affixes.append(affix)


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

    def LoadFromXML(self):
        pass


theStringManager = StringManager()
theStringManager.LoadFromXML()
