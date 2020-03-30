from math import pi, sqrt
from copy import deepcopy
from lxml import objectify

from logger import logger

from em_parse import read_from_xml_node, parse_str_to_bool, child_from_xml_node, check_mono_xml_node
from constants import (STATUS_SUCCESS, DEFAULT_TURNING_SPEED, FiringTypesStruct, DamageTypeStruct,
                       TEAM_DEFAULT_FORMATION_PROTOTYPE, GEOM_TYPE, ZERO_VECTOR, IDENTITY_QUATERNION)
from object_classes import *
from global_functions import GetActionByName
from global_properties import theServer


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
                logger.info(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName}")
            self.visibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode,
                                                                              "VisibleInEncyclopedia",
                                                                              do_not_warn=True))
            self.applyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes", do_not_warn=True))
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price = price
            self.isAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract", do_not_warn=True))
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype", do_not_warn=True)  # ??? maybe should fallback to "" instead None
            return STATUS_SUCCESS
        else:
            logger.warning(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")


class PhysicBodyPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.engineModelName = ""
        self.massValue = 1.0
        self.collisionInfos = []
        self.collisionTrimeshAllowed = False

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.engineModelName = read_from_xml_node(xmlNode, "ModelFile")
            if self.engineModelName is None and self.prototypeName == "CompoundVehiclePart":
                logger.error(f"No model file is provided for prototype {self.prototypeName}")
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            self.collisionTrimeshAllowed = parse_str_to_bool(read_from_xml_node(xmlNode, "CollisionTrimeshAllowed"))
            if mass is not None:
                self.massValue = float(mass)
            if self.massValue < 0.001:
                logger.error(f"Mass is too low for prototype {self.prototypeName}")
            return STATUS_SUCCESS


class SimplePhysicBodyPrototypeInfo(PhysicBodyPrototypeInfo):
    def __init__(self, server):
        PhysicBodyPrototypeInfo.__init__(self, server)


class VehiclePartPrototypeInfo(PhysicBodyPrototypeInfo):
    def __init__(self, server):
        PhysicBodyPrototypeInfo.__init__(self, server)
        self.weaponPrototypeId = -1
        self.durability = 0.0
        self.loadPoints = []
        self.blowEffectName = "ET_PS_HARD_BLOW"
        self.canBeUsedInAutogenerating = True
        self.repairCoef = 1.0
        self.modelMeshes = []
        self.boundsForMeshes = []
        self.verts = []
        self.inds = []
        self.numsTris = []
        self.vertsStride = []
        self.groupHealth = []  # groupHealthes in original
        self.durabilityCoeffsForDamageTypes = [0, 0, 0]

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicBodyPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.blowEffectName = read_from_xml_node(xmlNode, "BlowEffect")
            durability = read_from_xml_node(xmlNode, "Durability", do_not_warn=True)
            if durability is not None:
                self.durability = float(durability)
            strDurabilityCoeffs = read_from_xml_node(xmlNode, "DurCoeffsForDamageTypes", do_not_warn=True)
            if strDurabilityCoeffs is not None:
                self.durabilityCoeffsForDamageTypes = [float(coeff) for coeff in strDurabilityCoeffs.split()]
                for coeff in self.durabilityCoeffsForDamageTypes:
                    if coeff < -25.1 or coeff > 25.0:
                        logger.error(f"Invalif DurCoeffsForDamageTypes:{coeff} for {self.prototypeName}, "
                                     "should be between -25.0 and 25.0")

            loadPoints = read_from_xml_node(xmlNode, "LoadPoints", do_not_warn=True)
            if loadPoints is not None and loadPoints != "":
                self.loadPoints = loadPoints.split()
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price = int(price)

            repairCoef = read_from_xml_node(xmlNode, "RepairCoef", do_not_warn=True)
            if repairCoef is not None:
                self.repairCoef = float(repairCoef)

            self.canBeUsedInAutogenerating = parse_str_to_bool(read_from_xml_node(xmlNode, "CanBeUsedInAutogenerating",
                                                                                  do_not_warn=True))
            return STATUS_SUCCESS


class GunPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.barrelModelName = ""
        self.withCharging = True
        self.withShellsPoolLimit = True
        self.shellPrototypeId = -1
        self.damage = 1.0
        self.damageType = 0
        self.firingRate = 1.0
        self.firingRange = 1.0
        self.lowStopAngle = 0.0
        self.highStopAngle = 0.0
        self.ignoreStopAnglesWhenFire = False
        self.decalId = -1
        self.recoilForce = 0.0
        self.turningSpeed = DEFAULT_TURNING_SPEED
        self.chargeSize = 20
        self.reChargingTime = 1.0
        self.reChargingTimePerShell = 0.0
        self.shellsPoolSize = 12
        self.blastWavePrototypeId = -1
        self.firingType = 0
        self.fireLpMatrices = []
        self.explosionTypeName = "BIG"
        self.shellPrototypeName = ""
        self.blastWavePrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.shellPrototypeName = read_from_xml_node(xmlNode, "BulletPrototype")
            self.blastWavePrototypeName = read_from_xml_node(xmlNode, "BlastWavePrototype")
            damage = read_from_xml_node(xmlNode, "Damage", do_not_warn=True)
            if damage is not None:
                self.damage = float(damage)

            firingRate = read_from_xml_node(xmlNode, "FiringRate", do_not_warn=True)
            if firingRate is not None:
                self.firingRate = float(firingRate)

            firingRange = read_from_xml_node(xmlNode, "FiringRange", do_not_warn=True)
            if firingRange is not None:
                self.firingRange = float(firingRange)

            self.explosionTypeName = read_from_xml_node(xmlNode, "ExplosionType")

            recoilForce = read_from_xml_node(xmlNode, "RecoilForce", do_not_warn=True)
            if recoilForce is not None:
                self.recoilForce = float(recoilForce)

            decalName = read_from_xml_node(xmlNode, "Decal")
            self.decalId = f"Placeholder for {decalName}!"  # ai::DynamicScene::AddDecalName(ai::gDynamicScene, &decalName)

            firingType = read_from_xml_node(xmlNode, "FiringType")
            self.firingType = self.Str2FiringType(firingType)
            if self.firingType is None:
                logger.warning(f"Unknown firing type: {self.firingType}!")

            damageTypeName = read_from_xml_node(xmlNode, "DamageType")
            if damageTypeName is not None:
                self.damageType = self.Str2DamageType(damageTypeName)
            if self.damageType is None:
                logger.warning(f"Unknown damage type: {self.damageType}")

            self.withCharging = parse_str_to_bool(read_from_xml_node(xmlNode, "WithCharging"))

            chargeSize = read_from_xml_node(xmlNode, "ChargeSize")
            if chargeSize is not None:
                chargeSize = int(chargeSize)
                if chargeSize >= 0:  # ??? whaaat, why should it ever be less than 0?
                    self.chargeSize = chargeSize

            reChargingTime = read_from_xml_node(xmlNode, "RechargingTime")
            if reChargingTime is not None:
                self.reChargingTime = float(reChargingTime)

            self.shellsPoolSize = 0
            shellsPoolSize = read_from_xml_node(xmlNode, "ShellsPoolSize")
            if shellsPoolSize is not None:
                shellsPoolSize = int(shellsPoolSize)
                if shellsPoolSize > 0:
                    self.shellsPoolSize = shellsPoolSize
            if shellsPoolSize <= 0:
                self.withShellsPoolLimit = 0
                self.shellsPoolSize = 12

            self.withShellsPoolLimit = parse_str_to_bool(read_from_xml_node(xmlNode, "WithShellsPoolLimit"))

            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed")
            if turningSpeed is not None:
                self.turningSpeed = float(turningSpeed)
            self.turningSpeed *= pi / 180  # convert to rads
            self.engineModelName += "Gun"  # ??? is this really what's happening?
            self.ignoreStopAnglesWhenFire = parse_str_to_bool(read_from_xml_node(xmlNode, "IgnoreStopAnglesWhenFire"))
            return STATUS_SUCCESS

    def Str2FiringType(firing_type_name: str):
        return FiringTypesStruct.get(firing_type_name)

    def Str2DamageType(damage_type_name: str):
        return DamageTypeStruct.get(damage_type_name)

    def PostLoad(self, prototype_manager):
        self.explosionType = prototype_manager.theServer.theDynamicScene.GetExplosionType(self.explosionTypeName)
        self.shellPrototypeId = prototype_manager.GetPrototypeId(self.shellPrototypeName)
        if self.shellPrototypeId is None:
            logger.error(f"Shell prototype {self.shellPrototypeId} is invalid for {self.prototypeName}")
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)
        if self.blastWavePrototypeId is None:
            logger.error(f"Unknown blastwave prototype {self.blastWavePrototypeName} for {self.prototypeName}")


class GadgetPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modifications = []
        self.modelName = ""
        self.skinNum = 0
        self.isUpdating = False

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            modifications = read_from_xml_node(xmlNode, "Modifications").split(";")
            for mod in modifications:
                pass

    class ModificationInfo(object):
        def __init__(self, prot_info, tokens=None, other_mod=None):  # other ModificationInfo object can be passed to create copy
            if other_mod is None and tokens is not None:
                self.applierInfo_applierType = 0
                self.applierInfo_targetResourceId = -1
                self.applierInfo_targetFiringType = 0
                self.propertyName = ""
                self.value = {"id": 0,
                              "w": 0,
                              "y": 0,
                              "NameFromNum": 0,
                              "NumFromName": 0}
                tokens = tokens.split(";")
                for token in tokens:
                    token_parts = token.split()
                    if "VEHICLE" in token:
                        self.applierInfo_applierType = 0
                    elif prot_info.theServer.theResourceManager.GetResourceId(token_parts[0]) == -1:
                        self.applierInfo_applierType = 2
                self.modificationType = 0
            elif other_mod is not None and tokens is None:
                self.applierInfo_applierType = other_mod.applierInfo_applierType
                self.applierInfo_targetResourceId = other_mod.applierInfo_targetResourceId
                self.applierInfo_targetFiringType = other_mod.applierInfo_targetFiringType
                self.propertyName = other_mod.propertyName
                self.numForName = int(other_mod.modificationType)
                self.value = other_mod.value  # ??? some AIParam magic in here
            logger.warn("Is ModificationInfo init partially implemented?")


class WanderersManagerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class WanderersGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.vehicleDescriptions = []
        self.desiredCountLow = -1
        self.desiredCountHigh = -1

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            desiredCount = read_from_xml_node(xmlNode, "DesiredCount")
            if desiredCount is not None:
                tokensDesiredCount = desiredCount.split("-")
                token_length = len(tokensDesiredCount)
                if token_length == 2:
                    self.desiredCountLow = int(tokensDesiredCount[0])
                    self.desiredCountHigh = int(tokensDesiredCount[1])
                elif token_length == 1:
                    self.desiredCountLow = int(tokensDesiredCount[0])
                    self.desiredCountHigh = self.desiredCountLow
                else:
                    logger.error(f"WanderersGenerator {self.prototypeName} attrib DesiredCount range "
                                 f"should contain one or two numbers but contains {len(tokensDesiredCount)}")
                if self.desiredCountLow > self.desiredCountHigh:
                    logger.error(f"WanderersGenerator {self.prototypeName} attrib DesiredCount range invalid: "
                                 f"{self.desiredCountLow}-{self.desiredCountHigh}, "
                                 "should be from lesser to higher number")
                if self.desiredCountHigh > 5:
                    logger.error(f"WanderersGenerator {self.prototypeName} attrib DesiredCount high value: "
                                 f"{self.desiredCountHigh} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")
        logger.warn("Partially implemented WanderersGeneratorPrototypeInfo LoadFromXML!")


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
        self.size = deepcopy(ZERO_VECTOR)
        self.radius = 1.0
        self.massValue = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            if mass is not None:
                self.massValue = float(mass)
            self.engineModelName = read_from_xml_node(xmlNode, "ModelFile", do_not_warn=True)  # ??? maybe should fallback to "" instead None
            self.collisionTrimeshAllowed = parse_str_to_bool(read_from_xml_node(xmlNode,
                                                                                "CollisionTrimeshAllowed",
                                                                                do_not_warn=True))
            return STATUS_SUCCESS

    def SetGeomType(self, geom_type):
        self.geomType = GEOM_TYPE[geom_type]
        if self.geomType == 6:
            return
        collision_info = CollisionInfo()
        collision_info.Init()
        if self.geomType == 1:
            collision_info.geomType = 1
            collision_info.size["x"] = self.size["x"]
            collision_info.size["y"] = self.size["y"]
            collision_info.size["z"] = self.size["z"]
        elif self.geomType == 2:
            collision_info.geomType = 2
            collision_info.radius = self.radius
        elif self.geomType == 5:
            logger.warning(f"Obsolete GeomType: TriMesh! in {self.prototypeName}")
        self.collisionInfos.append(collision_info)


class ComplexPhysicObjPartDescription(Object):
    def __init__(self, prototype_info_object=None):
        Object.__init__(self, prototype_info_object)
        self.partResourceId = -1
        self.lpNames = []
        self.child_descriptions = []  # ??? temporary placeholder for original logic

    def LoadFromXML(self, xmlFile, xmlNode):
        self.name = read_from_xml_node(xmlNode, "id")
        if self.parent is not None:
            parent_lookup = self.parent.GetChildByName(self.name)
            if parent_lookup is not None and self is parent_lookup:  # ??? can this ever be true?
                logger.warning(f"When loading PartDescription: name = {self.name} conflicts with another child")

        partResourceType = read_from_xml_node(xmlNode, "partResourceType")
        self.partResourceId = theServer.theResourceManager.GetResourceId(partResourceType)
        lpNames = read_from_xml_node(xmlNode, "lpName")
        if lpNames is not None:
            self.lpNames = lpNames.split()
        for description_node in xmlNode.iterchildren():
            part_description = ComplexPhysicObjPartDescription()
            part_description.LoadFromXML(xmlFile, description_node)
            self.child_descriptions.append(part_description)  # ??? temporary placeholder for original logic


class ComplexPhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)
        self.partPrototypeIds = []
        self.massSize = {"x": 1.0,
                         "y": 1.0,
                         "z": 1.0}
        self.massTranslation = []
        self.partDescription = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            main_part_description_node = child_from_xml_node(xmlNode, "MainPartDescription")
            if main_part_description_node is not None:
                check_mono_xml_node(main_part_description_node, "PartDescription")
                partPrototypeDescriptions = ComplexPhysicObjPartDescription()
                partPrototypeDescriptions.LoadFromXML(xmlFile, main_part_description_node)
                self.partPrototypeDescriptions = partPrototypeDescriptions
            else:
                logger.warning(f"Parts description is missing for prototype {self.prototypeName}")

            parts_node = child_from_xml_node(xmlNode, "Parts")
            if parts_node is not None:
                check_mono_xml_node(parts_node, "Parts")
                for part_node in parts_node.iterchildren():
                    prototypeId = read_from_xml_node(part_node, "id")
                    prototypeName = read_from_xml_node(part_node, "Prototype")
                    protName = {"name": prototypeName,
                                "id": prototypeId}
                    self.partPrototypeNames.append(protName)
            self.massSize = read_from_xml_node(xmlNode, "MassSize").split()
            self.massTranslation = read_from_xml_node(xmlNode, "MassTranslation").split()
            massShape = read_from_xml_node(xmlNode, "MassShape")
            if massShape is not None:
                self.massShape = int(massShape)
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


class LocationPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")  # from GEOM_TYPE const enum
            return STATUS_SUCCESS


class RadioManagerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


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


class VehicleRoleCheaterPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)


class VehicleRoleCowardPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff = 0.30000001


class VehicleRoleMeatPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff = 0.30000001


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
            self.removeWhenChildrenDead = parse_str_to_bool(read_from_xml_node(xmlNode, "RemoveWhenChildrenDead", do_not_warn=True))
            formation = child_from_xml_node(xmlNode, "Formation", do_not_warn=True)
            if formation is not None:
                self.formationPrototypeName = read_from_xml_node(formation, "Prototype")
                distBetweenVehicles = read_from_xml_node(formation, "DistBetweenVehicles")
                if distBetweenVehicles is not None:
                    self.overridesDistBetweenVehicles = True
                    self.formationDistBetweenVehicles = float(distBetweenVehicles)
            return STATUS_SUCCESS


class CaravanTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.tradersGeneratorPrototypeName = ""
        self.guardsGeneratorPrototypeName = ""
        self.waresPrototypes = []
        self.formationPrototypeName = "caravanFormation"

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.tradersGeneratorPrototypeName = read_from_xml_node(xmlNode, "TradersVehiclesGeneratorName")
            self.guardsGeneratorPrototypeName = read_from_xml_node(xmlNode, "GuardVehiclesGeneratorName")
            waresPrototypes = read_from_xml_node(xmlNode, "WaresPrototypes")
            if waresPrototypes is not None:
                self.waresPrototypes = waresPrototypes.split()
            if self.tradersGeneratorPrototypeName is not None:
                if self.waresPrototypes is None:
                    logger.error(f"No wares for caravan with traders: {self.prototypeName}")
            return STATUS_SUCCESS


class VagabondTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.vehiclesGeneratorPrototype = ""
        self.waresPrototypes = []
        self.removeWhenChildrenDead = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.vehiclesGeneratorPrototype = read_from_xml_node(xmlNode, "VehicleGeneratorPrototype")
            self.waresPrototypes = read_from_xml_node(xmlNode, "WaresPrototypes").split()
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
                elif token_length == 1:
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

                if len(xmlNode.getchildren()) > 1:
                    check_mono_xml_node(xmlNode, "Description")
                    for description_entry in xmlNode.iterchildren():
                        veh_description = self.VehicleDescription(xmlFile, description_entry)
                        self.vehicleDescriptions.append(veh_description)
                self.partOfSchwartzForCabin = 0.25
                self.partOfSchwartzForBasket = 0.25
                self.partOfSchwartzForGuns = 0.5
                self.partOfSchwartzForWares = 0.0

                partOfSchwartzForCabin = read_from_xml_node(xmlNode, "partOfSchwartzForCabin", do_not_warn=True)
                if partOfSchwartzForCabin is not None:
                    self.partOfSchwartzForCabin = float(partOfSchwartzForCabin)

                partOfSchwartzForBasket = read_from_xml_node(xmlNode, "partOfSchwartzForBasket", do_not_warn=True)
                if partOfSchwartzForBasket is not None:
                    self.partOfSchwartzForBasket = float(partOfSchwartzForBasket)

                partOfSchwartzForGuns = read_from_xml_node(xmlNode, "partOfSchwartzForGuns", do_not_warn=True)
                if partOfSchwartzForGuns is not None:
                    self.partOfSchwartzForGuns = float(partOfSchwartzForGuns)

                partOfSchwartzForWares = read_from_xml_node(xmlNode, "partOfSchwartzForWares", do_not_warn=True)
                if partOfSchwartzForWares is not None:
                    self.partOfSchwartzForWares = float(partOfSchwartzForWares)
            return STATUS_SUCCESS

    class VehicleDescription(object):
        def __init__(self, xmlFile, xmlNode):
            self.vehiclePrototypeIds = []
            self.waresPrototypesIds = []
            self.vehiclePrototypeNames = []
            self.waresPrototypesNames = []
            self.gunAffixGeneratorPrototypeName = ""
            self.LoadFromXML(xmlFile, xmlNode)

        def LoadFromXML(self, xmlFile, xmlNode):
            self.partOfSchwartz = -1.0
            partOfSchwartz = read_from_xml_node(xmlNode, "PartOfSchwartz", do_not_warn=True)
            if partOfSchwartz is not None:
                self.partOfSchwartz = float(partOfSchwartz)
            self.tuningBySchwartz = self.partOfSchwartz > 0.0

            vehiclesPrototypes = read_from_xml_node(xmlNode, "VehiclesPrototypes")
            if vehiclesPrototypes is not None:
                self.vehiclePrototypeNames = vehiclesPrototypes.split()

            waresPrototypesNames = read_from_xml_node(xmlNode, "WaresPrototypes")
            if waresPrototypesNames is not None:
                self.waresPrototypesNames = waresPrototypesNames.split()

            self.gunAffixGeneratorPrototypeName = read_from_xml_node(xmlNode, "GunAffixGeneratorPrototype")

        def PostLoad(self, prototype_manager):
            for vehicle_prot_name in self.vehiclePrototypeNames:
                vehicleProt = prototype_manager.prototypesMap.get(vehicle_prot_name)
                if vehicleProt is None:
                    logger.error(f"Unknown vehicle prototype name: {vehicle_prot_name}")
                if prototype_manager.IsPrototypeOf(vehicleProt, "Vehicle"):
                    pass  # ???
            logger.warning("Not fully implemented PostLoad for VehiclesGeneratorPrototypeInfo VehicleDescription")


class FormationPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.maxVehicles = 5
        self.polylinePoints = []
        self.polylineLength = 0.0
        self.headOffset = 0.0
        self.linearVelocity = 100.0
        self.headPosition = 0
        self.isUpdating = False
        self.angularVelocity = 0.5

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            linearVelocity = read_from_xml_node(xmlNode, "LinearVelocity", do_not_warn=True)
            if linearVelocity is not None:
                self.linearVelocity = float(linearVelocity)

            angularVelocity = read_from_xml_node(xmlNode, "AngularVelocity", do_not_warn=True)
            if angularVelocity is not None:
                self.angularVelocity = float(angularVelocity)

            self.LoadPolylinePoints(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.CalcPolylineLengths()

    def CalcPolylineLengths(self):
        self.polylineLength = 0.0
        self.headOffset = 0.0
        if self.polylinePoints:
            for i in range(len(self.polylinePoints) - 1):
                first_point = self.polylinePoints[i]
                second_point = self.polylinePoints[i + 1]
                x_change = first_point.x - second_point.x
                y_change = first_point.y - second_point.y
                segmentLength = sqrt(x_change**2 + y_change**2)
                self.polylineLength += segmentLength
                if i < self.headPosition:
                    self.headOffset += segmentLength

    def LoadPolylinePoints(self, xmlFile, xmlNode):
        polyline = child_from_xml_node(xmlNode, "Polyline")
        if polyline is not None:
            check_mono_xml_node(xmlNode["Polyline"], "Point")
            for child in xmlNode["Polyline"].iterchildren():
                point = read_from_xml_node(child, "Coord").split()
                if len(point) == 2:
                    point = {"x": float(point[0]),
                             "y": float(point[1])}
                    if point["x"] == 0.0 or point["y"] == 0.0:
                        if self.polylinePoints:
                            self.headPosition = self.polylinePoints[-1]
                        else:
                            self.headPosition = 0
                        self.polylinePoints.append(point)
                else:
                    logger.error(f"Unexpected coordinate format for Formation {self.prototypeName}, expect two numbers")


class SettlementPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.zoneInfos = []
        self.vehiclesPrototypeId = -1
        self.vehiclesPrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            zone_info = self.AuxZoneInfo()
            zone_info.action = read_from_xml_node(xmlNode, "action", do_not_warn=True)
            offset = read_from_xml_node(xmlNode, "offset", do_not_warn=True)
            if offset is not None:
                offset = offset.split()
                zone_info.offset["x"] = offset[0]
                zone_info.offset["y"] = offset[1]
                zone_info.offset["z"] = offset[2]
            zone = read_from_xml_node(xmlNode, "zone", do_not_warn=True)
            if zone is not None:
                radius = read_from_xml_node(xmlNode["zone"], "radius", do_not_warn=True)
                zone_info.radius = float(radius)
            self.zoneInfos.append[zone_info]
            self.vehiclesPrototypeName = read_from_xml_node(xmlNode, "Vehicles")
            return STATUS_SUCCESS

    class AuxZoneInfo(object):
        def __init__(self):
            self.action = ""
            self.offset = deepcopy(ZERO_VECTOR)
            self.radius = 10.0


class PlayerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modelName = ""
        self.skinNumber = 0
        self.cfgNumber = 0
        # ??? some magic with World SceneGraph

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.modelName = read_from_xml_node(xmlNode, "ModelFile")
            skinNum = read_from_xml_node(xmlNode, "SkinNum", do_not_warn=True)
            if skinNum is not None:
                skinNum = int(skinNum)
                if skinNum > 0:
                    self.skinNumber = skinNum

            cfgNum = read_from_xml_node(xmlNode, "CfgNum", do_not_warn=True)
            if cfgNum is not None:
                cfgNum = int(cfgNum)
                if cfgNum > 0:
                    self.cfgNumber = cfgNum
            return STATUS_SUCCESS


class TriggerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class CinematicMoverPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class DynamicQuestPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.minReward = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            minReward = read_from_xml_node(xmlNode, "MinReward")
            if minReward is not None:
                self.minReward = int(minReward)
            return STATUS_SUCCESS


class DynamicQuestConvoyPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = 0.0
        self.criticalDistFromPlayer = 100.0
        self.criticalTime = 20.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, "PlayerSchwarzPart")
            if playerSchwarzPart is not None:
                self.playerSchwarzPart = float(playerSchwarzPart)

            criticalDistFromPlayer = read_from_xml_node(xmlNode, "CriticalDistFromPlayer")
            if criticalDistFromPlayer is not None:
                self.criticalDistFromPlayer = float(criticalDistFromPlayer)

            criticalTime = read_from_xml_node(xmlNode, "CriticalTime")
            if criticalTime is not None:
                self.criticalTime = float(criticalTime)

            return STATUS_SUCCESS


class DynamicQuestDestroyPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        targetSchwarzPart = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            targetSchwarzPart = read_from_xml_node(xmlNode, "TargetSchwarzPart")
            if targetSchwarzPart is not None:
                self.targetSchwarzPart = float(targetSchwarzPart)
            return STATUS_SUCCESS


class DynamicQuestHuntPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, "PlayerSchwarzPart")
            if playerSchwarzPart is not None:
                self.playerSchwarzPart = float(playerSchwarzPart)

            huntSeasonLength = read_from_xml_node(xmlNode, "HuntSeasonLength")
            if huntSeasonLength is not None:
                self.huntSeasonLength = float(huntSeasonLength)
            return STATUS_SUCCESS


class DynamicQuestPeacePrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerMoneyPart = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerMoneyPart = read_from_xml_node(xmlNode, "PlayerMoneyPart")
            if playerMoneyPart is not None:
                self.playerMoneyPart = float(playerMoneyPart)
            return STATUS_SUCCESS


class DynamicQuestReachPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, "PlayerSchwarzPart")
            if playerSchwarzPart is not None:
                self.playerSchwarzPart = float(playerSchwarzPart)
            return STATUS_SUCCESS


class SgNodeObjPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.engineModelName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.engineModelName = read_from_xml_node(xmlNode, "ModelFile")
            return STATUS_SUCCESS


class LightObjPrototypeInfo(SgNodeObjPrototypeInfo):
    def __init__(self, server):
        SgNodeObjPrototypeInfo.__init__(self, server)
        self.isUpdating = False


class BossArmPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.frameToPickUpLoad = 0
        self.turningSpeed = 0.5
        self.lpIdForLoad = -1
        self.cruticalNumExplodedLoads = 1
        self.attacks = []

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed", do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed = float(turningSpeed)

            frameToPickUpLoad = read_from_xml_node(xmlNode, "FrameToPickUpLoad", do_not_warn=True)
            if frameToPickUpLoad is not None:
                self.frameToPickUpLoad = int(frameToPickUpLoad)

            attack_actions = child_from_xml_node(xmlNode, "AttackActions")
            check_mono_xml_node(attack_actions, "Attack")
            for attack_node in attack_actions.iterchildren():
                action = self.AttackActionInfo()
                action.LoadFromXML(attack_node)
                self.attacks.append(action)

            cruticalNumExplodedLoads = read_from_xml_node(xmlNode, "CriticalNumExplodedLoads", do_not_warn=True)
            if cruticalNumExplodedLoads is not None:
                self.cruticalNumExplodedLoads = int(cruticalNumExplodedLoads)
            return STATUS_SUCCESS

    class AttackActionInfo(object):
        def __init__(self):
            self.frameToReleaseLoad = 0
            self.action = 0

        def LoadFromXML(self, xmlNode):
            frameToReleaseLoad = read_from_xml_node(xmlNode, "FrameToReleaseLoad", do_not_warn=True)
            if frameToReleaseLoad is not None:
                self.frameToReleaseLoad = int(frameToReleaseLoad)
            action = read_from_xml_node(xmlNode, "Action")
            self.action = GetActionByName(action)


class Boss02ArmPrototypeInfo(BossArmPrototypeInfo):
    def __init__(self, server):
        BossArmPrototypeInfo.__init__(self, server)
        self.frameToPickUpContainerForBlock = 0
        self.frameToReleaseContainerForBlock = 0
        self.frameToPickUpContainerForDie = 0
        self.frameToReleaseContainerForDie = 0
        self.actionForBlock = 0
        self.actionForDie = 0
        self.blockingContainerPrototypeId = -1
        self.blockingContainerPrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = BossArmPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            frameToPickUpContainerForBlock = read_from_xml_node(xmlNode, "FrameToPickUpContainerForBlock",
                                                                do_not_warn=True)
            if frameToPickUpContainerForBlock is not None:
                self.frameToPickUpContainerForBlock = int(frameToPickUpContainerForBlock)

            frameToReleaseContainerForBlock = read_from_xml_node(xmlNode, "FrameToReleaseContainerForBlock",
                                                                 do_not_warn=True)
            if frameToReleaseContainerForBlock is not None:
                self.frameToReleaseContainerForBlock = int(frameToReleaseContainerForBlock)

            frameToPickUpContainerForDie = read_from_xml_node(xmlNode, "FrameToPickUpContainerForDie",
                                                              do_not_warn=True)
            if frameToPickUpContainerForDie is not None:
                self.frameToPickUpContainerForDie = int(frameToPickUpContainerForDie)

            frameToReleaseContainerForDie = read_from_xml_node(xmlNode, "FrameToReleaseContainerForDie",
                                                               do_not_warn=True)
            if frameToReleaseContainerForDie is not None:
                self.frameToReleaseContainerForDie = int(frameToReleaseContainerForDie)

            actionForBlock = read_from_xml_node(xmlNode, "ActionForBlock")
            self.actionForBlock = GetActionByName(actionForBlock)

            actionForDie = read_from_xml_node(xmlNode, "ActionForDie")
            self.actionForDie = GetActionByName(actionForDie)

            self.blockingContainerPrototypeName = read_from_xml_node(xmlNode, "ContainerPrototype")
            return STATUS_SUCCESS


class BossMetalArmPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.explosionEffectName = ""
        self.turningSpeed = 0.5
        self.lpIdForLoad = -1
        self.loadProrotypeIds = []
        self.attacks = []
        self.numExplodedLoadsToDie = 1
        self.loadPrototypeNames = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            self.explosionEffectName = read_from_xml_node(xmlNode, "ExplosionEffect")
            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed", do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed = float(turningSpeed)

            frameToPickUpLoad = read_from_xml_node(xmlNode, "FrameToPickUpLoad", do_not_warn=True)
            if frameToPickUpLoad is not None:
                self.frameToPickUpLoad = float(frameToPickUpLoad)

            attack_actions = child_from_xml_node(xmlNode, "AttackActions")
            check_mono_xml_node(attack_actions, "Attack")
            for attack_node in attack_actions.iterchildren():
                action = self.AttackActionInfo()
                action.LoadFromXML(attack_node)
                self.attacks.append(action)

            loadPrototypeNames = read_from_xml_node(xmlNode, "LoadPrototypes", do_not_warn=True)
            if loadPrototypeNames is not None:
                self.loadPrototypeNames = loadPrototypeNames.split()

            numExplodedLoadsToDie = read_from_xml_node(xmlNode, "NumExplodedLoadsToDie", do_not_warn=True)
            if numExplodedLoadsToDie is not None:
                self.numExplodedLoadsToDie = int(numExplodedLoadsToDie)
            return STATUS_SUCCESS

    class AttackActionInfo(object):
        def __init__(self):
            self.frameToReleaseLoad = 0
            self.action = 0

        def LoadFromXML(self, xmlNode):
            frameToReleaseLoad = read_from_xml_node(xmlNode, "FrameToReleaseLoad", do_not_warn=True)
            if frameToReleaseLoad is not None:
                self.frameToReleaseLoad = int(frameToReleaseLoad)
            action = read_from_xml_node(xmlNode, "Action")
            self.action = GetActionByName(action)


class BossMetalArmLoadPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)
        self.blastWavePrototypeId = -1
        self.explosionEffectName = ""
        self.maxHealth = 1.0
        self.blastWavePrototypeName = ""
        self.isUpdating = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DummyObjectPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.blastWavePrototypeName = read_from_xml_node(xmlNode, "BlastWavePrototype")
            self.explosionEffectName = read_from_xml_node(xmlNode, "ExplosionEffect")

            maxHealth = read_from_xml_node(xmlNode, "MaxHealth")
            if maxHealth is not None:
                self.maxHealth = float(maxHealth)
            return STATUS_SUCCESS


class Boss03PartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)


class Boss04PartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)


class Boss04DronePrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.maxLinearVelocity = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxLinearVelocity = read_from_xml_node(xmlNode, "MaxLinearVelocity")
            if maxLinearVelocity is not None:
                self.maxLinearVelocity = float(maxLinearVelocity)
            return STATUS_SUCCESS


class Boss04StationPartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.criticalMeshGroupIds = []
        self.collisionTrimeshAllowed = True
        self.maxHealth = 0.0


class Boss04StationPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)


class Boss02PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.stateInfos = []
        self.speed = 1.0
        self.containerPrototypeId = -1
        self.relPosForContainerPickUp = {}
        self.relRotForContainerPickUp = {}
        self.relPosForContainerPutDown = {}
        self.containerPrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            states_node = child_from_xml_node(xmlNode, "States")
            check_mono_xml_node(states_node, "State")
            for state_node in states_node.iterchildren():
                state = self.StateInfo()
                state.LoadFromXML(state_node)
            speed = read_from_xml_node(xmlNode, "Speed")
            if speed is not None:
                self.speed = float(speed)
            self.containerPrototypeName = read_from_xml_node(xmlNode, "ContainerPrototype")
            return STATUS_SUCCESS

    class StateInfo(object):
        def __init__(self):
            self.loadPrototypeIds = []
            self.loadPrototypeNames = []
            self.position = deepcopy(ZERO_VECTOR)

        def LoadFromXML(self, xmlFile, xmlNode):
            self.loadPrototypeNames = read_from_xml_node(xmlNode, "LoadPrototypes").split()
            position = read_from_xml_node(xmlNode, "RelPos")
            self.position = {"x": position[0],
                             "y": position[1],
                             "z": position[2]}


class AnimatedComplexPhysicObjPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)


class Boss03PrototypeInfo(AnimatedComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        AnimatedComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.dronePrototypeIds = []
        self.maxDrones = 1
        self.droneRelPosition = ZERO_VECTOR
        self.droneRelRotation = IDENTITY_QUATERNION
        self.maxHorizAngularVelocity = 0.0
        self.horizAngularAcceleration = 0.0
        self.maxVertAngularVelocity = 0.0
        self.vertAngularAcceleration = 0.0
        self.maxLinearVelocity = 0.0
        self.linearAcceleration = 0.0
        self.pathTrackTiltAngle = 0.0
        self.maxHealth = 1.0
        self.maxShootingTime = 1.0
        self.defaultHover = 10.0
        self.hoverForPlacingDrones = 10.0
        self.dronePrototypeNames = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = AnimatedComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            pass


class Boss04PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.stationPrototypeId = -1
        self.dronePrototypeId = -1
        self.timeBetweenDrones = {"x": 10.0, "y": 20.0}
        self.maxDrones = 0
        self.stationToPartBindings = []
        self.droneSpawningLpIds = []
        self.stationPrototypeName = ""
        self.dronePrototypeName = ""
        self.droneSpawningLpNames = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            pass

    # "Boss03": Boss03PrototypeInfo,
    # "Boss04": Boss04PrototypeInfo,



# dict mapping Object Classes to PrototypeInfo Classes
thePrototypeInfoClassDict = {
    "AffixGenerator": AffixGeneratorPrototypeInfo,
    # "ArticulatedVehicle": ArticulatedVehiclePrototypeInfo,
    # "Bar": BarPrototypeInfo,
    # "Barricade": BarricadePrototypeInfo,
    # "Basket": BasketPrototypeInfo,
    # "BlastWave": BlastWavePrototypeInfo,
    "Boss02Arm": Boss02ArmPrototypeInfo,
    "Boss02": Boss02PrototypeInfo,
    "Boss03Part": Boss03PartPrototypeInfo,
    "Boss03": Boss03PrototypeInfo,
    "Boss04Drone": Boss04DronePrototypeInfo,
    "Boss04Part": Boss04PartPrototypeInfo,
    "Boss04": Boss04PrototypeInfo,
    "Boss04StationPart": Boss04StationPartPrototypeInfo,
    "Boss04Station": Boss04StationPrototypeInfo,
    "BossMetalArmLoad": BossMetalArmLoadPrototypeInfo,
    "BossMetalArm": BossMetalArmPrototypeInfo,
    # "BreakableObject": BreakableObjectPrototypeInfo,
    # "Building": BuildingPrototypeInfo,
    # "BulletLauncher": BulletLauncherPrototypeInfo,
    # "Bullet": BulletPrototypeInfo,
    # "Cabin": CabinPrototypeInfo,
    "CaravanTeam": CaravanTeamPrototypeInfo,
    # "Chassis": ChassisPrototypeInfo,
    # "Chest": ChestPrototypeInfo,
    "CinematicMover": CinematicMoverPrototypeInfo,
    # "CompositeObj": CompositeObjPrototypeInfo,
    # "CompoundGun": CompoundGunPrototypeInfo,
    # "CompoundVehiclePart": CompoundVehiclePartPrototypeInfo,
    "DummyObject": DummyObjectPrototypeInfo,
    "DynamicQuestConvoy": DynamicQuestConvoyPrototypeInfo,
    "DynamicQuestDestroy": DynamicQuestDestroyPrototypeInfo,
    "DynamicQuestHunt": DynamicQuestHuntPrototypeInfo,
    "DynamicQuestPeace": DynamicQuestPeacePrototypeInfo,
    "DynamicQuestReach": DynamicQuestReachPrototypeInfo,
    # "EngineOilLocation": EngineOilLocationPrototypeInfo,
    "Formation": FormationPrototypeInfo,
    "Gadget": GadgetPrototypeInfo,
    # "GeomObj": GeomObjPrototypeInfo,
    "InfectionLair": InfectionLairPrototypeInfo,
    "InfectionTeam": InfectionTeamPrototypeInfo,
    "InfectionZone": InfectionZonePrototypeInfo,
    # "JointedObj": JointedObjPrototypeInfo,
    # "Lair": LairPrototypeInfo,
    "LightObj": LightObjPrototypeInfo,
    "Location": LocationPrototypeInfo,
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
    "Player": PlayerPrototypeInfo,
    # "QuestItem": QuestItemPrototypeInfo,
    "RadioManager": RadioManagerPrototypeInfo,
    # "RepositoryObjectsGenerator": RepositoryObjectsGeneratorPrototypeInfo,
    # "RocketLauncher": RocketLauncherPrototypeInfo,
    # "Rocket": RocketPrototypeInfo,
    # "RocketVolleyLauncher": RocketVolleyLauncherPrototypeInfo,
    # "RopeObj": RopeObjPrototypeInfo,
    "SgNodeObj": SgNodeObjPrototypeInfo,
    # "SmokeScreenLocation": SmokeScreenLocationPrototypeInfo,
    # "StaticAutoGun": StaticAutoGunPrototypeInfo,
    # "Submarine": SubmarinePrototypeInfo,
    "Team": TeamPrototypeInfo,
    "TeamTacticWithRoles": TeamTacticWithRolesPrototypeInfo,
    # "ThunderboltLauncher": ThunderboltLauncherPrototypeInfo,
    # "Thunderbolt": ThunderboltPrototypeInfo,
    # "Town": TownPrototypeInfo,
    "Trigger": TriggerPrototypeInfo,
    # "TurboAccelerationPusher": TurboAccelerationPusherPrototypeInfo,
    "VagabondTeam": VagabondTeamPrototypeInfo,
    "VehiclePart": VehiclePartPrototypeInfo,
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
    "WanderersGenerator": WanderersGeneratorPrototypeInfo,
    "WanderersManager": WanderersManagerPrototypeInfo,
    # "Ware": WarePrototypeInfo,
    # "Wheel": WheelPrototypeInfo,
    # "Workshop": WorkshopPrototypeInfo
}
