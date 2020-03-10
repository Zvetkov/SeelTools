from lxml import objectify

from em_parse import read_from_xml_node, parse_str_to_bool

from logger import logger


class PrototypeInfo(object):
    def __init__(self, server):
        self.theServer = server
        self.className = ""
        self.prototypeName = ""
        self.prototypeId = -1
        self.resourceId = -1
        self.bIsUpdating = 1
        self.bVisibleInEncyclopedia = 1
        self.bApplyAffixes = 1
        self.price = 0
        self.bIsAbstract = 0
        self.parentPrototypeName = ""
        self.protoClassObject = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        if xmlNode.tag == "Prototype":
            self.prototypeName = read_from_xml_node(xmlNode, "Name")
            self.className = read_from_xml_node(xmlNode, "Class")
            strResType = read_from_xml_node(xmlNode, "ResourceType")
            self.resourceId = self.theServer.theResourceManager.GetResourceId(strResType)
            if self.resourceId == -1:
                raise(f"Error: invalid ResourceType: {strResType} for prototype {self.prototypeName}")
            self.protoClassObject = ""  # ??? (m3d::Class *)v5;
            self.bIsUpdating = parse_str_to_bool(read_from_xml_node(xmlNode, "IsUpdating"))
            self.bVisibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode, "VisibleInEncyclopedia"))
            self.bApplyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes"))
            if hasattr(xmlNode, "Price"):
                self.price = read_from_xml_node(xmlNode, "Price")
            self.bIsAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract"))
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype")
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
    # "DummyObject": DummyObjectPrototypeInfo,
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
    # "VehicleRecollection": VehicleRecollectionPrototypeInfo,
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
