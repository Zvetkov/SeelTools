import os
from timeit import default_timer as timer

from seeltools.utilities.log import logger
from seeltools.utilities.parse import xml_to_objfy
from seeltools.utilities.engine_config import EngineConfig
from seeltools.utilities.global_properties import GlobalProperties

from seeltools.server.affix import AffixManager
from seeltools.server.relationship import Relationship
from seeltools.server.resource_manager import ResourceManager
from seeltools.server.application import Application

from seeltools.gameobjects.prototype_info import thePrototypeInfoClassDict
from seeltools.gameobjects.prototype_manager import PrototypeManager


class Kernel(object):
    def __init__(self):
        self.engineConfig = EngineConfig()
        # self.fileMan = FileServer()  # probably useless for use in tool
        self.scriptHandle = 0
        # self.scriptServer = ScriptServer()


class Server(object):
    def InitOnce(self, theKernel):
        '''Called by CMiracle3d::LoadLevel'''
        self.engine_config = theKernel.engineConfig
        self.LoadGlobalPropertiesFromXML(self.engine_config.global_properties)
        self.theResourceManager = ResourceManager(self, 0, 0)
        self.theAffixManager = AffixManager(self.theResourceManager)
        self.theAffixManager.LoadFromXML(self.theGlobalProperties.pathToAffixes)
        app = Application()
        app.LoadServers("data/models/commonservers.xml")
        app.LoadAdditionalServers("data/maps/r1m1/servers.xml")
        app.LoadAdditionalServers("data/maps/r1m2/servers.xml")
        app.LoadAdditionalServers("data/maps/r1m3/servers.xml")
        app.LoadAdditionalServers("data/maps/r1m4/servers.xml")
        app.LoadAdditionalServers("data/maps/r2m1/servers.xml")
        app.LoadAdditionalServers("data/maps/r2m2/servers.xml")
        app.LoadAdditionalServers("data/maps/r3m1/servers.xml")
        app.LoadAdditionalServers("data/maps/r3m2/servers.xml")
        app.LoadAdditionalServers("data/maps/r4m1/servers.xml")
        app.LoadAdditionalServers("data/maps/r4m2/servers.xml")
        self.theAnimatedModelsServer = app.servers['AnimatedModelsServer'].server

    def Load(self, a2: int = 0, startupMode=0, xmlFile=0, xmlNode=0, isContiniousMap=0, saveType=0):
        start = timer()
        logger.debug("Starting timer")
        logger.info("Loading Server")
        self.saveType = saveType
        if not isContiniousMap:
            logger.info("Loading Realtionship")
            self.theRelationship = Relationship()
            self.theRelationship.LoadFromXML(self.theGlobalProperties.pathToRelationship, copy_to_default=True)
        logger.info("Skipping loading SoilProps")
        logger.info("Skipping loading ExternalPaths")
        logger.info("Skipping loading PlayerPassMap")
        if not isContiniousMap:
            logger.info("Skipping loading GameObjects")
            self.thePrototypeManager = PrototypeManager(self)
            self.thePrototypeManager.LoadFromXMLFile(self.theGlobalProperties.pathToGameObjects)
            logger.info("Initializing VehicleGeneratorInfoCache")
            # self.theVehiclesGeneratorInfoCache = VehiclesGeneratorInfoCache()
            # self.theVehiclesGeneratorInfoCache.EnsureInitialized()
            # logger.info("Refreshing GameObjects")
            # self.thePrototypeManager.RefreshFromXmlFile()  # (CStr)
            # logger.info("Loading QuestStates")
            # questStatesFileName = self.level.GetFullPathNameA(self.level, allowed_classes,
            #                                                   self.level.questStatesFileName)
            # self.theQuestStateManager = QuestStateManager()
            # self.theQuestStateManager.LoadFromXML(a2, self, questStatesFileName)
            # logger.info("QuestStates loaded")
            # logger.info("Loading DynamicScene")
            # self.theDynamicScene = DynamicScene()
            # if xmlNode:
            #     self.theDynamicScene.LoadSceneFromXML(xmlFile, xmlNode, allowed_classes)
            # else:
            #     allowedClasses = []
            #     level_file_name = self.level.GetFullPathNameA(self.level, allowed_classes, self.level.dsSrvName)
            #     self.theDynamicScene.LoadSceneFromXML(self.pDynamicScene, level_file_name, allowedClasses)
            # logger.info("DynamicScene loaded")
        end = timer()
        logger.debug(f"Loading Server Total time: {end - start}")

    def LoadGlobalPropertiesFromXML(self, fileName):
        xmlFile = xml_to_objfy(fileName)
        if xmlFile.tag == "Properties":
            self.theGlobalProperties = GlobalProperties()
            self.theGlobalProperties.LoadFromXML(fileName, xmlFile)
        else:
            raise NameError("GlobalProperties file should contain root Properties tag")

    def LoadPrototypeNamesFromXML():
        raise NotImplementedError("LoadPrototypeNamesFromXML not implementet for Server")

    def CreatePrototypeInfoByClassName(self, className: str):
        class_refference = thePrototypeInfoClassDict.get(className)
        if class_refference is not None:
            class_refference(self)
        return class_refference

    def save_all(self):
        self.thePrototypeManager.save_to_xml(self.theGlobalProperties.pathToGameObjects)


theKernel = Kernel()
theServer = Server()
theServer.InitOnce(theKernel)
theServer.Load()
