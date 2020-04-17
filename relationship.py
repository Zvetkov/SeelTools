from em_parse import read_from_xml_node, xml_to_objfy

from logger import logger


class Relationship(object):
    def __init__(self):
        self.pTolerance = 0
        self.pDefaultTolerance = 0
        self.defaultTolerance = 1
        self.minID = 0
        self.maxID = -1

        self.toleranceMap = {}  # ??? can this be useful?
        self.toleranceMap["enemy"] = {"name": "enemy",
                                      "tolerance": 1}
        self.toleranceMap["neutral"] = {"name": "neutral",
                                        "tolerance": 2}
        self.toleranceMap["ally"] = {"name": "ally",
                                     "tolerance": 3}
        self.toleranceMap["own"] = {"name": "own",
                                    "tolerance": 4}

        self.toleranceList = list(self.toleranceMap.values())

    def LoadFromXML(self, xmlFile, copy_to_default: bool = True):
        xmlNode = xml_to_objfy(xmlFile)
        if xmlNode.tag != "relationship":
            raise ValueError("Relationship XML should contain root tag 'relationship'!")
        formatType = 0
        self.minID = int(read_from_xml_node(xmlNode, "MinPlayerID"))
        self.maxID = int(read_from_xml_node(xmlNode, "MaxPlayerID"))
        default_tolerance_name = read_from_xml_node(xmlNode, "DefaultTolerance")
        self.defaultTolerance = self.GetToleranceByName(default_tolerance_name)

        if self.minID <= self.maxID:
            if self.maxID - self.minID + 1 > 1000:
                self.maxID = self.minID + 1001
                logger.warning(f"Tolerance range can't be more than 1001, for example 1000-2001 range is valid."
                               f"Reseting max value to be {self.maxID}")
            self.pTolerance = {}
            tolerance_range_len = self.maxID - self.minID
            tolerance_id_range = range(0, tolerance_range_len**2)
            for tolerance_id in tolerance_id_range:
                self.pTolerance[tolerance_id] = self.defaultTolerance
            format_type_read = read_from_xml_node(xmlNode, "FormatType", do_not_warn=True)
            if format_type_read is not None:
                formatType = int(format_type_read)
            if formatType != 0:
                if formatType == 1:
                    raise NotImplementedError("Can't work with saves yet, do not load from currentmap.xml")
                    self.LoadFormat(xmlFile, xmlNode, 1)  # ??? do we even need this for format_type 1?
                else:
                    raise ValueError(f"Invalid format type {formatType} for relationship")
            else:
                self.LoadFormat(xmlFile, xmlNode, 0)
        if copy_to_default:
            self.pDefaultTolerance = self.pTolerance
        else:
            raise ValueError("Relationship MinPlayerID should be less than MaxPlayerID")

    def LoadFormat(self, xmlFile, xmlNode, format_type: int = 0):
        for rel in xmlNode.iterchildren():
            if rel.tag != "set":
                logger.warning(f"Invalid tag {rel.tag} in Relationship map {xmlNode.base}")
            else:
                tolerance = self.GetToleranceByName(read_from_xml_node(rel, "tolerance"))
                for_whom = read_from_xml_node(rel, "forwhom")
                who = read_from_xml_node(rel, "who")
                self.SetTolerance(for_whom, who, tolerance)

    def SaveFormat(self, xmlFile, xmlNode, format_type: int = 0):
        raise NotImplementedError("Not imlemented SaveFormat method for Relationship")

    def SaveToXML(self, xmlFile, xmlNode):
        raise NotImplementedError("Not imlemented SaveToXML method for Relationship")

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
                logger.warning(f"Invalid belong {belong} listed in relationship map! "
                               f"Belong should be between {self.minID} and {self.maxID}")

        for who_belong in who:
            for whom_belong in for_whom:
                if whom_belong != who_belong:
                    # strange native way to store belong to belong tolerance mappings
                    self.pTolerance[whom_belong + (who_belong - min_id) * (max_id - min_id + 1) - min_id] = tolerance
                    self.pTolerance[who_belong + (whom_belong - min_id) * (max_id - min_id + 1) - min_id] = tolerance
                else:
                    logger.warning(f"Belong {who_belong} is in both 'forwhom' and 'who' attribs of set!")

    def GetTolerance(self, belongId1: int, belongId2: int, from_default: bool = False):
        if from_default:
            tolerance_source = self.pDefaultTolerance
        else:
            tolerance_source = self.pTolerance
        if belongId1 == belongId2:
            return self.toleranceMap["own"]
        if belongId1 < self.minID or belongId1 > self.maxID or belongId2 < self.minID or belongId2 > self.maxID:
            return self.defaultTolerance
        else:
            return tolerance_source[belongId1 + (belongId2 - self.minID) * (self.maxID - self.minID + 1) - self.minID]

    def GetToleranceByName(self, tol_name):
        tol = self.toleranceMap.get(tol_name)
        if tol is not None:
            return tol["tolerance"]
        else:
            return self.defaultTolerance

    def CheckTolerance(self, belongId1: int, belongId2: int, from_default: bool = False):
        if belongId1 == belongId2:
            return self.toleranceMap["own"]
        if belongId1 < self.minID or belongId1 > self.maxID or belongId2 < self.minID or belongId2 > self.maxID:
            return self.defaultTolerance
        tolerance_difference = self.GetTolerance(belongId1, belongId2, from_default) - self.defaultTolerance
        nearest_tolerance = self.defaultTolerance
        min_tolerance = abs(tolerance_difference)
        tolerance_declared = self.GetTolerance(belongId1, belongId2)

        for tolerance_state in self.toleranceList:
            tolerance_for_index = tolerance_state['tolerance']
            if min_tolerance > abs(tolerance_declared - tolerance_for_index):
                nearest_tolerance = tolerance_for_index
                min_tolerance = abs(tolerance_declared - tolerance_for_index)

        return nearest_tolerance
