from lxml import objectify

from logger import logger

from em_parse import read_from_xml_node, parse_str_to_bool, child_from_xml_node
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
            strResType = read_from_xml_node(xmlNode, "ResourceType", do_not_warn=True)
            self.isUpdating = parse_str_to_bool(read_from_xml_node(xmlNode, "IsUpdating", do_not_warn=True))
            if strResType is not None:
                self.resourceId = self.theServer.theResourceManager.GetResourceId(strResType)
            if self.resourceId == -1:
                logger.warn(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName}")
            self.visibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode,
                                                                              "VisibleInEncyclopedia",
                                                                              do_not_warn=True))
            self.applyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes", do_not_warn=True))
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price = read_from_xml_node(xmlNode, "Price")
            self.isAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract", do_not_warn=True))
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype", do_not_warn=True)
            return STATUS_SUCCESS
        else:
            logger.warning(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")


class AffixGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.affixDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            for affix in xmlNode["Affix"].iterchildren():
                self.affixDescriptions.append(read_from_xml_node(affix, "AffixName"))
            return STATUS_SUCCESS

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
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.intersectionRadius = 0.0
        self.lookRadius = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            intersectionRadius = read_from_xml_node(xmlNode, "IntersectionRadius", do_not_warn=True)
            if intersectionRadius is not None:
                self.intersectionRadius = intersectionRadius
            lookRadius = read_from_xml_node(xmlNode, "LookRadius", do_not_warn=True)
            if lookRadius is not None:
                self.lookRadius = lookRadius
            return STATUS_SUCCESS


class SimplePhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)
        self.collisionInfos = []
        self.collisionTrimeshAllowed = 0
        self.geomType = 0
        self.engineModelName = ""
        self.size = []  # ZeroVector ???
        self.radius = 1.0
        self.massValue = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            if mass is not None:
                self.massValue = float(mass)
            self.engineModelName = read_from_xml_node(xmlNode, "ModelFile", do_not_warn=True)
            self.collisionTrimeshAllowed = parse_str_to_bool(read_from_xml_node(xmlNode,
                                                                                "CollisionTrimeshAllowed",
                                                                                do_not_warn=True))
            return STATUS_SUCCESS


class DummyObjectPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        pass

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            pass  # skipping magic related to DisablePhysics and DisableGeometry
            return STATUS_SUCCESS


class VehicleRecollectionPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        pass

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class VehicleRolePrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            vehicleFiringRangeCoeff = read_from_xml_node(xmlNode, "FiringRangeCoeff", do_not_warn=True)
            if vehicleFiringRangeCoeff is not None:
                self.vehicleFiringRangeCoeff = vehicleFiringRangeCoeff
            return STATUS_SUCCESS


class VehicleRoleBarrierPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class VehicleRoleCheaterPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class VehicleRoleCowardPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff = 0.30000001

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class VehicleRoleMeatPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff = 0.30000001

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class VehicleRoleOppressorPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            oppressionShift = read_from_xml_node(xmlNode, "OppressionShift")
            self.oppressionShift = oppressionShift.split()
            return STATUS_SUCCESS


class VehicleRolePendulumPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            oppressionShift = read_from_xml_node(xmlNode, "OppressionShift")
            self.oppressionShift = oppressionShift.split()
            a_param = read_from_xml_node(xmlNode, "A")
            b_param = read_from_xml_node(xmlNode, "B")
            if a_param is not None:
                self.a = float(a_param)
            if b_param is not None:
                self.b = float(b_param)
            return STATUS_SUCCESS


class VehicleRoleSniperPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)

    # def LoadFromXML(self, xmlFile, xmlNode):
    #     return VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)


class TeamTacticWithRolesPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.rolePrototypeNames = []
        self.rolePrototypeIds = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            for role in xmlNode.iterchildren():
                self.rolePrototypeNames.append(read_from_xml_node(role, "Prototype"))
            return STATUS_SUCCESS


class NPCMotionControllerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class InfectionLairPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class TeamPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.decisionMatrixNum = -1
        self.decisionMatrixName = ""  # placeholder for AIManager functionality ???
        self.removeWhenChildrenDead = True
        self.formationPrototypeName = "caravanFormation"
        self.overridesDistBetweenVehicles = 0
        self.isUpdating = False
        self.formationDistBetweenVehicles = 30.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.decisionMatrixName = read_from_xml_node(xmlNode, "DecisionMatrix")
            self.removeWhenChildrenDead = parse_str_to_bool(read_from_xml_node(xmlNode, "RemoveWhenChildrenDead"))
            formation = child_from_xml_node(xmlNode, "Formation", do_not_warn=True)
            if formation is not None:
                self.formationPrototypeName = read_from_xml_node(formation, "Prototype")
                distBetweenVehicles = read_from_xml_node(formation, "DistBetweenVehicles")
                if distBetweenVehicles is not None:
                    self.overridesDistBetweenVehicles = True
                    self.formationDistBetweenVehicles = distBetweenVehicles
            return STATUS_SUCCESS


class InfectionTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.items = []
        self.vehiclesGeneratorProtoName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            vehicles = child_from_xml_node(xmlNode, "Vehicles", do_not_warn=True)
            if vehicles is not None:
                for vehicle in vehicles.iterchildren():
                    item = {"protoName": read_from_xml_node(vehicle, "PrototypeName"),
                            "count": int(read_from_xml_node(vehicle, "Count"))}
                    self.items.append(item)
            return STATUS_SUCCESS


class InfectionZonePrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.minDistToPlayer = 100.0
        self.criticalTeamDist = 1000000.0
        self.criticalTeamTime = 0.0
        self.blindTeamDist = 1000000.0
        self.blindTeamTime = 0.0
        self.dropOutSegmentAngle = 180

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            minDistToPlayer = read_from_xml_node(xmlNode, "MinDistToPlayer", do_not_warn=True)
            if minDistToPlayer is not None:
                self.minDistToPlayer = float(minDistToPlayer)

            criticalTeamDist = read_from_xml_node(xmlNode, "CriticalTeamDist", do_not_warn=True)
            if criticalTeamDist is not None:
                self.criticalTeamDist = float(criticalTeamDist)

            criticalTeamTime = read_from_xml_node(xmlNode, "CriticalTeamTime", do_not_warn=True)
            if criticalTeamTime is not None:
                self.criticalTeamTime = float(criticalTeamTime)

            blindTeamDist = read_from_xml_node(xmlNode, "BlindTeamDist", do_not_warn=True)
            if blindTeamDist is not None:
                self.blindTeamDist = float(blindTeamDist)

            blindTeamTime = read_from_xml_node(xmlNode, "BlindTeamTime", do_not_warn=True)
            if blindTeamTime is not None:
                self.blindTeamTime = float(blindTeamTime)

            dropOutSegmentAngle = read_from_xml_node(xmlNode, "DropOutSegmentAngle", do_not_warn=True)
            if dropOutSegmentAngle is not None:
                self.dropOutSegmentAngle = int(dropOutSegmentAngle)
            return STATUS_SUCCESS


class VehiclesGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.vehicleDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.desiredCountLow = -1
            self.desiredCountHigh = -1
            desiredCount = read_from_xml_node(xmlNode, "DesiredCount")
            if desiredCount is not None:
                tokensDesiredCount = desiredCount.split("-")
                token_length = len(tokensDesiredCount)
                if token_length == 2:
                    self.desiredCountLow = int(tokensDesiredCount[0])
                    self.desiredCountHigh = int(tokensDesiredCount[1])
                if token_length == 1:
                    self.desiredCountLow = int(tokensDesiredCount[0])
                    self.desiredCountHigh = self.desiredCountLow
                else:
                    logger.error(f"VehicleGenerator {self.prototypeName} attrib DesiredCount range "
                                 f"should contain one or two numbers but contains {len(tokensDesiredCount)}")
                if self.desiredCountLow > self.desiredCountHigh:
                    logger.error(f"VehicleGenerator {self.prototypeName} attrib DesiredCount range invalid: "
                                 f"{self.desiredCountLow}-{self.desiredCountHigh}, "
                                 "should be from lesser to higher number")
                if self.desiredCountHigh > 5:
                    logger.error(f"VehicleGenerator {self.prototypeName} attrib DesiredCount high value: "
                                 f"{self.desiredCountHigh} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")
            return STATUS_SUCCESS



# dict mapping Object Classes to PrototypeInfo Classes
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
    "InfectionLair": InfectionLairPrototypeInfo,
    "InfectionTeam": InfectionTeamPrototypeInfo,
    "InfectionZone": InfectionZonePrototypeInfo,
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
    "NPCMotionController": NPCMotionControllerPrototypeInfo,
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
    "TeamTacticWithRoles": TeamTacticWithRolesPrototypeInfo,
    # "ThunderboltLauncher": ThunderboltLauncherPrototypeInfo,
    # "Thunderbolt": ThunderboltPrototypeInfo,
    # "Town": TownPrototypeInfo,
    # "Trigger": TriggerPrototypeInfo,
    # "TurboAccelerationPusher": TurboAccelerationPusherPrototypeInfo,
    # "VagabondTeam": VagabondTeamPrototypeInfo,
    # "VehiclePart": VehiclePartPrototypeInfo,
    # "Vehicle": VehiclePrototypeInfo,
    "VehicleRecollection": VehicleRecollectionPrototypeInfo,
    "VehicleRoleBarrier": VehicleRoleBarrierPrototypeInfo,
    "VehicleRoleCheater": VehicleRoleCheaterPrototypeInfo,
    "VehicleRoleCoward": VehicleRoleCowardPrototypeInfo,
    "VehicleRoleMeat": VehicleRoleMeatPrototypeInfo,
    "VehicleRoleOppressor": VehicleRoleOppressorPrototypeInfo,
    "VehicleRolePendulum": VehicleRolePendulumPrototypeInfo,
    "VehicleRoleSniper": VehicleRoleSniperPrototypeInfo,
    # "VehicleSplinter": VehicleSplinterPrototypeInfo,
    "VehiclesGenerator": VehiclesGeneratorPrototypeInfo,
    # "WanderersGenerator": WanderersGeneratorPrototypeInfo,
    # "WanderersManager": WanderersManagerPrototypeInfo,
    # "Ware": WarePrototypeInfo,
    # "Wheel": WheelPrototypeInfo,
    # "Workshop": WorkshopPrototypeInfo
}
