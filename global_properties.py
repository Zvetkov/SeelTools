from warnings import warn
from engine_config import EngineConfig
from em_parse import xml_to_objfy, read_from_xml_node, parse_str_to_bool


class Kernel(object):
    def __init__(self):
        self.engineConfig = EngineConfig()
        # self.fileMan = FileServer()  # probably useless for use in tool
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
        self.attractiveCoeff = 1.0
        self.barmenModelName = "mask1"
        self.blastWaveCameraShakeRadiusCoeff = 2.0
        self.colorEnemy = -65536  # ???
        self.colorFriend = -16711936  # ??? (should be hex?)
        self.colorTargetCaptured = -256
        self.defaultArticleRegenerationTime = 100.0
        self.defaultLookBoxLength = 50.0
        self.defaultTargetBoxLength = 50.0
        self.difficultyLevelCoeffs = []
        self.distanceFromPlayerToMoveout = 300.0
        self.distToTurnOffPhysics = 320.0
        self.distToTurnOnPhysics = 300.0
        self.energyBlowDeltaTime = 1.2
        self.energyVpBlowProbability = 5
        self.energyWheelBlowProbability = 2
        self.flowVpVelocity = 6.0
        self.flowWheelVelocity = 4.0
        self.gameTimeMult = 60.0
        self.groundRepositorySize_x = 14
        self.groundRepositorySize_y = 300
        self.healthUnitPrice = 1.0
        self.infoAreaRadius = 10
        self.infoObjUpdateTimeout = 0.5
        self.izvratRepositoryMaxSize_x = 13
        self.izvratRepositoryMaxSize_y = 13
        self.lockTimeout = 5.0
        self.maxDistToAvoid = 1.0
        self.maxGroupingAngle = 0.043633234  # pi/72
        self.maxShakeDamage = 100.0
        self.maxSpeedWithNoFuel = 0.0
        self.namedBelongIds = []
        self.pathToAffixes = ""
        self.pathToGameObjects = ""
        self.pathToQuests = ""
        self.pathToRelationship = ""
        self.pathToResourceTypes = ""
        self.pathToVehiclePartTypes = ""
        self.physicStepTime = 0.039999999
        self.playerPassMapUnpassableCfm = 0.0099999998
        self.playerPassMapUnpassableErp = 0.1
        self.playerPassMapUnpassableMu = 0.30000001
        self.predictionTime = 1.0
        self.probabilityToDropArticlesFromDeadVehicles = 0.69999999
        self.probabilityToDropGunsFromDeadVehicles = 0.69999999
        self.probabilityToGenerateDynamicQuestInTown = 1.0
        self.property2PriceCoeff = 1.0
        self.repulsiveCoeff = 1.0
        self.shakeDamageToDurationCoeff = 2.0
        self.splintersAutoDisableAngularThreshold = 0.1
        self.splintersAutoDisableLinearThreshold = 0.1
        self.splintersAutoDisableNumSteps = 5
        self.targetCapturedContourWidth = 0.69999999
        self.targetInfoContourWidth = 0.69999999
        self.throwCoeff = 3.0
        self.timeOutForReAimGuns = 0.5
        self.unlockRegion.x = 100.0
        self.unlockRegion.y = 100.0
        self.vehicleAiFiringRangeMult = 1.0
        self.vehiclesDropChests = 1
        self.zoneDefaultFirstSpawnTime = 10.0
        self.zoneRespawnTimeOutIncreaseCoeff = 1.1

    def LoadFromXML(self, xmlFile, xmlNode):
        namedBelongIds = read_from_xml_node(xmlNode["Belongs"], "Values")
        self.namedBelongIds = namedBelongIds.split()
        self.namedBelongIdsVector = self.namedBelongIds  # ??? are both needed?

        izvratRepositoryMaxSize = read_from_xml_node(xmlNode["IzvratRepository"], "MaxSize")
        self.izvratRepositoryMaxSize_x = izvratRepositoryMaxSize.split()[0]
        self.izvratRepositoryMaxSize_y = izvratRepositoryMaxSize.split()[1]

        groundRepositorySize = read_from_xml_node(xmlNode["GroundRepository"], "Size")
        self.groundRepositorySize_x = groundRepositorySize.split()[0]
        self.groundRepositorySize_y = groundRepositorySize.split()[1]

        self.gameTimeMult = read_from_xml_node(xmlNode["Mult"], "GameTimeMult")
        if self.gameTimeMult <= 0.000099999997:
            warn("GameTimeMult is too low! Set to 0.0001 or higher")
        self.vehicleAiFiringRangeMult = read_from_xml_node(xmlNode["Mult"], "VehicleAIFiringRangeMult")

        self.maxBurstTime = read_from_xml_node(xmlNode["BurstParameters"], "MaxBurstTime")
        self.minBurstTime = read_from_xml_node(xmlNode["BurstParameters"], "MinBurstTime")
        self.timeBetweenBursts = read_from_xml_node(xmlNode["BurstParameters"], "TimeBetweenBursts")

        self.probabilityToGenerateDynamicQuestInTown = \
            read_from_xml_node(xmlNode["DynamicQuest"], "ProbabilityToGenerateDynamicQuestInTown")
        if self.probabilityToGenerateDynamicQuestInTown < 0.0 or self.probabilityToGenerateDynamicQuestInTown > 1.0:
            warn("ProbabilityToGenerateDynamicQuestInTown value is invalid! Set between 0.0 and 1.0")

        self.pathToRelationship = read_from_xml_node(xmlNode["CommonPaths"], "Relationship")
        self.pathToGameObjects = read_from_xml_node(xmlNode["CommonPaths"], "GameObjects")
        self.pathToQuests = read_from_xml_node(xmlNode["CommonPaths"], "Quests")
        self.pathToResourceTypes = read_from_xml_node(xmlNode["CommonPaths"], "ResourceTypes")
        self.pathToAffixes = read_from_xml_node(xmlNode["CommonPaths"], "Affixes")
        self.pathToVehiclePartTypes = read_from_xml_node(xmlNode["CommonPaths"], "VehiclePartTypes")

        self.distToTurnOnPhysics = read_from_xml_node(xmlNode["Physics"], "DistToTurnOnPhysics")
        self.distToTurnOffPhysics = read_from_xml_node(xmlNode["Physics"], "DistToTurnOffPhysics")
        self.physicStepTime = read_from_xml_node(xmlNode["Physics"], "PhysicStepTime")
        if self.distToTurnOffPhysics - 10.0 <= self.distToTurnOnPhysics:
            warn("Differenece between distToTurnOffPhysics and distToTurnOnPhysics is too low! "
                 "Set to be at least 10.0 appart")

        self.barmenModelName = read_from_xml_node(xmlNode["Npc"], "BarmenModelName")

        self.splintersAutoDisableLinearThreshold = \
            read_from_xml_node(xmlNode["BreakableObjectSplinters"], "AutoDisableLinearThreshold")
        self.splintersAutoDisableAngularThreshold = \
            read_from_xml_node(xmlNode["BreakableObjectSplinters"], "AutoDisableAngularThreshold")
        self.splintersAutoDisableNumSteps = \
            read_from_xml_node(xmlNode["BreakableObjectSplinters"], "AutoDisableNumSteps")

        self.vehiclesDropChests = \
            parse_str_to_bool(read_from_xml_node(xmlNode["Vehicles"], "VehiclesDropChests"))
        maxSpeedWithNoFuel = read_from_xml_node(xmlNode["Vehicles"], "MaxSpeedWithNoFuel")
        # ??? why? Is this working?
        self.maxSpeedWithNoFuel = maxSpeedWithNoFuel * 0.27777779  # 5/18 = 0.2(7)

        self.infoAreaRadius = read_from_xml_node(xmlNode["SmartCursor"], "InfoAreaRadius")
        self.lockTimeout = read_from_xml_node(xmlNode["SmartCursor"], "LockTimeout")
        unlockRegion = read_from_xml_node(xmlNode["SmartCursor"], "UnlockRegion")
        self.unlockRegion = unlockRegion.split()
        # ??? unused in actual game globalproperties.cfg
        # self.infoObjUpdateTimeout = read_from_xml_node(xmlNode["SmartCursor"], "InfoObjUpdateTimeout")

        self.blastWaveCameraShakeRadiusCoeff = \
            read_from_xml_node(xmlNode["CameraController"], "BlastWaveCameraShakeRadiusCoeff")
        self.shakeDamageToDurationCoeff = read_from_xml_node(xmlNode["CameraController"], "ShakeDamageToDurationCoeff")
        self.maxShakeDamage = read_from_xml_node(xmlNode["CameraController"], "MaxShakeDamage")
        if self.maxShakeDamage <= 1.0:
            warn("maxShakeDamage should be more than 1.0!")

        self.distanceFromPlayerToMoveout = read_from_xml_node(xmlNode["Caravans"], "DistanceFromPlayerToMoveout")

        self.defaultLookBoxLength = read_from_xml_node(xmlNode["ObstacleAvoidance"], "DefaultLookBoxLength")
        self.defaultTargetBoxLength = read_from_xml_node(xmlNode["ObstacleAvoidance"], "DefaultTargetBoxLength")
        self.attractiveCoeff = read_from_xml_node(xmlNode["ObstacleAvoidance"], "AttractiveCoeff")
        self.repulsiveCoeff = read_from_xml_node(xmlNode["ObstacleAvoidance"], "RepulsiveCoeff")
        self.maxDistToAvoid = read_from_xml_node(xmlNode["ObstacleAvoidance"], "MaxDistToAvoid")
        self.predictionTime = read_from_xml_node(xmlNode["ObstacleAvoidance"], "PredictionTime")

        self.throwCoeff = read_from_xml_node(xmlNode["DeathProperties"], "ThrowCoeff")
        self.flowVpVelocity = read_from_xml_node(xmlNode["DeathProperties"], "FlowVpVelocity")
        self.flowWheelVelocity = read_from_xml_node(xmlNode["DeathProperties"], "FlowWheelVelocity")
        self.energyBlowDeltaTime = read_from_xml_node(xmlNode["DeathProperties"], "EnergyBlowDeltaTime")
        self.energyVpBlowProbability = read_from_xml_node(xmlNode["DeathProperties"], "EnergyVpBlowProbability")
        self.energyWheelBlowProbability = read_from_xml_node(xmlNode["DeathProperties"], "EnergyWheelBlowProbability")

        self.healthUnitPrice = read_from_xml_node(xmlNode["Repair"], "HealthUnitPrice")

        self.defaultArticleRegenerationTime = \
            read_from_xml_node(xmlNode["Articles"], "DefaultRegenerationTime")
        self.probabilityToDropArticlesFromDeadVehicles = \
            read_from_xml_node(xmlNode["Articles"], "ProbabilityToDropArticlesFromDeadVehicles")
        self.probabilityToDropGunsFromDeadVehicles = \
            read_from_xml_node(xmlNode["Articles"], "ProbabilityToDropGunsFromDeadVehicles")

        self.zoneRespawnTimeOutIncreaseCoeff = \
            read_from_xml_node(xmlNode["InfectionZones"], "ZoneRespawnTimeOutIncreaseCoeff")
        self.zoneDefaultFirstSpawnTime = \
            read_from_xml_node(xmlNode["InfectionZones"], "ZoneDefaultFirstSpawnTime")

        self.colorFriend = read_from_xml_node(xmlNode["InterfaceStuff"], "ColorFriend")
        self.colorEnemy = read_from_xml_node(xmlNode["InterfaceStuff"], "ColorEnemy")
        self.colorTargetCaptured = read_from_xml_node(xmlNode["InterfaceStuff"], "ColorTargetCaptured")
        self.targetInfoContourWidth = read_from_xml_node(xmlNode["InterfaceStuff"], "TargetInfoContourWidth")
        self.targetCapturedContourWidth = read_from_xml_node(xmlNode["InterfaceStuff"], "TargetCapturedContourWidth")

        self.playerPassMapUnpassableMu = read_from_xml_node(xmlNode["PlayerPassmap"], "PlayerPassMapUnpassableMu")
        self.playerPassMapUnpassableErp = read_from_xml_node(xmlNode["PlayerPassmap"], "PlayerPassMapUnpassableErp")
        self.playerPassMapUnpassableCfm = read_from_xml_node(xmlNode["PlayerPassmap"], "PlayerPassMapUnpassableCfm")

        fullGroupingAngleDegree = read_from_xml_node(xmlNode["Weapon"], "MaxGroupingAngle")
        self.maxGroupingAngle = fullGroupingAngleDegree * 0.017453292 * 0.5  # pi/180 = 0.017453292
        self.timeOutForReAimGuns = read_from_xml_node(xmlNode["Weapon"], "TimeOutForReAimGuns")

        diffLevels = xmlNode["DifficultyLevels"]
        for diffLevel in diffLevels:
            if diffLevel.tag == "Level":
                self.difficultyLevelCoeffs.append(CoeffsForDifficultyLevel().LoadFromXML(xmlFile, xmlNode))
            else:
                warn(f"Unexpected tag {diffLevel.tag} in DifficultyLevels enumeration")

        self.property2PriceCoeff = read_from_xml_node(xmlNode["Price"], "Property2PriceCoeff")
        if not self.difficultyLevelCoeffs:
            raise ValueError("No difficulty levels in GlobalProperties!")


class CoeffsForDifficultyLevel(object):
    def __init__(self):
        self.name = ""
        self.damageCoeffForPlayerFromEnemies = 0.0
        self.enemiesShootingDelay = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        self.name = read_from_xml_node(xmlNode, "Name")
        self.damageCoeffForPlayerFromEnemies = read_from_xml_node(xmlNode, "EnemyWeaponCoeff")
        self.enemiesShootingDelay = read_from_xml_node(xmlNode, "EnemyShootingDelay")
        if self.damageCoeffForPlayerFromEnemies < 0.0:
            warn("Invalid EnemyWeaponCoeff! Should be a positive float number!")
        if self.enemiesShootingDelay < 0.0 or self.enemiesShootingDelay > 3.0:
            warn("Invalid EnemyShootingDelay! Should be a positive float number between 0.0 and 3.0")
