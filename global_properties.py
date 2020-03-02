from engine_config import EngineConfig
from em_parse import xml_to_objfy, read_from_xml_node


class Kernel(object):
    def __init__(self):
        self.engineConfig = EngineConfig()
        self.fileMan = FileServer()
        self.scriptHandle = 0
        self.scriptServer = ScriptServer()


class Server(object):
    def InitOnce(self):
        engine_config = Kernel.engineConfig
        self.LoadGlobalPropertiesFromXML(engine_config.global_properties_path)

    def LoadGlobalPropertiesFromXML(self, fileName):
        xmlFile = xml_to_objfy(fileName)
        if xmlFile.tag == "Properties":
            self.theGlobalProp = GlobalProperties()
            self.theGlobalProp.LoadFromXML(fileName, xmlFile)
        else:
            raise NameError("GlobalProperties file should contain Properties tag")


class GlobalProperties(object):
    def __init__(self):
        self.difficultyLevelCoeffs = []
        self.barmenModelName = ""
        self.namedBelongIds = ""
        self.pathToResourceTypes = ""
        self.pathToVehiclePartTypes = ""
        self.pathToAffixes = ""
        self.pathToQuests = ""
        self.pathToGameObjects = ""
        self.pathToRelationship = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        izvrat_repository = xmlNode["IzvratRepository"]
        izvratRepositoryMaxSize = read_from_xml_node(izvrat_repository, "MaxSize")
        self.izvratRepositoryMaxSize_x = izvratRepositoryMaxSize.split()[0]
        self.izvratRepositoryMaxSize_y = izvratRepositoryMaxSize.split()[1]


class CoeffsForDifficultyLevel(object):
    def __init__(self):
        self.name = ""
        self.damageCoeffForPlayerFromEnemies = 0.0
        self.enemiesShootingDelay = 0.0
