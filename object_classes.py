from id_manager import theIdManager
from constants import STATUS_SUCCESS
from logger import logger


class Object(object):
    '''Base class for all game object classes'''
    def __init__(self, class_object=None):
        self.refCount = 0
        obj_id = theIdManager.GetUniqueId()
        self.name = f"Object{obj_id}"
        self.parent = 0

        self.numChildren = 0
        self.children = []  # will try to use this instead of indexes of siblings and children ???

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
        self.numChildren += 1
        # self.isChildDirty = 1  # ??? whytf do we need this?
        return STATUS_SUCCESS


class Obj(Object):
    '''Base class containing prototype info'''
    def __init__(self, prototype_info_object: None):
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


class PhysicObj(Obj):
    def __init__(self, prototype_info_object: None):
        if prototype_info_object is not None:
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


class VehicleRecollection(Obj):
    def __init__(self, prototype_info_object=None):
        Obj.__init__(self, prototype_info_object)
        self.recollectionItems = []
        self.vehicleId = -1


class DummyObject(SimplePhysicObj):
    def __init__(self, prototype_info_object=None):
        SimplePhysicObj.__init__(self, prototype_info_object)
        # if prototype_info_object.disablePhysics:
        #     PhysicObj.DisablePhysics(self)
        # if prototype_info_object.disableGeometry:
        #     PhysicObj.DisableGeometry(self)
        if self.physicBody is not None:
            logger.warn("Not implemented PhysicBody check related to modelName")


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
