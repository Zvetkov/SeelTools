from id_manager import theIdManager
from constants import STATUS_SUCCESS
import prototype_info
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
            Obj.__init__(self, prototype_info)
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


class VehicleRecollection(Obj):
    def __init__(self, prototype_info: prototype_info.VehicleRecollectionPrototypeInfo = None):
        Obj.__init__(self, prototype_info)
        self.recollectionItems = []
        self.vehicleId = -1
