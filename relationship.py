from warnings import warn
from em_parse import read_from_xml_node, xml_to_objfy


class Relationship(object):
    def __init__(self):
        self.toleranceMap = {}  # ??? can this be useful?
        self.tolerance = 0
        self.playerDefaultTolerance = 0  # pTolerance
        self.defaultTolerance = 1
        self.minID = 0
        self.maxId = -1
        self.toleranceList = []

        self.toleranceMap["enemy"] = {"name": "enemy",
                                      "tolerance": 1}
        self.toleranceMap["neutral"] = {"name": "neutral",
                                        "tolerance": 2}
        self.toleranceMap["ally"] = {"name": "ally",
                                     "tolerance": 3}
        self.toleranceMap["own"] = {"name": "own",
                                    "tolerance": 4}

        self.toleranceList = [tol for tol in self.toleranceMap.values()]

    def LoadFromXML(self, xmlFile):
        xmlNode = xml_to_objfy(xmlFile)
        if xmlNode.tag != "relationship":
            raise ValueError("Relationship XML should contain root tag 'relationship'!")
        self.tolerance = {}
        self.minID = int(read_from_xml_node(xmlNode, "MinPlayerID"))
        self.maxID = int(read_from_xml_node(xmlNode, "MaxPlayerID"))
        self.playerDefaultTolerance = read_from_xml_node(xmlNode, "DefaultTolerance")

        if self.playerDefaultTolerance is not None:
            self.playerDefaultTolerance = 0  # ??? why we discarding saved value?

        defaultTolerance = int(read_from_xml_node(xmlNode, "DefaultTolerance"))
        tolerance = self.GetToleranceByName(defaultTolerance)
        self.defaultTolerance = tolerance

        if self.minID <= self.maxID:
            if self.maxID - self.minID + 1 > 1000:
                self.maxID = self.minID + 1001
                warn(f"Tolerance range can't be more than 1001, for example 1000-2001 range is valid."
                     f"Reseting max value to be {self.maxID}")
                # tolerance_diff = self.maxID - self.minID
                tolerance_range = range(self.minID, self.maxID)
                for tolerance in tolerance_range:
                    self.playerDefaultTolerance[tolerance] = self.defaultTolerance
                    format_type = read_from_xml_node(xmlNode, "FormatType")
                    if format_type is not None:
                        format_type = int(format_type)
                        if format_type == 1:
                            raise NotImplementedError("Can't work with saves yet, do not load from currentmap.xml")
                            self.LoadFormat(xmlFile, xmlNode, 1)  # ??? do we even need this for format_type 1?
                        else:
                            raise ValueError(f"Invalid format type {format_type} for relationship")
                    else:
                        self.LoadFormat(xmlFile, xmlNode, 0)
        else:
            raise ValueError("Relationship MinPlayerID should be less than MaxPlayerID")

    def LoadFormat(self, xmlFile, xmlNode, format_type: int = 0):
        for rel in xmlNode.iterchildren():
            if rel.tag != "set":
                warn(f"Invalid tag {rel.tag} in Relationship map {xmlNode.base}")
            else:
                tolerance = self.GetToleranceByName(read_from_xml_node(rel, "tolerance"))
                for_whom = read_from_xml_node(rel, "forwhom")
                who = read_from_xml_node(rel, "who")
                self.SetTolerance(for_whom, who, tolerance)

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
