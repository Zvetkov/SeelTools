from math import sqrt, cos, pi
from copy import deepcopy

from id_manager import theIdManager
from constants import STATUS_SUCCESS, ZERO_VECTOR, INITIAL_OBJECTS_DIRECTION, BUILDING_TYPE, IDENTITY_QUATERNION
from global_functions import MassSetBoxTotal
from em_parse import safe_check_and_set, parse_str_to_bool, read_from_xml_node, child_from_xml_node

from logger import logger


class Object(object):
    '''Base class for all game object classes'''
    def __init__(self, class_object=None):
        self.refCount = 0
        obj_id = theIdManager.GetUniqueId()
        self.name = f"Object{obj_id}"
        self.parent = None

        self.numChildren = 0
        self.children = []  # will try to use this instead of indexes of siblings and children ???
        self.children_map = {}

        self.scriptHandle = 0
        self.persistant = 1
        if class_object is not None:
            for child in class_object.children:
                self.AddChild(child)
        # self.firstChild = 0
        # self.lastChild = 0
        # self.nextSibling = 0
        # self.prevSibling = 0

    def AddChild(self, class_object):
        self.children.append(class_object)
        class_object.parent = self
        self.children_map[class_object.name] = class_object
        self.numChildren += 1
        # self.isChildDirty = 1  # ??? whytf do we need this?
        return STATUS_SUCCESS

    def GetChildByName(self, name: str):
        return self.children_map.get(name)


class Obj(Object):
    '''Base class containing prototype info'''
    def __init__(self, prototype_info_object=None):
        Object.__init__(self)
        self.allChildren = []
        self.isNil = 1
        self.appliedPrefixIds = []
        self.appliedSuffixIds = []
        self.modifiers = []
        self.eventRecipients = []
        self.parentRepository = 0
        self.passedToAnotherMap = False
        self.hierarchyType = 0
        self.isAlreadySaved = False
        self.affixesWasApplied = False
        self.prototypeId = -1
        self.flags = 17
        self.needPostLoad = True
        self.mustCreateVisualPart = True
        self.parentId = -1
        self.belong = 1000
        self.objId = -1
        self.updatingObjId = -1
        self.isUpdating = True
        self.mustBeUpdating = True
        self.timeOut = 0.0
        # self.LastDamageSource = -1
        if prototype_info_object is not None:
            self.prototypeId = prototype_info_object.prototypeId
            self.isUpdating = prototype_info_object.isUpdating

    def LoadFromXML(self, xmlFile, xmlNode):
        logger.info("Contains info mostly useful for savefile loading, ignoring?")


class GeomRepository(Object):
    def __init__(self):
        Object.__init__(self)
        self.slots = []
        self.referenceChests = []
        self.changed = False
        self.geomSize = {"x": 1, "y": 1}
        self.sortStyle = 0
        self.vehicleId = -1


class CollisionInfo(object):
    def __init__(self, info=None):  # other CollisionInfo object can be passed as arg to initialise something of a copy
        if info is not None:
            self.trimeshVertices = 0
            self.trimeshIndices = 0
            self.geomType = info.geomType  # ??? WUT?
            self.relTranslation = {"x": info.relTranslation["x"],
                                   "y": info.relTranslation["y"],
                                   "z": info.relTranslation["z"]}
            self.relRotation = {"x": info.relRotation["x"],
                                "y": info.relRotation["y"],
                                "z": info.relRotation["z"],
                                "w": info.relRotation["w"]}
            self.size = {"x": info.size["x"],
                         "y": info.size["y"],
                         "z": info.size["z"]}
            self.radius = info.radius
            if info.trimeshVertices != 0:
                if self.geomType is not None:
                    pass  # ??? some more magic in here
            self.trimeshIndices = info.trimeshIndices
            self.numTrimeshVertices = info.numTrimeshVertices
            self.numTrimeshIndices = info.numTrimeshIndices
        else:
            self.trimeshIndices = 0
            self.trimeshVertices = 0
            self.Init()

    def Init(self):
        self.geomType = 0
        self.relRotation_y = 0
        self.relTranslation = {"x": 0.0,
                               "y": 0.0,
                               "z": 0.0}  # ??? z not actually initialized here
        self.relRotation = {"x": 0.0,
                            "y": 0.0,
                            "z": 0.0,
                            "w": 1.0}
        self.size = {"x": 0.0,
                     "y": 0.0,
                     "z": 0.0}
        self.numTrimeshVertices = 0
        self.numTrimeshIndices = 0


class PhysicBody(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.mass = 0.0
        self.pGeoms = []
        self.node = 0
        self.ownerPhysicObj = 0
        self.animAction = 0
        self.effectAction = 0
        self.cfgNum = 0
        self.animationIsStopped = False
        self.mU = 1.0
        self.needToRelinkNode = True
        if prototype_info_object is None:
            self.collisionInfos = []
            self.modelname = "BOX"
            self.trimeshVertices = []
            self.trimeshIndices = []
            # collision_info = CollisionInfo()
            # collision_info.trimeshVertices = 0
            # collision_info.trimeshIndices = 0
            # collision_info.Init()
            # self.collisionInfos.append(collision_info)
            self.collisionTrimeshAllowed = False
            self.loadedAnimTime = 0
        else:
            self.modelname = prototype_info_object.engineModelName
            self.collisionInfos = prototype_info_object.collisionInfos
            self.collisionTrimeshAllowed = prototype_info_object.collisionTrimeshAllowed

    def ChangePhysicBodyByCollisionInfo(self, collisionInfos: list):
        self.pGeoms = [0 for geom in self.pGeoms]
        for collision_info in collisionInfos:
            if collision_info == 1:
                self.pGeoms.append("Box")
            elif collision_info == 2:
                self.pGeoms.append("Sphere")
            elif collision_info == 3:
                self.pGeoms.append("Cylinder")
            elif collision_info == 4:
                self.pGeoms.append("Ray")
            elif collision_info == 5:
                self.pGeoms.append("TriMesh")
            else:
                logger.error(f"Invalid geom type: {collision_info}")


class VehiclePart(PhysicBody):
    def __init__(self, prototype_info_object=None):
        PhysicBody.__init__(self, prototype_info_object)
        self.decals = []
        self.price = {"value": prototype_info_object.price}
        self.partName = ""
        self.blowEffectName = ""
        self.suppressedLPs = []
        self.modelParts = []
        self.loadDecalsData = []
        prototype_info_object.className = "VehiclePart"
        self.durabilityCoeffsForDamageTypes = prototype_info_object.durabilityCoeffsForDamageTypes
        self.lastHitPos = 0
        self.passToAnotherMapData = 0
        self.ownerCompoundPart = 0
        collision = prototype_info_object.collisionInfos
        size = collision[8]
        size_4 = collision[9]
        size_8 = collision[10]
        if sqrt(size**2 + size_4**2 + size_8**2) < 0.001:
            size = 0.1
            size_4 = 0.1
            size_8 = 0.1
        PhysicBody.ChangePhysicBodyByCollisionInfo(self, self.collisionInfos)
        MassSetBoxTotal(self.mass, size_4, prototype_info_object.massValue, size, size_4, size_8)
        self.splashEffect = 0
        self.makeSplash = 0
        groupHealth = prototype_info_object.groupHealth  # groupHealthes in original
        for health in groupHealth:
            model_part = self.modelParts()
            model_part.health = health
            model_part.maxHealth = health
            model_part.jadedEffect = 0
            self.modelParts.append(model_part)

        class ModelPart(object):
            def __init__(self):
                self.maxHealth = 0.0
                self.health = 0.0
                self.jadedEffect = 0


class Chassis(VehiclePart):
    def __init__(self, prototype_info_object=None):
        VehiclePart.__init__(self, prototype_info_object)
        self.health = prototype_info_object.maxHealth
        self.fuel = prototype_info_object.maxFuel


class Cabin(VehiclePart):
    def __init__(self, prototype_info_object=None):
        VehiclePart.__init__(self, prototype_info_object)
        self.maxPower = prototype_info_object.maxPower
        self.maxTorque = prototype_info_object.maxTorque
        self.maxSpeed = prototype_info_object.maxSpeed
        self.fuelConsumption = prototype_info_object.fuelConsumption
        self.control = 50.0
        self.maxGadgets = 3


class Basket(VehiclePart):
    def __init__(self, prototype_info_object=None):
        VehiclePart.__init__(self, prototype_info_object)


class Trigger(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.variables = []
        self.flyPathForCinematicFly = ""
        self.triggerScriptFuncName = ""
        self.objId = []
        self.eventInfos = []
        self.callEvent = {"eventId": 0,
                          "objName": "",
                          "callObjId": -1}
        self.state = 0
        self.timeOutForTimePeriod = 1.0
        self.framesForFramesPassed = 0
        self.idForCinemaMsg = -1
        self.count = 0
        self.scriptPresent = False
        self.stateKeep = False
        self.canUpdate = False


class CinematicMover(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.flyPathName = ""
        self.currentFlyPath = 0
        self.currentFlyTime = 0.0
        self.controlledObjId = -1


class GameTime(object):
    def __init__(self):
        self.milliSeconds = 0
        self.milliSeconds0 = 0

    def init_short(self, milliSeconds):
        self.milliSeconds = milliSeconds
        self.milliSeconds0 = milliSeconds

    def init_long(self, hour: int, minute: int, day: int, month: int, year: int):
        if month > 12:
            month = 12
        if day > 30:
            day = 30
        if hour > 23:
            hour = 23
        if minute > 59:
            minute = 59
        milliSeconds = 60000 * (minute + 60 * (hour + 24 * (day + 31 * (month + 12 * year))))
        self.milliSeconds = milliSeconds
        self.milliSeconds0 = milliSeconds


class DynamicQuest(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        if self.takeGameTime:
            GameTime(self.takeGameTime)  # Loaded in runtime
        self.hirerName = ""
        self.targetName = ""
        self.hirerObjId = -1
        self.targetObjId = -1
        self.questStatus = 0
        self.reward = 0
        self.fadingMsgIdOnComplete = 2
        self.showMessageForAddMoney = True


class DynamicQuestDestroy(DynamicQuest):
    def __init__(self, prototype_info_object=None):
        DynamicQuest.__init__(self, prototype_info_object)


class DynamicQuestPeace(DynamicQuest):
    def __init__(self, prototype_info_object=None):
        DynamicQuest.__init__(self, prototype_info_object)


class DynamicQuestReach(DynamicQuest):
    def __init__(self, prototype_info_object=None):
        DynamicQuest.__init__(self, prototype_info_object)


class DynamicQuestConvoy(DynamicQuest):
    def __init__(self, prototype_info_object=None):
        DynamicQuest.__init__(self, prototype_info_object)
        self.caravanId = -1
        self.targetLocationId = -1
        self.timePlayerIsTooFar = 0.0


class DynamicQuestHunt(DynamicQuest):
    def __init__(self, prototype_info_object=None):
        DynamicQuest.__init__(self, prototype_info_object)
        self.fragsAtStart = 0
        self.showMessageForAddMoney = False
        self.timePassed = -1.0
        self.fadingMsgIdOnComplete = 1


class Gadget(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.slotNum = -1


class SgNodeObj(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.node = 0
        self.modelName = prototype_info_object.engineModelName
        self.position = []
        self.rotation = [0.0, 0.0, 0.0, 1.0]
        self.scale = 1.0
        self.needToRelink = 0


class LightObj(SgNodeObj):
    def __init__(self, prototype_info_object=None):
        SgNodeObj.__init__(self, prototype_info_object)


class PhysicObj(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        # self.intersectionObstacle = None  # 0 Ptr
        # self.body = 0
        # self.lookSphere = 0
        # self.postActionFlags = 0
        # self.physicBehaviorFlags = 0.0

        # self.postRotation.x = 0.0
        # self.postRotation.y = 0.0
        # self.postRotation.z = 0.0
        # self.postRotation.w = 1.0

        # self.postPosition.x = 0.0
        # self.postPosition.y = 0.0

        # self.massCenter.x = 0.0
        # self.massCenter.y = 0.0

        # self.body = dBodyCreate(theGlobalWorld)
        # dBodySetData(self.body.id, self)
        # self.spaceId = 0
        # self.isSpaceOwner = 1
        # if prototype_info_object.lookRadius > 0.0099999998:
        #     self.lookSphere = SphereForIntersection.CreateObject(0, 0, prototype_info_object.lookRadius)
        #     self.lookSphere.geomId = self.body.id
        # Sphere.CreateObject(0, 0, 1.0)
        # self.boundSphere = "sphere"
        # self.bIsUpdatingByODE = 1
        # self.enabledCellsCount = 0
        # self.bBodyEnabledLastFrame = 1
        self.skinNumber = 0
        # self.physicState = 3
        # self.timeFromLastCollisionEffect = 1000.0


class SimplePhysicObj(PhysicObj):
    def __init__(self, prototype_info_object=None):
        PhysicObj.__init__(self, prototype_info_object)
        if prototype_info_object is not None:
            self.collisionInfos = prototype_info_object.collisionInfos
        self.scale = 1.0
        self.physicBody = None  # ??? Some magic happens here, probably don't need this
        # self.deadTimerActive = 0
        # self.deadTimer = 0.0
        # self.testVisibility = 0
        # self.Construct(self)

    def Construct(self):
        if self.physicBody is not None:
            logger.warn("Not implemented Construct method for SimplePhysicObject class")


class Chest(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.lifeTime = prototype_info_object.lifeTime
        self.repository = GeomRepository()
        self.repository.geomSize["x"] = 200  # guessing, missing parameter name
        self.repository.geomSize["y"] = 2000  # guessing, missing parameter name
        # self.SetAutoDisabling(isAutoDisabling=True, linearThreshold=0.1, angularThreshold=0.1, steps=5)


class ObjPrefab(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.physicObjs = []
        self.otherChildren = []
        self.vehiclesForAdd = []
        self.team = 0


class Barricade(ObjPrefab):
    def __init__(self, prototype_info_object=None):
        ObjPrefab.__init__(self, prototype_info_object)
        self.probability = prototype_info_object.probability


class Settlement(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)

    def LoadFromXML(self, xmlFile, xmlNode):
        pass


class InfectionLair(Settlement):
    def __init__(self, prototype_info_object=None):
        Settlement.__init__(self, prototype_info_object)


class InfectionZone(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.infectionPolygon = []
        self.dropOutPoints = []
        self.infectionTeamPrototypeName = ""
        self.infectionLairName = ""
        self.minDistToPlayer = prototype_info_object.minDistToPlayer
        self.criticalTeamDist = prototype_info_object.criticalTeamDist
        self.criticalTeamTime = prototype_info_object.criticalTeamTime
        self.blindTeamDist = prototype_info_object.blindTeamDist
        self.hadPlayerInside = False
        self.infectionTeamId = -1
        self.infectionLairId = -1
        self.baseTimeoutForRespawn = 30.0
        self.timeoutForRespawn = 30.0
        self.dropOutCos = 0.0
        self.timeForRespawn = 0.0
        self.dropOutTimeOut = 0.0
        self.lastFramePlayerInsideWithoutEnemies = 0.0
        self.dropOutCos = cos((prototype_info_object.dropOutSegmentAngle / 2) * pi / 180)


class Team(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.removeWhenChildrenDead = prototype_info_object.removeWhenChildrenDead
        self.ai = [0]
        self.vehicles = []
        self.steeringForceMap = []
        self.teamTacticName = ""
        self.useStandardUpdatingBehavior = True
        self.ai = self.decisionMatrixNum  # AI.SetDecisionMatrix(this_team.AI, prototypeInfo.decisionMatrixNum) ???
        self.formation = 0
        self.combatMastermind = 0
        self.pPath = 0
        self.frozen = False
        self.mustMoveToTarget = False
        self.maxTeamSpeed = 13.888889
        self.needAdjustBehaviour = True
        self.teamTacticId = -1
        self.teamTacticShouldBeAssigned = True


class InfectionTeam(Team):
    def __init__(self, prototype_info_object=None):
        Team.__init__(self, prototype_info_object)
        self.generated = False
        self.removeWhenChildrenDead = False
        self.criticalTeamDist = 1000000.0
        self.criticalTeamTime = 0.0
        self.timeBeyondCriticalDist = 0.0
        self.blindTeamDist = 1000000.0
        self.blindTeamTime = 0.0
        self.timeBeyondBlindDist = 0.0


class Location(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.idsWasInside = []
        self.targetClasses = []
        self.toleranceSet = []
        self.passageAddress = ""
        self.correspondingPassageLocationName = ""
        self.npcs = []
        self.locationType = 0
        self.isActive = True
        self.lookingTimeOut = 1.0
        self.passageActive = True
        self.toleranceSet.append("eTolerance")
        self.targetClasses.append("Vehicle")
        self.targetClasses.append("Boss02")
        self.numFramesPassed = 0


class ComplexPhysicObj(PhysicObj):
    def __init__(self, prototype_info_object=None):
        PhysicObj.__init__(self, prototype_info_object)
        if prototype_info_object is not None:
            self.vehicleParts = []


class StaticAutoGun(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.health = 0.0
        self.maxHealth = 0.0  # actually NumericInRangeRegenerating object, probably only matters in runtime
        self.timeForNextCheck = 0.1  # temp value
        self.destroyedModelName = prototype_info_object.destroyedModelName
        self.targetClasses = []
        self.currentEnemyId = -1


class AnimatedComplexPhysicObj(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)


class Vehicle(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.wheels = []
        self.AI = []
        self.gadgets = []


class ArticulatedVehicle(Vehicle):
    def __init__(self, prototype_info_object):
        Vehicle.__init__(self, prototype_info_object)
        self.trailerObjId = -1
        self.trailerJoint = 0
        self.relJointPosOnMe = deepcopy(ZERO_VECTOR)
        self.relJointPosOnTrailer = deepcopy(ZERO_VECTOR)


class VehicleRecollection(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.recollectionItems = []
        self.vehicleId = -1


class WanderersManager(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.wayPointIndexMap = []
        self.wayPoints = []
        self.precisePaths = []
        self.caravanInfos = []
        self.vagabondPrototypeIds = []
        self.rebornTimeout = 10.0
        self.wandererStates = []
        self.waitingVagabonds = []
        self.guardVehiclesIds = []
        self.transitionIndices = []
        self.timeBeforeReborn = 0.0

    class WandererState(object):
        def __init__(self):
            self.timeout = 0.0
            self.precisePath = []

    class CaravanInfo(object):
        def __init__(self):
            self.prototypeName = ""
            self.wayPointIndices = []


class CaravanTeam(Team):
    def __init__(self, prototype_info_object=None):
        Team.__init__(self, prototype_info_object)
        self.guardVehiclesIds = []
        self.removeWhenChildrenDead = False
        self.useStandardUpdatingBehavior = False
        self.waitingForPlayerToMoveout = False
        self.guardTeamId = -1
        self.curAttackerId = -1


class VagabondTeam(Team):
    def __init__(self, prototype_info_object=None):
        Team.__init__(self, prototype_info_object)
        # should be replaced with proper Id for PrototypeManager
        self.vehiclesGeneratorPrototypeId = "PLACEHOLDER_PROTOTYPE_ID"
        if self.vehiclesGeneratorPrototypeId == -1:
            logger.error(f"Unknown VehiclesGenerator {self.vehiclesGeneratorPrototype}")


class VehiclesGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.vehicleDescription = {"vehiclePrototypeIds": [],
                                   "vehiclePrototypeNames": [],
                                   "gunAffixGeneratorPrototypeName": [],
                                   "tuningBySchwartz": True,
                                   "gunAffixGeneratorPrototypeId": -1}
        self.desiredCountLow = -1
        self.desiredCountHigh = -1


class Formation(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.distBetweenVehicles = 30.0
        self.maxVehicles = prototype_info_object.maxVehicles
        self.linearVelocity = prototype_info_object.linearVelocity
        self.angularVelocity = prototype_info_object.angularVelocity
        self.position = deepcopy(ZERO_VECTOR)
        self.direction = deepcopy(INITIAL_OBJECTS_DIRECTION)
        self.positions = []
        self.pPath = 0
        self.numPathPoint = -1
        self.vehicles = []


class DummyObject(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        # if prototype_info_object.disablePhysics:
        #     self.DisablePhysics(self)
        # if prototype_info_object.disableGeometry:
        #     self.DisableGeometry(self)
        if self.physicBody is not None:
            logger.warn("Not implemented PhysicBody check related to modelName")


class Player(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.modelName = prototype_info_object.modelName
        self.skinNumber = prototype_info_object.skinNumber
        self.cfgNumber = prototype_info_object.cfgNumber


class RadioManager(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.radioEnabled = True


class VehicleRole(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.targetVehicleId = -1
        self.targetTeamId = -1
        self.targetObjId = -1


class VehicleRoleBarrier(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)


class VehicleRoleCoward(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)


class VehicleRoleOppressor(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)


class VehicleRoleMeat(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)
        self.chaseTactics = 0
        self.needCreateChaseTactics = 0


class VehicleRoleCheater(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)
        self.chaseTactics = 0
        self.needCreateChaseTactics = 0


class VehicleRoleSniper(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)
        self.sniperState = 0
        self.deniedHeight = 10000.0


class VehicleRolePendulum(VehicleRole):
    def __init__(self):
        VehicleRole.__init__(self)
        self.direction_x = 1.0
        self.direction_y = 0.0
        self.angle = 0.0


class TeamTacticWithRoles(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)


class NPCMotionController(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.elapsedStateTime = 0.0
        self.timeForState = 0.0
        self.vehicleUnderControlId = -1
        self.style = 0
        self.lastDesiredPosition = []
        self.characteristicDist = 10.0
        self.characteristicPeriod = 5.0


class BossMetalArm(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.turningSpeed = prototype_info_object.turningSpeed
        self.loadObjId = -1
        self.attackState = 0
        self.dirForCharging = deepcopy(ZERO_VECTOR)
        self.curAttackAction = -1
        self.numExplodedLoads = 0
        self.curLoadExploded = False
        # self.DisablePhysics()


class BossMetalArmLoad(DummyObject):
    def __init__(self, prototype_info_object):
        DummyObject.__init__(self, prototype_info_object)
        self.health = prototype_info_object.maxHealth
        self.collisionMode = 0


class Boss02(ComplexPhysicObj):
    def __init__(self, prototype_info_object):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.stateInfos = prototype_info_object.stateInfos
        self.numState = -2
        self.moveState = 0
        self.containerId = -1
        # self.DisablePhysics()


class BossArm(VehiclePart):
    def __init__(self, prototype_info_object):
        VehiclePart.__init__(self, prototype_info_object)
        self.turningSpeed = prototype_info_object.turningSpeed
        self.loadProrotypeIds = []
        self.attackState = 0
        self.loadObjId = -1
        self.dirForCharging = deepcopy(INITIAL_OBJECTS_DIRECTION)
        self.numExplodedLoads = 0
        self.curLoadExploded = 0
        self.curAttackAction = -1
        self.curLoadVelocity = deepcopy(ZERO_VECTOR)


class Boss02Arm(BossArm):
    def __init__(self, prototype_info_object):
        BossArm.__init__(self, prototype_info_object)
        self.customState = 0
        self.containerId = -1
        self.relPosForContainerPickUp = deepcopy(ZERO_VECTOR)
        self.relPosForContainerPutDown = deepcopy(ZERO_VECTOR)
        self.effectsEnabled = True
        # self.SetNodeAction()


class Boss03Part(VehiclePart):
    def __init__(self, prototype_info_object):
        VehiclePart.__init__(self, prototype_info_object)
        self.isDamageable = False


class Boss03(AnimatedComplexPhysicObj):
    def __init__(self, prototype_info_object):
        AnimatedComplexPhysicObj.__init__(self, prototype_info_object)
        self.heath = prototype_info_object.maxHealth
        self.pointsForDrones = []
        self.pointsForShooting = []
        self.pathNameForFlyingWithWings = ""
        self.linearVelocity = deepcopy(ZERO_VECTOR)
        self.relAngularVelocity = deepcopy(ZERO_VECTOR)
        self.liveStatus = 4
        self.droneSpawningStatus = 0
        self.dronePlacingTimeout = 0.0
        self.shootingTimeout = 0.0
        self.pathTrackingStatus = 0
        self.desiredDestination = deepcopy(ZERO_VECTOR)
        self.desiredDirection = deepcopy(INITIAL_OBJECTS_DIRECTION)
        self.droneTeam = 0
        self.currentFlyPath = 0
        self.currentFlyTime = 0.0
        self.keyPartsMaxDurability = 0.0
        # self.DisablePhysics()
        self.physicState = 1
        # self.SetCorrectEnabledCellsCounter()
        # self.EnableGeometry()


class Boss04(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.stations = []
        self.drones = []
        self.pathNamesForDrones = []
        self.state = 0
        # self.DisablePhysics()


class Boss04Drone(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.flyPathName = ""
        self.currentFlyPath = 0
        self.currentFlyTime = 0.0
        self.customControl = False


class Boss04Part(VehiclePart):
    def __init__(self, prototype_info_object=None):
        VehiclePart.__init__(self, prototype_info_object)
        self.isDamageable = False


class Boss04Station(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.destroyed = False
        # self.DisablePhysics()


class Boss04StationPart(VehiclePart):
    def __init__(self, prototype_info_object=None):
        VehiclePart.__init__(self, prototype_info_object)
        self.meshGroupInfos = []
        self.prevMeshGroupInfos = []


class BlastWave(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.waveForceIntensity = prototype_info_object.waveForceIntensity
        self.waveDamageIntensity = prototype_info_object.waveDamageIntensity
        self.rocketExplosionType = 0
        self.effectNode = 0
        self.frameWhenCreated = 0
        self.emitterId = -1
        self.collider = False


class Gun(VehiclePart):
    def __init__(self, prototype_info_object):
        VehiclePart.__init__(self, prototype_info_object)
        self.lowStopAngle = prototype_info_object.lowStopAngle
        self.highStopAngle = prototype_info_object.highStopAngle
        self.damage = prototype_info_object.damage
        self.shellPrototypeId = prototype_info_object.shellPrototypeId
        self.damageType = prototype_info_object.damageType
        self.firingRate = prototype_info_object.firingRate
        self.firingRange = prototype_info_object.firingRange
        self.recoilForce = prototype_info_object.recoilForce
        self.turningSpeed = prototype_info_object.turningSpeed
        self.chargeSize = prototype_info_object.chargeSize
        self.reChargingTime = prototype_info_object.reChargingTime
        self.reChargingTimePerShell = prototype_info_object.reChargingTimePerShell
        self.shellsInPool = prototype_info_object.shellsPoolSize
        self.currentDesiredAlpha = 1000000.0
        self.curBarrelIndex = 0
        self.isFiring = False
        self.chargeState = 0
        self.barrelNode = 0
        self.wasShot = False
        self.justShot = False
        self.leftStopAngle = 0.0
        self.rightStopAngle = 0.0
        self.targetObjId = -1
        self.timeFromLastShot = 1000.0
        self.currentReChargingTime = 0.0
        self.shellsInCurrentCharge = self.chargeSize
        self.initialHorizAngle = 0.0


class CompoundVehiclePart(VehiclePart):
    def __init__(self, prototype_info_object):
        VehiclePart.__init__(self, prototype_info_object)
        self.vehicleParts = []


class CompoundGun(CompoundVehiclePart):
    def __init__(self, prototype_info_object):
        CompoundVehiclePart.__init__(self, prototype_info_object)


class BulletLauncher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)
        self.numBulletsInShot = prototype_info_object.numBulletsInShot
        self.groupingAngle = prototype_info_object.groupingAngle
        self.numBulletsToTracer = 0


class RocketLauncher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class RocketVolleyLauncher(RocketLauncher):
    def __init__(self, prototype_info_object):
        RocketLauncher.__init__(self, prototype_info_object)
        self.hadToLaunch = []
        self.isVolleyFiring = False


class ThunderboltLauncher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)
        self.enemies = []


class PlasmaBunchLauncher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class Mortar(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class MortarVolleyLauncher(Mortar):
    def __init__(self, prototype_info_object):
        Mortar.__init__(self, prototype_info_object)


class LocationPusher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class MinePusher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class TurboAccelerationPusher(Gun):
    def __init__(self, prototype_info_object):
        Gun.__init__(self, prototype_info_object)


class Shell(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.gunObjId = -1
        self.emittedObjId = -1


class Rocket(Shell):
    def __init__(self, prototype_info_object):
        Shell.__init__(self, prototype_info_object)
        self.velocity = prototype_info_object.velocity
        self.lifeTime = prototype_info_object.flyTime
        self.minTurningRadius = prototype_info_object.minTurningRadius
        self.physicState = 1
        # self.DisablePhysics()
        # self.SetCorrectEnabledCellsCounter()
        # self.EnableGeometry()
        self.targetObjId = -1
        self.withAngleLimit = 1
        self.numCircles = 0


class PlasmaBunch(Shell):
    def __init__(self, prototype_info_object):
        Shell.__init__(self, prototype_info_object)
        self.velocity = prototype_info_object.velocity
        self.lifeTime = prototype_info_object.flyTime
        self.physicState = 1
        # self.DisablePhysics()
        # self.SetCorrectEnabledCellsCounter()
        # self.EnableGeometry()


class MortarShell(Shell):
    def __init__(self, prototype_info_object):
        Shell.__init__(self, prototype_info_object)
        self.lifeTime = prototype_info_object.flyTime
        self.physicState = 1
        # self.DisablePhysics()
        # self.SetCorrectEnabledCellsCounter()
        # self.EnableGeometry()


class Mine(Rocket):
    def __init__(self, prototype_info_object):
        Rocket.__init__(self, prototype_info_object)
        self.TL = 0.0
        self.yVelocity = 0.0
        # sefl.EnableGeometry()


class Thunderbolt(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.lifeTime = prototype_info_object.flyTime
        self.origin = deepcopy(ZERO_VECTOR)
        self.origin["masterPoints"] = []
        self.targets = []
        self.segments = []


class Bullet(Shell):
    def __init__(self, prototype_info_object):
        Shell.__init__(self, prototype_info_object)
        self.tracet = 0
        self.parentBarrel = 0
        self.framesToLive = 1


class TemporaryLocation(Location):
    def __init__(self, prototype_info_object):
        Location.__init__(self, prototype_info_object)
        self.temporaryLocationState = 0
        self.isActive = False
        self.TL = 0.0


class SmokeScreenLocation(TemporaryLocation):
    def __init__(self, prototype_info_object):
        TemporaryLocation.__init__(self, prototype_info_object)


class NailLocation(TemporaryLocation):
    def __init__(self, prototype_info_object):
        TemporaryLocation.__init__(self, prototype_info_object)


class EngineOilLocation(TemporaryLocation):
    def __init__(self, prototype_info_object):
        TemporaryLocation.__init__(self, prototype_info_object)


class Submarine(DummyObject):
    def __init__(self, prototype_info_object):
        DummyObject.__init__(self, prototype_info_object)
        self.entryPath = {"vehiclePoints": [],
                          "cameraPoints": []}
        self.nextMap = ""
        self.nextMapLocation = ""
        self.physicState = 1
        # self.SetCorrectEnabledCellsCounter()
        self.EnableGeometry()
        self.linearVelocity = deepcopy(ZERO_VECTOR)
        self.nextMapAngle = -1


class Building(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.npcs = []

    def GetBuildingTypeByName(name):
        return BUILDING_TYPE.get(name)


class Bar(Building):
    def __init__(self, prototype_info_object):
        Building.__init__(self, prototype_info_object)
        self.barmanId = -1


class Workshop(Building):
    def __init__(self, prototype_info_object):
        Building.__init__(self, prototype_info_object)
        self.repositories = []
        self.articles = []
        self.originalObjectsInRepository = []
        priceCoeffProvider = WorkshopPriceCoeffProvider(self)
        self.priceCoeffProvider = priceCoeffProvider


class WorkshopPriceCoeffProvider(object):
    def __init__(self, workshop: Workshop):
        self.workshop = workshop


class Ware(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.maxItems = prototype_info_object.maxItems
        self.durability = prototype_info_object.maxDurability


class BreakableObject(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.removingEffectName = ""
        self.connectedRopes = []
        # self.DisablePhysics()
        self.state = 0
        self.destroyable = prototype_info_object.destroyable
        self.criticalHitEnergy = prototype_info_object.criticalHitEnergy
        # DynamicScene.GetBoEffectTypeByName(prototype_info_object.effectType)
        self.effectType = f"Placeholder for {prototype_info_object.effectType}!"
        # DynamicScene.GetBoEffectTypeByName(prototype_info_object.destroyEffectType)
        self.destroyEffectType = f"Placeholder for {prototype_info_object.destroyEffectType}!"
        self.jointId = 0
        self.positioningOnGround = 1
        self.causePos = {"x": 0.0, "y": 0.0}
        self.auseForce = 0.0
        self.initVelocities = 0
        # self.SetStaticCollision()


class ParticleSplinter(DummyObject):
    def __init__(self, prototype_info_object):
        DummyObject.__init__(self, prototype_info_object)
        # self.TransferToSpace()


class VehicleSplinter(DummyObject):
    def __init__(self, prototype_info_object):
        DummyObject.__init__(self, prototype_info_object)


class PhysicUnit(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.walkSpeed = prototype_info_object.walkSpeed
        self.turnSpeed = prototype_info_object.turningSpeed
        self.maxStandTime = prototype_info_object.maxStandTime
        self.pathsMap = []
        self.curPathName = []
        self.State = 0
        self.causePos = deepcopy(ZERO_VECTOR)
        self.causeForce = 0.0
        self.initVelocities = 0
        self.curWayPointNum = 0
        self.prevWayPoint = deepcopy(ZERO_VECTOR)
        self.walkState = 0
        self.curPath = 0
        self.mustChangePath = False
        self.mustWalk = True
        logger.info("Partially implemented PhysicUnit class")


class Wheel(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.jointID = 0
        self.driven = 1
        self.steering = 0
        self.splashEffect = 0
        self.splashType = 0
        self.makeSplash = 0
        # DynamicScene.GetWheelTypeByName(prototype_info_object.typeName)
        self.wheelType = f"Placeholder type for {prototype_info_object.typeName}!"
        self.modelBroken = False
        self.suspencionNode = 0
        self.curAngle = 0.0
        self.initialRotation = deepcopy(IDENTITY_QUATERNION)


class JointedObj(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.membersSpace = 0
        self.members = []
        self.extraMembers = []
        self.joints = []
        self.jointsIndices = []
        self.externalJoints = []
        self.externalJointsInfo = []
        self.onLoad = 0
        self.jointToGeom = []
        self.modelName = ""
        self.mass = 10.0
        self.node = 0
        self.model = 0
        self.anim = 0
        self.strech = 1.0
        self.position = deepcopy(ZERO_VECTOR)
        self.enabled = 0
        self.dataForLoad = []
        self.edataForLoad = []
        self.asRope = 0
        self.splineNeighbours = []
        self.deadTimerActive = []
        self.testVisibility = 0
        self.disableTimerActive = 0
        self.deadTimer = 0.0
        self.disableTimer = 0.0


class CompositeObj(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.members = []
        self.boneToGeom = []
        self.bonesIndices = []
        self.joints = []
        self.connections = []
        self.modelName = ""
        self.mass = 10.0
        self.node = 0
        self.Model = 0
        self.Anim = 0
        self.position = deepcopy(ZERO_VECTOR)
        self.enabled = 0
        self.dataForLoad = []
        self.initialNodeTransform = 1.0
        self.deadTimerActive = 0
        self.deadTimer = 0.0
        self.testVisibility = 0


class GeomObj(PhysicObj):
    def __init__(self, prototype_info_object):
        PhysicObj.__init__(self, prototype_info_object)
        self.pGeom = 0
        self.mass = 0.0


class RopeObj(SimplePhysicObj):
    def __init__(self, prototype_info_object):
        SimplePhysicObj.__init__(self, prototype_info_object)
        self.posts = []
        self.strech = 1.0
        self.tiePoses = []
        self.tiedObjPoses = []
        self.tieObjects = []
        post = self.Post()
        self.dummyPost = post
        # self.DisablePhysics()
        # self.DisableGeometry()

    class Post(object):
        def __init__(self):
            self.serverObjName = ""
            self.lpName = ""
            self.nodesNamesHierarchy = []
            self.postNode = 0
            self.postObj = 0
            self.postTiePos = deepcopy(ZERO_VECTOR)


class Npc(Obj):
    def __init__(self, prototype_info_object):
        Obj.__init__(self, prototype_info_object)
        self.npcType = 1
        self.modelName = ""
        self.skinNumber = 0
        self.cfgNumber = 0
        self.helloReplyNames = []
        self.spokenCount = 0


class Article(object):
    def __init__(self, xmlFile, xmlNode, thePrototypeManager):
        self.prototypeName = ""
        self.basePrice = 0
        self.sellable = False
        self.amount = 0
        self.amountDynamic = 0
        self.priceDynamic = 0
        self.prototypeId = -1

        self.dispersion = 0.0
        self.externalPriceCoefficient = 1.0
        self.randomPriceCoefficient = -1.0
        self.runtimePriceCoefficient = 1.0

        self.buyable = True

        self.minCount = -1
        self.maxCount = -1

        self.regenerationPeriod = 0  # maybe 300 is better default ???
        self.afterLastRegeneration = 0.0

        self.prototypeName = safe_check_and_set(self.prototypeName, xmlNode, "Prototype")
        self.LoadFromXML(xmlFile, xmlNode, thePrototypeManager)

        # self.ReadDefaultCountFromPrototype(thePrototypeManager)
        # self.ReadFromPrototype(thePrototypeManager)  # whyyyyyyy second time, some stupid overwrite ???
        # if self.randomPriceCoefficient < 0.0:
        #     dispersion_percentage = self.dispersion * 0.01
        #     self.randomPriceCoefficient = f"Randomized value based on dispersion: {dispersion_percentage}"
        # if self.sellable or self.buyable:
        #     self.priceDynamic = True
        #     self.amountDynamic = True

    def LoadFromXML(self, xmlFile, xmlNode, thePrototypeManager):
        self.prototypeId = safe_check_and_set(self.prototypeId, xmlNode, "PrototypeId", "int")
        basePrice = safe_check_and_set(self.basePrice, xmlNode, "BasePrice", "int")
        if basePrice >= 0:
            self.basePrice = basePrice
        self.dispersion = safe_check_and_set(self.dispersion, xmlNode, "Dispersion", "float")
        if self.dispersion < 0.0 or self.dispersion > 100.0:
            logger.error(f"Dispersion is outside expected range, should be between 0 and 100. "
                         f" For prototype {self.prototypeName}")
        self.externalPriceCoefficient = safe_check_and_set(self.externalPriceCoefficient, xmlNode,
                                                           "ExternalPriceCoefficient", "float")
        self.randomPriceCoefficient = safe_check_and_set(self.randomPriceCoefficient, xmlNode,
                                                         "RandomPriceCoefficient", "float")
        self.sellable = parse_str_to_bool(read_from_xml_node(xmlNode, "Export"))
        self.buyable = parse_str_to_bool(read_from_xml_node(xmlNode, "Import"))
        amount = safe_check_and_set(self.amount, xmlNode, "Amount", "int")
        if amount >= 0:
            self.amount = amount
        self.ReadDefaultCountFromPrototype(thePrototypeManager)
        self.maxCount = safe_check_and_set(self.maxCount, xmlNode, "MaxCount", "int")
        self.minCount = safe_check_and_set(self.minCount, xmlNode, "MinCount", "int")
        self.amountDynamic = safe_check_and_set(self.amountDynamic, xmlNode, "AmountDynamic", "int")
        self.priceDynamic = safe_check_and_set(self.priceDynamic, xmlNode, "PriceDynamic", "int")
        self.regenerationPeriod = safe_check_and_set(self.regenerationPeriod, xmlNode, "RegenerationPeriod", "float")
        self.afterLastRegeneration = safe_check_and_set(self.afterLastRegeneration, xmlNode, "AfterLastRegeneration",
                                                        "float")

    def ReadFromPrototype(self, thePrototypeManager):
        prototypes = thePrototypeManager.prototypes
        prototypeId = self.prototypeId
        prototype = prototypes[prototypeId]
        if prototypes and prototypeId < len(prototypes) and prototype != 0:
            if prototype.className == "Ware":
                self.basePrice = prototype.price
                self.dispersion = prototype.priceDispersion
            else:
                self.basePrice = prototype.price
                self.dispersion = 20.0
        else:
            logger.error(f"Invalid prototype id: {self.prototypeId}")

    def ReadDefaultCountFromPrototype(self, thePrototypeManager):
        prototypes = thePrototypeManager.prototypes
        prototypeId = self.prototypeId
        prototype = prototypes[prototypeId]
        if prototypes and prototypeId < len(prototypes) and prototype != 0:
            if prototype.className == "Ware":
                self.minCount = prototype.minCount
                self.dispersion = prototype.maxCount
        else:
            logger.error(f"Invalid prototype id: {self.prototypeId}")

    def LoadArticlesFromNode(article_list, xmlFile, xmlNode, thePrototypeManager):
        articles = []
        articles = child_from_xml_node(xmlNode, "Article", do_not_warn=True)
        if articles is not None:
            for article_node in articles:
                article = Article(xmlFile, article_node, thePrototypeManager)
                article_list.append(article)

    def PostLoad(self, prototype_manager):
        if self.prototypeName:
            self.prototypeId = prototype_manager.GetPrototypeId(self.prototypeName)
            if self.prototypeId == -1:
                logger.error(f"Unknown ware prototype name {self.prototypeName}!")
        self.ReadFromPrototype(prototype_manager)
        if self.randomPriceCoefficient < 0.0:
            dispersion_percentage = self.dispersion * 0.01
            self.randomPriceCoefficient = f"Randomized value based on dispersion: {dispersion_percentage}"
        if self.sellable or self.buyable:
            self.priceDynamic = True
            self.amountDynamic = True


class Town(Settlement):
    # partilly implemented as in M113 version, should be roughly similar to original implementation
    def __init__(self, prototype_info_object):
        Settlement.__init__(self, prototype_info_object)
        self.resourceIdToCoeff = {"first": None,
                                  "second": None}
        self.buildings = []
        self.targetClasses = []
        self.gateState = 0
        self.gateTime = 0  # internal logic based on NumbercBoundedBelow, probably only matters in runtime
        self.maxDefenders = prototype_info_object.maxDefenders
        self.entryPath = "DummyCinematicPath"
        self.exitPath = "DummyCinematicPath"
        self.pointOfViewInInterface = {"x": 5.0,
                                       "y": 20.0,
                                       "z": 5.0}
        self.caravanLocationsNames = []
        self.caravanPathNames = []
        self.treasureLocationsNames = []
        self.reachLocationsNames = []
        self.destroyLocationsNames = []
        self.shouldInitializeWorkshops = True
        self.targetClasses.append("Vehicle")
        self.gateNode = 0
        self.playerEnteringTownCount = 0
        self.questsGenerated = 0
        self.vehicleShouldBeMoved = 0
        self.playerPathIndex = -1
        self.newPosForVehicle = deepcopy(ZERO_VECTOR)
        self.newDirForVehicle = deepcopy(INITIAL_OBJECTS_DIRECTION)
        self.vehicleToBeMoved = 0
        self.ruined = False
        self.timeFromLastEnterTown = 0.0
        self.oldCameraMode = 5
        self.openGateToPlayer = True


class Lair(Settlement):
    def __init__(self, prototype_info_object):
        Settlement.__init__(self, prototype_info_object)
        self.reproductTime = 30.0  # actually NumericInRangeRegenerating object, probably only matters in runtime
        self.maxAttackers = prototype_info_object.maxAttackers
        self.maxDefenders = prototype_info_object.maxDefenders
        self.flags = 4
        self.state = 0
        self.timeOut = 2.0


class RepositoryObjectsGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"


class WanderersGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"


class AffixGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"


class QuestItem(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"
