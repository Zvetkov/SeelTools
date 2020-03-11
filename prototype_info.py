from lxml import objectify

from logger import logger

from em_parse import read_from_xml_node, parse_str_to_bool
from constants import STATUS_SUCCESS
from object_classes import *


class PrototypeInfo(object):
    '''Base Prototype information class'''
    def __init__(self, server):
        self.theServer = server
        self.className = ""
        self.prototypeName = ""
        self.prototypeId = -1
        self.resourceId = -1
        self.isUpdating = 1
        self.visibleInEncyclopedia = 1
        self.applyAffixes = 1
        self.price = 0
        self.isAbstract = 0
        self.parentPrototypeName = ""
        self.protoClassObject = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        if xmlNode.tag == "Prototype":
            self.prototypeName = read_from_xml_node(xmlNode, "Name")
            self.className = read_from_xml_node(xmlNode, "Class")
            self.protoClassObject = globals()[self.className]  # getting class object by name
            strResType = read_from_xml_node(xmlNode, "ResourceType")
            self.isUpdating = parse_str_to_bool(read_from_xml_node(xmlNode, "IsUpdating"))
            self.resourceId = self.theServer.theResourceManager.GetResourceId(strResType)
            if self.resourceId == -1:
                logger.error(f"Error: invalid ResourceType: {strResType} for prototype {self.prototypeName}")
            self.visibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode, "VisibleInEncyclopedia"))
            self.applyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes"))
            price = read_from_xml_node(xmlNode, "Price")
            if price is not None:
                self.price = read_from_xml_node(xmlNode, "Price")
            self.isAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract"))
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype")
            return STATUS_SUCCESS
        else:
            logger.warning(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")


class AffixGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.affixDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        for affix in xmlNode["Affix"].iterchildren():
            self.affixDescriptions.append(read_from_xml_node(affix, "AffixName"))

    def GenerateAffixesForObj(self, obj, desiredNumAffixed):
        pass

    # class AffixDescription(object):
    #     def __init__(self):
    #         self.affixName = ""
    # trying to replace with simple dict ??? why do we need this class?

    class ModificationInfo(object):
        def __init__(self):
            self.pass_id = 0
            # raise NotImplementedError('Not implemmented ModificationInfo initiatilization')






class PhysicObjPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        self.intersectionRadius = 0.0
        self.lookRadius = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            intersectionRadius = read_from_xml_node(xmlNode, "IntersectionRadius")
            if intersectionRadius is not None:
                self.intersectionRadius = intersectionRadius
            lookRadius = read_from_xml_node(xmlNode, "LookRadius")
            if lookRadius is not None:
                self.lookRadius = lookRadius
            return STATUS_SUCCESS


class SimplePhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self):
        PhysicObjPrototypeInfo.__init__(self)
        self.collisionInfos = []
        self.collisionTrimeshAllowed = 0
        self.geomType = 0
        self.engineModelName = ""
        self.size = []  # ZeroVector ???
        self.radius = 1.0
        self.massValue = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass


class DummyObjectPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass


class VehicleRecollectionPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        return PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode) == STATUS_SUCCESS


class somethingPrototypeInfo(PrototypeInfo):
    def __init__(self):
        PrototypeInfo.__init__(self)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        pass


thePrototypeInfoClassDict = {
    "AffixGenerator": AffixGeneratorPrototypeInfo,
    # "ArticulatedVehicle": ArticulatedVehiclePrototypeInfo,
    # "Bar": BarPrototypeInfo,
    # "Barricade": BarricadePrototypeInfo,
    # "Basket": BasketPrototypeInfo,
    # "BlastWave": BlastWavePrototypeInfo,
    # "Boss02Arm": Boss02ArmPrototypeInfo,
    # "Boss02": Boss02PrototypeInfo,
    # "Boss03Part": Boss03PartPrototypeInfo,
    # "Boss03": Boss03PrototypeInfo,
    # "Boss04Drone": Boss04DronePrototypeInfo,
    # "Boss04Part": Boss04PartPrototypeInfo,
    # "Boss04": Boss04PrototypeInfo,
    # "Boss04StationPart": Boss04StationPartPrototypeInfo,
    # "Boss04Station": Boss04StationPrototypeInfo,
    # "BossMetalArmLoad": BossMetalArmLoadPrototypeInfo,
    # "BossMetalArm": BossMetalArmPrototypeInfo,
    # "BreakableObject": BreakableObjectPrototypeInfo,
    # "Building": BuildingPrototypeInfo,
    # "BulletLauncher": BulletLauncherPrototypeInfo,
    # "Bullet": BulletPrototypeInfo,
    # "Cabin": CabinPrototypeInfo,
    # "CaravanTeam": CaravanTeamPrototypeInfo,
    # "Chassis": ChassisPrototypeInfo,
    # "Chest": ChestPrototypeInfo,
    # "CinematicMover": CinematicMoverPrototypeInfo,
    # "CompositeObj": CompositeObjPrototypeInfo,
    # "CompoundGun": CompoundGunPrototypeInfo,
    # "CompoundVehiclePart": CompoundVehiclePartPrototypeInfo,
    "DummyObject": DummyObjectPrototypeInfo,
    # "DynamicQuestConvoy": DynamicQuestConvoyPrototypeInfo,
    # "DynamicQuestDestroy": DynamicQuestDestroyPrototypeInfo,
    # "DynamicQuestHunt": DynamicQuestHuntPrototypeInfo,
    # "DynamicQuestPeace": DynamicQuestPeacePrototypeInfo,
    # "DynamicQuestReach": DynamicQuestReachPrototypeInfo,
    # "EngineOilLocation": EngineOilLocationPrototypeInfo,
    # "Formation": FormationPrototypeInfo,
    # "Gadget": GadgetPrototypeInfo,
    # "GeomObj": GeomObjPrototypeInfo,
    # "InfectionLair": InfectionLairPrototypeInfo,
    # "InfectionTeam": InfectionTeamPrototypeInfo,
    # "InfectionZone": InfectionZonePrototypeInfo,
    # "JointedObj": JointedObjPrototypeInfo,
    # "Lair": LairPrototypeInfo,
    # "LightObj": LightObjPrototypeInfo,
    # "Location": LocationPrototypeInfo,
    # "LocationPusher": LocationPusherPrototypeInfo,
    # "Mine": MinePrototypeInfo,
    # "MinePusher": MinePusherPrototypeInfo,
    # "Mortar": MortarPrototypeInfo,
    # "MortarShell": MortarShellPrototypeInfo,
    # "MortarVolleyLauncher": MortarVolleyLauncherPrototypeInfo,
    # "NPCMotionController": NPCMotionControllerPrototypeInfo,
    # "NailLocation": NailLocationPrototypeInfo,
    # "Npc": NpcPrototypeInfo,
    # "ObjPrefab": ObjPrefabPrototypeInfo,
    # "ParticleSplinter": ParticleSplinterPrototypeInfo,
    # "PhysicUnit": PhysicUnitPrototypeInfo,
    # "PlasmaBunchLauncher": PlasmaBunchLauncherPrototypeInfo,
    # "PlasmaBunch": PlasmaBunchPrototypeInfo,
    # "Player": PlayerPrototypeInfo,
    # "QuestItem": QuestItemPrototypeInfo,
    # "RadioManager": RadioManagerPrototypeInfo,
    # "RepositoryObjectsGenerator": RepositoryObjectsGeneratorPrototypeInfo,
    # "RocketLauncher": RocketLauncherPrototypeInfo,
    # "Rocket": RocketPrototypeInfo,
    # "RocketVolleyLauncher": RocketVolleyLauncherPrototypeInfo,
    # "RopeObj": RopeObjPrototypeInfo,
    # "SgNodeObj": SgNodeObjPrototypeInfo,
    # "SmokeScreenLocation": SmokeScreenLocationPrototypeInfo,
    # "StaticAutoGun": StaticAutoGunPrototypeInfo,
    # "Submarine": SubmarinePrototypeInfo,
    # "Team": TeamPrototypeInfo,
    # "TeamTacticWithRoles": TeamTacticWithRolesPrototypeInfo,
    # "ThunderboltLauncher": ThunderboltLauncherPrototypeInfo,
    # "Thunderbolt": ThunderboltPrototypeInfo,
    # "Town": TownPrototypeInfo,
    # "Trigger": TriggerPrototypeInfo,
    # "TurboAccelerationPusher": TurboAccelerationPusherPrototypeInfo,
    # "VagabondTeam": VagabondTeamPrototypeInfo,
    # "VehiclePart": VehiclePartPrototypeInfo,
    # "Vehicle": VehiclePrototypeInfo,
    "VehicleRecollection": VehicleRecollectionPrototypeInfo,
    # "VehicleRoleBarrier": VehicleRoleBarrierPrototypeInfo,
    # "VehicleRoleCheater": VehicleRoleCheaterPrototypeInfo,
    # "VehicleRoleCoward": VehicleRoleCowardPrototypeInfo,
    # "VehicleRoleMeat": VehicleRoleMeatPrototypeInfo,
    # "VehicleRoleOppressor": VehicleRoleOppressorPrototypeInfo,
    # "VehicleRolePendulum": VehicleRolePendulumPrototypeInfo,
    # "VehicleRoleSniper": VehicleRoleSniperPrototypeInfo,
    # "VehicleSplinter": VehicleSplinterPrototypeInfo,
    # "VehiclesGenerator": VehiclesGeneratorPrototypeInfo,
    # "WanderersGenerator": WanderersGeneratorPrototypeInfo,
    # "WanderersManager": WanderersManagerPrototypeInfo,
    # "Ware": WarePrototypeInfo,
    # "Wheel": WheelPrototypeInfo,
    # "Workshop": WorkshopPrototypeInfo
}
