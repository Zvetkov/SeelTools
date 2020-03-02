from em_parse import read_from_xml_node, is_xml_node_contains
from prototype_info import PrototypeInfo


class VehicleDescription(object):
    def __init__(self, xmlFile, xmlNode):
        self.vehiclePrototypeIds = []
        self.waresPrototypesIds = []
        self.vehiclePrototypeNames = []
        self.waresPrototypesNames = []
        self.gunAffixGeneratorPrototypeName = ""
        VehicleDescription.LoadFromXML(self, xmlFile, xmlNode)

    def LoadFromXML(self, xmlFile, xmlNode):
        self.Wares
        self.GunAffixGenerator
        self.VehiclesPrototypes
        self.partOfSchwartz = -1.0
        if xmlNode and is_xml_node_contains(xmlNode, "PartOfSchwartz"):
            self.partOfSchwartz = read_from_xml_node(xmlNode, "PartOfSchwartz")
        self.TuningBySchwartz = self.partOfSchwartz > 0.0  # bool
        self.vehiclePrototypeNames = read_from_xml_node(xmlNode, "VehiclesPrototypes")
        self.waresPrototypesNames = read_from_xml_node(xmlNode, "WaresPrototypes")
        self.gunAffixGeneratorPrototypeName = read_from_xml_node(xmlNode, "GunAffixGeneratorPrototype")


class VehiclesGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        self.vehicleDescriptions = []
