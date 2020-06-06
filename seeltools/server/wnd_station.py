from seeltools.utilities.engine_config import theEngineConfig
from seeltools.utilities.log import logger
from seeltools.utilities.parse import xml_to_objfy, read_from_xml_node, child_from_xml_node, check_mono_xml_node


class WndStation(object):
    '''UI manager containing GfxServer and UI strings repository '''
    def __init__(self):
        self.strings = {}
        self.allWindows = {}
        self.allWindowsById = {}

    def GetStringByStringId(self, str_id, localizationIndex: str = ''):
        '''Get localizied string by id, where id is the service name'''
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
theWndStation.LoadStrings(theEngineConfig.affixes_strings)
