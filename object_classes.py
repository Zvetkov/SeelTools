from math import sqrt, cos, pi

from id_manager import theIdManager
from constants import STATUS_SUCCESS, INITIAL_OBJECTS_DIRECTION
from global_functions import MassSetBoxTotal

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
        self.ai = self.decisionMatrixNum  # ai::AI::SetDecisionMatrix(this_team->m_AI, prototypeInfo->m_decisionMatrixNum) ???
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


class Vehicle(ComplexPhysicObj):
    def __init__(self, prototype_info_object=None):
        ComplexPhysicObj.__init__(self, prototype_info_object)
        self.wheels = []
        self.AI = []
        self.gadgets = []


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
        self.vehiclesGeneratorPrototypeId = "PLACEHOLDER_PROTOTYPE_ID"  # should be replaced with proper Id for PrototypeManager
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


class WanderersGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"


class AffixGenerator(object):
    def __init__(self, prototype_info_object=None):
        self.not_implemented = "DummyClass"


class Formation(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.distBetweenVehicles = 30.0
        self.maxVehicles = prototype_info_object.maxVehicles
        self.linearVelocity = prototype_info_object.linearVelocity
        self.angularVelocity = prototype_info_object.angularVelocity
        self.position = [0, 0, 0]
        self.direction = INITIAL_OBJECTS_DIRECTION
        self.positions = []
        self.pPath = 0
        self.numPathPoint = -1
        self.vehicles = []


class DummyObject(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        # if prototype_info_object.disablePhysics:
        #     PhysicObj.DisablePhysics(self)
        # if prototype_info_object.disableGeometry:
        #     PhysicObj.DisableGeometry(self)
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
