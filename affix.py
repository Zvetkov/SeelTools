from lxml import objectify

from logger import logger

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

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        self.name = read_from_xml_node(xmlNode, "Name")
        forms_quantity = 1
        is_prefix = self.affixGroup.affixType == 0
        if is_prefix:
            forms_quantity = theEngineConfig.loc_forms_quantity
        if forms_quantity > 0:
            default_localized_string = self.GetLocalizedName(self.name)
            logger.debug(f"Default localized string {default_localized_string} found for {self.name}")
            for localization_index in range(forms_quantity):
                localized_string = self.GetLocalizedName(self.name, str(localization_index))
                logger.debug(f"localized string {localized_string} found for {self.name}")
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

    def GetLocalizedName(self, name, localizationIndex: str = ""):
        local_name = theWndStation.GetStringByStringId(name, localizationIndex)
        return local_name


class AffixGroup(object):
    def __init__(self, affix_manager):
        self.theAffixManager = affix_manager
        self.affixGroupId = -1
        self.name = ""
        self.order = -1
        self.targetResourceId = -1
        self.affixIds = []

    def LoadFromXML(self, xmlFile, xmlNode):
        self.name = read_from_xml_node(xmlNode, "Name")
        self.order = int(read_from_xml_node(xmlNode, "order"))
        check_mono_xml_node(xmlNode, "Affix")
        for affix_node in xmlNode["Affix"]:
            affix = Affix(self)
            affix.LoadFromXML(xmlFile, affix_node)
            self.affixIds.append(affix)
            self.theAffixManager.AddAffix(affix)


class AffixManager(object):
    def __init__(self, theResourceManager: ResourceManager):
        self.affixGroups = []
        self.affixes = []
        self.affix_map = {}
        self.theResourceManager = theResourceManager

    def LoadFromXML(self, fileName):
        xmlFile = xml_to_objfy(fileName)
        if xmlFile.tag == "Affixes":
            check_mono_xml_node(xmlFile, "ForResource")
            for resource_node in xmlFile["ForResource"]:
                resource_name = read_from_xml_node(resource_node, "Name")
                resource_id = self.theResourceManager.GetResourceId(resource_name)
                if resource_id == -1:
                    logger.warning(f"Error loading affixes: invalid resource name: {resource_name}")
                else:
                    prefixes = child_from_xml_node(resource_node, "Prefixes", do_not_warn=True)
                    suffixes = child_from_xml_node(resource_node, "Suffixes", do_not_warn=True)

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
                    if suffixes is None and prefixes is None:
                        logger.warning(f"Affixes node for resource {resource_name} has no Prefixes and no Suffixes!")
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

    # def GetAffixGroupIdByName(self, affixName):
    #     if not self.affixGroups:
    #         return -1
    #     else:
    #         return self.affixGroup_map[affixName]

    def GetAffixGroupsByResourceId(self, resourceId):
        if not self.affixGroups:
            return -1
        else:
            if resourceId != -1:
                valid_afx_gr = [afx_gr for afx_gr in self.affixGroups
                                if self.theResourceManager.ResourceIsKindOf(resourceId, afx_gr.targetResourceId)]
                if len(valid_afx_gr) > 1:
                    logger.warning(f"There is more than one available affixGroup for resource id {resourceId}!")
                return valid_afx_gr[0]

            else:
                raise ValueError(f"Invalid resourceId given, can't return AffixGroup!")

    def GetAffixIdByNameAndResource(self, affixName, resourceId):
        if resourceId == -1 or not self.affixes:
            return -1
        else:
            afx = self.affix_map[affixName]
            if self.theResourceManager.ResourceIsKindOf(resourceId, afx.affixGroup.targetResourceId):
                return afx.affixId
            else:
                raise TypeError(f"Affix {affixName} has unexpected resource type {afx.affixGroup.targetResourceId}, "
                                f"compared to given resourceId {resourceId}")

    def GetNumAffixes(self):
        return len(self.affixes)

    def AddAffix(self, affix: Affix):
        if self.GetAffixIdByNameAndResource(affix.name, affix.affixGroup.targetResourceId) != -1:
            logger.warning(f"Affix {affix.name} already exists for resource!")
        else:
            affix.affixId = len(self.affixes)
            self.affixes.append(affix)
            self.affix_map[affix.name] = affix


class WndStation(object):
    '''UI manager containing GfxServer and UI strings repository '''
    def __init__(self):
        self.strings = {}
        self.allWindows = {}
        self.allWindowsById = {}

    def GetStringByStringId(self, str_id, localizationIndex: str = ''):
        if len(localizationIndex) > 0:
            if localizationIndex in ["0", "1"]:
                localizationIndex = f"_localizedform_{localizationIndex}"
            else:
                logger.warning("Invalid localization index, only empty, 0 and 1 available")

        string = self.strings.get(f"{str_id}{localizationIndex}")
        if string is not None:
            return string
        else:
            logger.warning(f"String name given is not in String Dictionary: {str_id}")

    def Create(self, stringsName: str, schemaName: str = ""):
        # self.theGfxServer.Create()
        # self.theGfxServer.SetSchema(schemaName)
        self.CreateDefaultStrings()
        self.LoadStrings(stringsName)
        return 1

    def CreateDefaultStrings(self):
        self.strings["ok"] = "Ok"
        self.strings["cancel"] = "Cancel"
        self.strings["yes"] = "Yes"
        self.strings["no"] = "No"
        self.strings["error"] = "Error"

    def LoadStrings(self, stringsName: str):
        xmlFile = xml_to_objfy(stringsName)
        if xmlFile.tag == "resource":
            check_mono_xml_node(xmlFile, "string")
            for xml_node in child_from_xml_node(xmlFile, "string"):
                id_attr = read_from_xml_node(xml_node, "id")
                value_attr = read_from_xml_node(xml_node, "value")
                self.strings[id_attr] = value_attr


# class GfxServer(object):
#     def __init__(self):
#         raise NotImplementedError()

#     def Create(self):
#         raise NotImplementedError()

#     def SetSchema(self):
#         raise NotImplementedError()


theWndStation = WndStation()
theWndStation.Create(theEngineConfig.ui_edit_strings)
theWndStation.LoadStrings(theEngineConfig.affixes_strings_path)
