from math import pi, sqrt
from copy import deepcopy
from lxml import objectify

from logger import logger

from em_parse import (read_from_xml_node, child_from_xml_node, check_mono_xml_node, safe_check_and_set,
                      parse_str_to_bool, parse_str_to_quaternion, parse_str_to_vector)
from constants import (STATUS_SUCCESS, DEFAULT_TURNING_SPEED, FiringTypesStruct, DamageTypeStruct, DESTROY_EFFECT_NAMES,
                       TEAM_DEFAULT_FORMATION_PROTOTYPE, GEOM_TYPE, ZERO_VECTOR, IDENTITY_QUATERNION)
from object_classes import *
from global_functions import GetActionByName, AIParam


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
        self.parentPrototypeName = -1
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
            if strResType is not None and self.resourceId == -1:
                if not self.parentPrototypeName:
                    logger.info(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName}")
                elif self.parent.resourceId == -1:
                    logger.info(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName} "
                                f" and its parent {self.parent.prototypeName}")

            self.visibleInEncyclopedia = parse_str_to_bool(read_from_xml_node(xmlNode,
                                                                              "VisibleInEncyclopedia",
                                                                              do_not_warn=True))
            self.applyAffixes = parse_str_to_bool(read_from_xml_node(xmlNode, "ApplyAffixes", do_not_warn=True))
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price = price
            self.isAbstract = parse_str_to_bool(read_from_xml_node(xmlNode, "Abstract", do_not_warn=True))
            # ??? maybe should fallback to "" instead None
            self.parentPrototypeName = read_from_xml_node(xmlNode, "ParentPrototype", do_not_warn=True)
            return STATUS_SUCCESS
        else:
            logger.warning(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")

    def CopyFrom(self, prot_to_copy_from):
        if self.className == prot_to_copy_from.className:
            self.InternalCopyFrom(prot_to_copy_from)
        else:
            logger.error(f"Unexpected parent prototype class for {self.prototypeName}: "
                         f"expected {self.className}, got {prot_to_copy_from.className}")

    def InternalCopyFrom(self, prot_to_copy_from):
        logger.error(f"CopyFrom is not implemented for PrototypeInfo {self.prototypeName} of class {self.className}")

    def PostLoad(self, prototype_manager):
        if self.parentPrototypeName:
            self.parentPrototypeId = prototype_manager.GetPrototypeId(self.parentPrototypeName)
            if self.parentPrototypeId == -1:
                logger.error(f"Invalid parent prototype: '{self.parentPrototypeName}' "
                             f"for prototype: '{self.prototypeName}'")


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
            self.engineModelName = safe_check_and_set(self.engineModelName, xmlNode, "ModelFile")
            if self.engineModelName is None and not issubclass(type(self), CompoundVehiclePartPrototypeInfo):
                logger.error(f"No model file is provided for prototype {self.prototypeName}")
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            self.collisionTrimeshAllowed = parse_str_to_bool(read_from_xml_node(xmlNode, "CollisionTrimeshAllowed",
                                                                                do_not_warn=True))
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
            self.blowEffectName = safe_check_and_set(self.blowEffectName, xmlNode, "BlowEffect")
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


class ChassisPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.maxHealth = 1.0
        self.maxFuel = 1.0
        self.brakingSoundName = ""
        self.pneumoSoundName = ""
        self.gearShiftSoundName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicBodyPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxHealth = read_from_xml_node(xmlNode, "MaxHealth", do_not_warn=True)
            if maxHealth is not None:
                self.maxHealth = float(maxHealth)

            maxFuel = read_from_xml_node(xmlNode, "MaxFuel", do_not_warn=True)
            if maxFuel is not None:
                self.maxFuel = float(maxFuel)

            self.brakingSoundName = read_from_xml_node(xmlNode, "BrakingSound")
            self.pneumoSoundName = read_from_xml_node(xmlNode, "PneumoSound")
            self.gearShiftSoundName = read_from_xml_node(xmlNode, "GearShiftSound")
            return STATUS_SUCCESS


class CabinPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.maxPower = 1.0
        self.maxTorque = 1.0
        self.maxSpeed = 1.0
        self.fuelConsumption = 1.0
        self.gadgetSlots = []
        self.control = 50.0
        self.engineHighSoundName = ""
        self.engineLowSoundName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicBodyPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxPower = read_from_xml_node(xmlNode, "MaxPower", do_not_warn=True)
            if maxPower is not None:
                self.maxPower = float(maxPower)

            maxTorque = read_from_xml_node(xmlNode, "MaxTorque", do_not_warn=True)
            if maxTorque is not None:
                self.maxTorque = float(maxTorque)

            maxSpeed = read_from_xml_node(xmlNode, "MaxSpeed", do_not_warn=True)
            if maxSpeed is not None:
                self.maxSpeed = float(maxSpeed)

            fuelConsumption = read_from_xml_node(xmlNode, "FuelConsumption", do_not_warn=True)
            if fuelConsumption is not None:
                self.fuelConsumption = float(fuelConsumption)

            self.engineHighSoundName = safe_check_and_set(self.engineHighSoundName, xmlNode, "EngineHighSound")
            self.engineLowSoundName = safe_check_and_set(self.engineLowSoundName, xmlNode, "EngineLowSound")

            control = read_from_xml_node(xmlNode, "Control", do_not_warn=True)
            if control is not None:
                self.control = float(control)
            if self.control < 0.0 or self.control > 100.0:
                self.control = 100.0

            self.maxSpeed = self.maxSpeed * 0.27777779  # ~5/18 or 50/180

            gadgetDescriptions = child_from_xml_node(xmlNode, "GadgetDescription", do_not_warn=True)
            if gadgetDescriptions is not None:
                check_mono_xml_node(gadgetDescriptions, "Slot")
                for gadget_node in gadgetDescriptions.iterchildren(tag="Slot"):
                    gadget = {"resourceType": read_from_xml_node(gadget_node, "ResourceType"),
                              "maxAmount": int(read_from_xml_node(gadget_node, "MaxAmount"))}
                    self.gadgetSlots.append(gadget)
            return STATUS_SUCCESS


class BasketPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.slots = []
        self.repositorySize = {"x": 10, "y": 10}

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicBodyPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            repositoryDescriptions = child_from_xml_node(xmlNode, "RepositoryDescription")
            repositorySize = read_from_xml_node(repositoryDescriptions, "RepositorySize")
            self.repositorySize = {"x": repositorySize[0],
                                   "y": repositorySize[1]}
            if len(repositoryDescriptions.getchildren()) > 1:
                check_mono_xml_node(repositoryDescriptions, "Slot")
                for slot_node in repositoryDescriptions.iterchildren(tag="Slot"):
                    pos = read_from_xml_node(slot_node, "Pos").split()
                    pos = {"x": pos[0], "y": pos[1]}
                    slot = {"name": read_from_xml_node(slot_node, "Name"),
                            "pos": pos}
                    self.slots.append(slot)
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


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
            self.shellPrototypeName = safe_check_and_set(self.shellPrototypeName, xmlNode, "BulletPrototype")
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWavePrototype")
            damage = read_from_xml_node(xmlNode, "Damage", do_not_warn=True)
            if damage is not None:
                self.damage = float(damage)

            firingRate = read_from_xml_node(xmlNode, "FiringRate", do_not_warn=True)
            if firingRate is not None:
                self.firingRate = float(firingRate)

            firingRange = read_from_xml_node(xmlNode, "FiringRange", do_not_warn=True)
            if firingRange is not None:
                self.firingRange = float(firingRange)

            self.explosionTypeName = safe_check_and_set(self.explosionTypeName, xmlNode, "ExplosionType")

            recoilForce = read_from_xml_node(xmlNode, "RecoilForce", do_not_warn=True)
            if recoilForce is not None:
                self.recoilForce = float(recoilForce)

            decalName = safe_check_and_set("", xmlNode, "Decal")
            self.decalId = f"Placeholder for {decalName}!"  # DynamicScene.AddDecalName(decalName)

            firingType = read_from_xml_node(xmlNode, "FiringType")
            self.firingType = GunPrototypeInfo.Str2FiringType(firingType)
            if self.firingType is None:
                logger.warning(f"Unknown firing type: {self.firingType}!")

            damageTypeName = read_from_xml_node(xmlNode, "DamageType", do_not_warn=True)
            if damageTypeName is not None:
                self.damageType = GunPrototypeInfo.Str2DamageType(damageTypeName)
            if self.damageType is None:
                logger.warning(f"Unknown damage type: {self.damageType}")

            self.withCharging = parse_str_to_bool(read_from_xml_node(xmlNode, "WithCharging", do_not_warn=True))

            chargeSize = read_from_xml_node(xmlNode, "ChargeSize", do_not_warn=True)
            if chargeSize is not None:
                chargeSize = int(chargeSize)
                if chargeSize >= 0:  # ??? whaaat, why should it ever be less than 0?
                    self.chargeSize = chargeSize

            reChargingTime = read_from_xml_node(xmlNode, "RechargingTime", do_not_warn=True)
            if reChargingTime is not None:
                self.reChargingTime = float(reChargingTime)

            self.shellsPoolSize = 0
            shellsPoolSize = read_from_xml_node(xmlNode, "ShellsPoolSize", do_not_warn=True)
            if shellsPoolSize is not None:
                shellsPoolSize = int(shellsPoolSize)
                if shellsPoolSize > 0:
                    self.shellsPoolSize = shellsPoolSize
                if shellsPoolSize <= 0:
                    self.withShellsPoolLimit = 0
                    self.shellsPoolSize = 12

            self.withShellsPoolLimit = parse_str_to_bool(read_from_xml_node(xmlNode, "WithShellsPoolLimit",
                                                                            do_not_warn=True))

            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed", do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed = float(turningSpeed)
            self.turningSpeed *= pi / 180  # convert to rads
            self.engineModelName += "Gun"  # ??? is this really what's happening?
            self.ignoreStopAnglesWhenFire = parse_str_to_bool(read_from_xml_node(xmlNode, "IgnoreStopAnglesWhenFire",
                                                                                 do_not_warn=True))
            return STATUS_SUCCESS

    def Str2FiringType(firing_type_name: str):
        return FiringTypesStruct.get(firing_type_name)

    def Str2DamageType(damage_type_name: str):
        return DamageTypeStruct.get(damage_type_name)

    def PostLoad(self, prototype_manager):
        self.explosionType = "DUMMY_EXPLOSION_TYPE_NOT_IMPLEMENTED_GET_EXPLOSION_TYPE"
        # self.explosionType = prototype_manager.theServer.theDynamicScene.GetExplosionType(self.explosionTypeName)
        self.shellPrototypeId = prototype_manager.GetPrototypeId(self.shellPrototypeName)
        if self.shellPrototypeId == -1:  # ??? there also exist check if sheelPrototypeName is not empty. A valid case?
            logger.error(f"Shell prototype {self.shellPrototypeId} is invalid for {self.prototypeName}")
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)
        if self.blastWavePrototypeId == -1:
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
            for modification_description in modifications:
                modification_info = self.ModificationInfo(modification_description, self)
                self.modifications.append(modification_info)
            self.modelName = safe_check_and_set(self.modelName, xmlNode, "ModelFile")
            self.skinNum = safe_check_and_set(self.skinNum, xmlNode, "SkinNum", "int")
            return STATUS_SUCCESS

    class ModificationInfo(object):
        # other ModificationInfo object can be passed to create copy
        def __init__(self, tokens: str, prot_info, other_mod=None):  # tokens=None
            if other_mod is None:
                self.applierInfo = {"applierType": 0,
                                    "targetResourceId": -1,
                                    "targetFiringType": 0}
                self.propertyName = ""
                self.value = ""  # is AIParam() necessary ???
                self.value_type = 0

                self.modificationType = 0
                token_value_part = 2

                token_parts = tokens.split()
                tokens_size = len(token_parts)
                if tokens_size == 4:
                    if token_parts[2] == "+=":
                        self.modificationType = 1
                        token_value_part = 3
                    else:
                        logger.error("Unexpected gadget modification token format. "
                                     "For 4-part token format third part should be '+='. "
                                     f"Given tokens: '{tokens}' for prototype: {prot_info.prototypeName}")
                elif tokens_size != 3:
                    logger.error("Expected tokens list with size equal to 3 or 4. "
                                 f"Given tokens: '{tokens}' for prototype: {prot_info.prototypeName}")

                token_resource_id = prot_info.theServer.theResourceManager.GetResourceId(token_parts[0])
                if token_parts[0] == "VEHICLE":
                    self.applierInfo["applierType"] = 0
                elif token_resource_id == -1:
                    self.applierInfo["applierType"] = 2
                    self.applierInfo["targetFiringType"] = GunPrototypeInfo.Str2FiringType(token_parts[0])
                    if self.applierInfo["targetFiringType"] is None:
                        logger.warning(f"Unknown firing type '{token_parts[0]}' "
                                       f"for modification token of prototype: {prot_info.prototypeName}")
                else:
                    self.applierInfo["applierType"] = 1
                    self.applierInfo["targetResourceId"] = token_resource_id
                self.propertyName = token_parts[1]
                if self.modificationType != 0:
                    if self.modificationType == 1:
                        self.value = token_parts[token_value_part]
                        self.value_type = 5
                    else:
                        logger.error(f"Unexpected modificationType for ModificationInfo '{tokens}'' "
                                     f"of {prot_info.prototypeName}")
                else:
                    value = float(token_parts[token_value_part]) * 0.01
                    self.value = value
                    self.value_type = 4

            elif other_mod is not None:
                self.applierInfo["applierType"] = other_mod.applierInfo["applierType"]
                self.applierInfo["targetResourceId"] = other_mod.applierInfo["targetResourceId"]
                self.applierInfo["targetFiringType"] = other_mod.applierInfo["targetFiringType"]
                self.propertyName = other_mod.propertyName
                # self.NumFromName = int(other_mod.modificationType)
                self.value = other_mod.value  # ??? some AIParam magic in here


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
            desiredCount = read_from_xml_node(xmlNode, "DesiredCount", do_not_warn=True)
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
            vehicles = child_from_xml_node(xmlNode, "Vehicles")
            check_mono_xml_node(vehicles, "Vehicle")
            for vehicle_node in vehicles.iterchildren("Vehicle"):
                vehicle_description = self.VehicleDescription()
                vehicle_description.LoadFromXML(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.vehicleDescriptions:
            for vehicle_description in self.vehicleDescriptions:
                vehicle_description.PostLoad(prototype_manager)

    class VehicleDescription(object):
        def __init__(self):
            self.prototype = ""
            self.prototypeId = -1
            self.cabin = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basket = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.cabinSmallGun = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.cabinBigGun = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.cabinSpecialWeapon = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basketSmallGun0 = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basketSmallGun1 = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basketBigGun0 = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basketBigGun1 = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            self.basketSideGun = WanderersGeneratorPrototypeInfo.VehiclePartDescription()

        def LoadFromXML(self, xmlFile, xmlNode):
            self.prototype = safe_check_and_set(self.prototype, xmlNode, "Prototype")
            self.cabin = self.LoadPartFromXML("Cabin", xmlFile, xmlNode)
            self.basket = self.LoadPartFromXML("Basket", xmlFile, xmlNode)
            self.cabinSmallGun = self.LoadPartFromXML("CabinSmallGun", xmlFile, xmlNode)
            self.cabinBigGun = self.LoadPartFromXML("CabinBigGun", xmlFile, xmlNode)
            self.cabinSpecialWeapon = self.LoadPartFromXML("CabinSpecialWeapon", xmlFile, xmlNode)
            self.basketSmallGun0 = self.LoadPartFromXML("BasketSmallGun0", xmlFile, xmlNode)
            self.basketSmallGun1 = self.LoadPartFromXML("BasketSmallGun1", xmlFile, xmlNode)
            self.basketBigGun0 = self.LoadPartFromXML("BasketBigGun0", xmlFile, xmlNode)
            self.basketBigGun1 = self.LoadPartFromXML("BasketBigGun1", xmlFile, xmlNode)
            self.basketSideGun = self.LoadPartFromXML("BasketSideGun", xmlFile, xmlNode)

        def LoadPartFromXML(self, partName, xmlFile, xmlNode):
            partXMLNode = child_from_xml_node(xmlNode, partName, do_not_warn=True)
            part = WanderersGeneratorPrototypeInfo.VehiclePartDescription()
            if partXMLNode is not None:
                part.LoadFromXML(xmlFile, partXMLNode)
            return part

        def PostLoad(self, prototype_manager):
            self.prototypeId = prototype_manager.GetPrototypeId(self.prototype)
            if self.prototypeId == -1:
                logger.error(f"Unknown vehicle prototype {self.prototype} in wanderers generator!")
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.cabin, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basket, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.cabinSmallGun, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.cabinBigGun, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.cabinSpecialWeapon, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basketSmallGun0, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basketSmallGun1, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basketBigGun0, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basketBigGun1, prototype_manager)
            WanderersGeneratorPrototypeInfo.VehiclePartDescription.PostLoad(self.basketSideGun, prototype_manager)

    class VehiclePartDescription(object):
        def __init__(self):
            self.present = True
            self.prototypeNames = []
            self.prototypeIds = []

        def LoadFromXML(self, xmlFile, xmlNode):
            self.present = parse_str_to_bool(read_from_xml_node(xmlNode, "Present", do_not_warn=True))
            strPrototypes = read_from_xml_node(xmlNode, "Prototypes", do_not_warn=True)
            if strPrototypes is not None:
                self.prototypeNames = strPrototypes.split()

        def PostLoad(self, prototype_manager):
            for prot_name in self.prototypeNames:
                prot_id = prototype_manager.GetPrototypeId(prot_name)
                if prot_id == -1:
                    logger.error(f"Unknown vehicle part prototype {prot_name} in wanderers generator!")
                self.prototypeIds.append(prot_id)


class AffixGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.affixDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            affix_nodes = child_from_xml_node(xmlNode, "Affix")
            for affix in affix_nodes:
                self.affixDescriptions.append(read_from_xml_node(affix, "AffixName"))
            return STATUS_SUCCESS

    def GenerateAffixesForObj(self, obj, desiredNumAffixed):
        pass

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


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
            # ??? maybe should fallback to "" instead None
            self.engineModelName = read_from_xml_node(xmlNode, "ModelFile", do_not_warn=True)
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


class ChestPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            self.lifeTime = safe_check_and_set(-1, xmlNode, "LifeTime", "float")
            if self.lifeTime <= 0.0:
                self.withLifeTime = False
            else:
                self.withLifeTime = True
            return STATUS_SUCCESS


class ComplexPhysicObjPartDescription(Object):
    def __init__(self, prototype_info_object=None):
        Object.__init__(self, prototype_info_object)
        self.partResourceId = -1
        self.lpNames = []
        self.child_descriptions = []  # ??? temporary placeholder for original logic

    def LoadFromXML(self, xmlFile, xmlNode, server):
        self.name = read_from_xml_node(xmlNode, "id")
        if self.parent is not None:
            parent_lookup = self.parent.GetChildByName(self.name)
            if parent_lookup is not None and self is parent_lookup:  # ??? can this ever be true?
                logger.warning(f"When loading PartDescription: name = {self.name} conflicts with another child")

        partResourceType = read_from_xml_node(xmlNode, "partResourceType")
        self.partResourceId = server.theResourceManager.GetResourceId(partResourceType)
        lpNames = read_from_xml_node(xmlNode, "lpName", do_not_warn=True)
        if lpNames is not None:
            self.lpNames = lpNames.split()
        if len(xmlNode.getchildren()) >= 1:
            check_mono_xml_node(xmlNode, "PartDescription")
            for description_node in xmlNode.iterchildren(tag="PartDescription"):
                part_description = ComplexPhysicObjPartDescription()
                part_description.LoadFromXML(xmlFile, description_node, server)
                self.child_descriptions.append(part_description)  # ??? temporary placeholder for original logic


class ComplexPhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)
        self.partPrototypeIds = []
        self.partPrototypeNames = []
        self.massSize = {"x": 1.0,
                         "y": 1.0,
                         "z": 1.0}
        self.massTranslation = deepcopy(ZERO_VECTOR)
        self.partDescription = []
        self.allPartNames = []
        self.massShape = 0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            main_part_description_node = child_from_xml_node(xmlNode, "MainPartDescription", do_not_warn=True)
            if main_part_description_node is not None:
                partPrototypeDescriptions = ComplexPhysicObjPartDescription()
                partPrototypeDescriptions.LoadFromXML(xmlFile, main_part_description_node, self.theServer)
                self.partPrototypeDescriptions = partPrototypeDescriptions
            else:
                if self.parent.partPrototypeDescriptions is None:
                    logger.warning(f"Parts description is missing for prototype {self.prototypeName}")
            parts_node = child_from_xml_node(xmlNode, "Parts")
            if parts_node is not None:
                check_mono_xml_node(parts_node, "Part")
                for part_node in parts_node.iterchildren(tag="Part"):
                    prototypeId = read_from_xml_node(part_node, "id")
                    prototypeName = read_from_xml_node(part_node, "Prototype")
                    protName = {"name": prototypeName,
                                "id": prototypeId}
                    self.partPrototypeNames.append(protName)
            massSize = read_from_xml_node(xmlNode, "MassSize", do_not_warn=True)
            if massSize is not None:
                self.massSize = parse_str_to_vector(massSize)
            massTranslation = read_from_xml_node(xmlNode, "MassTranslation", do_not_warn=True)
            if massTranslation is not None:
                self.massTranslation = parse_str_to_vector(massTranslation)
            self.massShape = safe_check_and_set(self.massShape, xmlNode, "MassShape", "int")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        for prot_name in self.partPrototypeNames:
            self.partPrototypeIds.append(prototype_manager.GetPrototypeId(prot_name["name"]))
        # can this replace ComplexPhysicObjPartDescription::GetPartNames?
        self.allPartNames = [part.name for part in self.partDescription]


class StaticAutoGunPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.maxHealth = 1.0
        self.destroyedModelName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            if self.parentPrototypeName is None:
                self.maxHealth = safe_check_and_set(self.maxHealth, xmlNode, "MaxHealth", "float")
                self.destroyedModelName = safe_check_and_set(self.destroyedModelName, xmlNode, "DestroyedModel")
            return STATUS_SUCCESS


class VehiclePrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.wheelInfos = []
        self.selfbrakingCoeff = 0.0060000001
        self.diffRatio = 1.0
        self.maxEngineRpm = 1.0
        self.lowGearShiftLimit = 1.0
        self.highGearShiftLimit = 1.0
        self.steeringSpeed = 1.0
        self.takingRadius = 1.0
        self.priority = -56
        self.decisionMatrixNum = -1
        self.hornSoundName = ""
        self.cameraHeight = -1.0
        self.cameraMaxDist = 25.0
        self.destroyEffectNames = ["ET_PS_VEH_EXP" for i in range(4)]
        self.blastWavePrototypeId = -1
        self.additionalWheelsHover = 0.0
        self.driftCoeff = 1.0
        self.pressingForce = 1.0
        self.healthRegeneration = 0.0
        self.durabilityRegeneration = 0.0
        self.blastWavePrototypeName = ""
        self.visibleInEncyclopedia = False

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.diffRatio = safe_check_and_set(self.diffRatio, xmlNode, "DiffRatio", "float")
            self.maxEngineRpm = safe_check_and_set(self.maxEngineRpm, xmlNode, "MaxEngineRpm", "float")
            self.lowGearShiftLimit = safe_check_and_set(self.lowGearShiftLimit, xmlNode, "LowGearShiftLimit", "float")
            self.highGearShiftLimit = safe_check_and_set(self.highGearShiftLimit, xmlNode,
                                                         "HighGearShiftLimit", "float")
            self.selfbrakingCoeff = safe_check_and_set(self.selfbrakingCoeff, xmlNode, "SelfBrakingCoeff", "float")
            self.steeringSpeed = safe_check_and_set(self.steeringSpeed, xmlNode, "SteeringSpeed", "float")
            decisionMatrixName = read_from_xml_node(xmlNode, "DecisionMatrix", do_not_warn=True)
            # theAIManager.LoadMatrix(decisionMatrixName)
            # self.decisionMatrixNum = theAIManager.GetMatrixNum(decisionMatrixName)
            self.decisionMatrixNum = f"DummyMatrixNum_{decisionMatrixName}"  # ??? replace when AIManager is implemented
            self.takingRadius = safe_check_and_set(self.takingRadius, xmlNode, "TakingRadius", "float")
            self.priority = safe_check_and_set(self.priority, xmlNode, "Priority", "int")
            self.hornSoundName = safe_check_and_set(self.hornSoundName, xmlNode, "HornSound")
            self.cameraHeight = safe_check_and_set(self.cameraHeight, xmlNode, "CameraHeight", "float")
            self.cameraMaxDist = safe_check_and_set(self.cameraMaxDist, xmlNode, "CameraMaxDist", "float")
            destroyEffectNames = [read_from_xml_node(xmlNode, name, do_not_warn=True) for name in DESTROY_EFFECT_NAMES]
            for i in range(len(self.destroyEffectNames)):
                if destroyEffectNames[i] is not None:
                    self.destroyEffectNames[i] = destroyEffectNames[i]
            wheels_info = child_from_xml_node(xmlNode, "Wheels", do_not_warn=True)
            if self.parentPrototypeName is not None and wheels_info is not None:
                logger.error(f"Wheels info is present for inherited vehicle {self.prototypeName}")
            elif self.parentPrototypeName is None and wheels_info is None:
                logger.error(f"Wheels info is not present for parent vehicle {self.prototypeName}")
            elif self.parentPrototypeName is None and wheels_info is not None:
                check_mono_xml_node(wheels_info, "Wheel")
                for wheel_node in wheels_info.iterchildren(tag="Wheel"):
                    steering = read_from_xml_node(wheel_node, "steering", do_not_warn=True)
                    wheel_prototype_name = read_from_xml_node(wheel_node, "Prototype")
                    wheel = self.WheelInfo(wheel_prototype_name, steering)
                    self.wheelInfos.append(wheel)
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWave")
            self.additionalWheelsHover = safe_check_and_set(self.additionalWheelsHover, xmlNode,
                                                            "AdditionalWheelsHover", "float")
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWave")
            self.driftCoeff = safe_check_and_set(self.driftCoeff, xmlNode, "DriftCoeff", "float")
            self.pressingForce = safe_check_and_set(self.pressingForce, xmlNode, "PressingForce", "float")
            self.healthRegeneration = safe_check_and_set(self.healthRegeneration, xmlNode,
                                                         "HealthRegeneration", "float")
            self.durabilityRegeneration = safe_check_and_set(self.durabilityRegeneration, xmlNode,
                                                             "DurabilityRegeneration", "float")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for wheel_info in self.wheelInfos:
            wheel_info.wheelPrototypeId = prototype_manager.GetPrototypeId(wheel_info.wheelPrototypeName)
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    class WheelInfo(object):
        def __init__(self, wheelPrototypeName, steering):
            self.steering = steering
            self.wheelPrototypeName = wheelPrototypeName
            self.wheelPrototypeId = -1

        def PostLoad(self, prototype_manager):
            self.wheelPrototypeId = prototype_manager.GetPrototypeId(self.wheelPrototypeName)


class ArticulatedVehiclePrototypeInfo(VehiclePrototypeInfo):
    def __init__(self, server):
        VehiclePrototypeInfo.__init__(self, server)
        self.trailerPrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.trailerPrototypeName = safe_check_and_set(self.trailerPrototypeName, xmlNode, "TrailerPrototype")
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    def PostLoad(self, prototype_manager):
        VehiclePrototypeInfo.PostLoad(self, prototype_manager)
        self.trailerPrototypeId = prototype_manager.GetPrototypeId(self.trailerPrototypeName)


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


class WheelPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.suspensionModelName = ""
        self.suspensionRange = 0.5
        self.suspensionCFM = 0.1
        self.suspensionERP = 0.80000001
        self.mU = 1.0
        self.typeName = "BIG"
        self.blowEffectName = "ET_PS_HARD_BLOW"

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            suspensionRange = read_from_xml_node(xmlNode, "SuspensionRange", do_not_warn=True)
            if suspensionRange is not None:
                self.suspensionRange = float(suspensionRange)

            self.suspensionModelName = read_from_xml_node(xmlNode, "SuspensionModelFile")

            suspensionCFM = read_from_xml_node(xmlNode, "SuspensionCFM", do_not_warn=True)
            if suspensionCFM is not None:
                self.suspensionCFM = float(suspensionCFM)

            suspensionERP = read_from_xml_node(xmlNode, "SuspensionERP", do_not_warn=True)
            if suspensionERP is not None:
                self.suspensionERP = float(suspensionERP)

            mU = read_from_xml_node(xmlNode, "mU", do_not_warn=True)
            if mU is not None:
                self.mU = float(mU)

            self.typeName = safe_check_and_set(self.typeName, xmlNode, "EffectType")
            self.blowEffectName = safe_check_and_set(self.blowEffectName, xmlNode, "BlowEffect")
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
            check_mono_xml_node(xmlNode, "Role")
            for role in xmlNode.iterchildren(tag="Role"):
                self.rolePrototypeNames.append(read_from_xml_node(role, "Prototype"))
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.rolePrototypeNames:
            for role_name in self.rolePrototypeNames:
                role_prot_id = prototype_manager.GetPrototypeId(role_name)
                if role_prot_id == -1:  # ??? there also exist check if sheelPrototypeName is not empty. A valid case?
                    logger.error(f"Unknown role prototype: '{self.shellPrototypeId}' for prot: '{self.prototypeName}'")
                else:
                    self.rolePrototypeIds.append(role_prot_id)


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
        self.formationPrototypeId = -1
        self.overridesDistBetweenVehicles = False
        self.isUpdating = False
        self.formationDistBetweenVehicles = 30.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.decisionMatrixName = read_from_xml_node(xmlNode, "DecisionMatrix")
            self.removeWhenChildrenDead = parse_str_to_bool(read_from_xml_node(xmlNode, "RemoveWhenChildrenDead",
                                                                               do_not_warn=True))
            formation = child_from_xml_node(xmlNode, "Formation", do_not_warn=True)
            if formation is not None:
                self.formationPrototypeName = read_from_xml_node(formation, "Prototype")
                distBetweenVehicles = read_from_xml_node(formation, "DistBetweenVehicles", do_not_warn=True)
                if distBetweenVehicles is not None:
                    self.overridesDistBetweenVehicles = True
                    self.formationDistBetweenVehicles = float(distBetweenVehicles)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.formationPrototypeId = prototype_manager.GetPrototypeId(self.formationPrototypeName)


class CaravanTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.tradersGeneratorPrototypeName = ""
        self.guardsGeneratorPrototypeName = ""
        self.tradersGeneratorPrototypeId = -1
        self.guardsGeneratorPrototypeId = -1
        self.waresPrototypes = []
        self.formationPrototypeName = "caravanFormation"

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.tradersGeneratorPrototypeName = safe_check_and_set(self.tradersGeneratorPrototypeName, xmlNode,
                                                                    "TradersVehiclesGeneratorName")
            self.guardsGeneratorPrototypeName = safe_check_and_set(self.guardsGeneratorPrototypeName, xmlNode,
                                                                   "GuardVehiclesGeneratorName")
            waresPrototypes = read_from_xml_node(xmlNode, "WaresPrototypes", do_not_warn=True)
            if waresPrototypes is not None:
                self.waresPrototypes = waresPrototypes.split()
            if self.tradersGeneratorPrototypeName is not None:
                if self.waresPrototypes is None:
                    logger.error(f"No wares for caravan with traders: {self.prototypeName}")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        TeamPrototypeInfo.PostLoad(self, prototype_manager)
        self.tradersGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.tradersGeneratorPrototypeName)
        if self.tradersGeneratorPrototypeId == -1:
            logger.error(f"Unknown VehiclesGenerator '{self.tradersGeneratorPrototypeName}' "
                         f"for traders of CaravanTeam {self.prototypeName}")

        self.guardsGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.guardsGeneratorPrototypeName)
        if self.guardsGeneratorPrototypeId == -1:
            logger.error(f"Unknown VehiclesGenerator '{self.guardsGeneratorPrototypeName}' "
                         f"for guards of CaravanTeam {self.prototypeName}")


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
        self.vehiclesGeneratorProtoId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.vehiclesGeneratorProtoName = safe_check_and_set(self.vehiclesGeneratorProtoName, xmlNode,
                                                                 "VehiclesGenerator")
            vehicles = child_from_xml_node(xmlNode, "Vehicles", do_not_warn=True)
            if vehicles is not None and len(vehicles.getchildren()) >= 1:
                check_mono_xml_node(vehicles, "Vehicle")
                for vehicle in vehicles.iterchildren(tag="Vehicle"):
                    item = {"protoName": read_from_xml_node(vehicle, "PrototypeName"),
                            "count": int(read_from_xml_node(vehicle, "Count"))}
                    self.items.append(item)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        TeamPrototypeInfo.PostLoad(self, prototype_manager)
        self.vehiclesGeneratorProtoId = prototype_manager.GetPrototypeId(self.vehiclesGeneratorProtoName)
        if self.vehiclesGeneratorProtoId == -1:
            if not self.items:
                if self.vehiclesGeneratorProtoName:
                    logger.error(f"Unknown '{self.vehiclesGeneratorProtoName}' VehiclesGenerator "
                                 f"for infection team '{self.prototypeName}'")
                else:
                    logger.error(f"No vehicle generator and no vehicles for InfectionTeam '{self.prototypeName}'")




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
                    for description_entry in xmlNode.iterchildren(tag="Description"):
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

    def PostLoad(self, prototype_manager):
        if self.vehicleDescriptions:
            for vehicle_description in self.vehicleDescriptions:
                vehicle_description.PostLoad(prototype_manager)

    class VehicleDescription(object):
        def __init__(self, xmlFile, xmlNode):
            self.waresPrototypesNames = []
            self.waresPrototypesIds = []

            self.vehiclePrototypeNames = []
            self.vehiclePrototypeIds = []

            self.gunAffixGeneratorPrototypeName = ""
            self.gunAffixGeneratorPrototypeId = -1
            self.LoadFromXML(xmlFile, xmlNode)

        def LoadFromXML(self, xmlFile, xmlNode):
            self.partOfSchwartz = -1.0
            partOfSchwartz = read_from_xml_node(xmlNode, "PartOfSchwartz", do_not_warn=True)
            if partOfSchwartz is not None:
                self.partOfSchwartz = float(partOfSchwartz)
            self.tuningBySchwartz = self.partOfSchwartz > 0.0

            vehiclesPrototypes = read_from_xml_node(xmlNode, "VehiclesPrototypes", do_not_warn=True)
            if vehiclesPrototypes is not None:
                self.vehiclePrototypeNames = vehiclesPrototypes.split()

            waresPrototypesNames = read_from_xml_node(xmlNode, "WaresPrototypes", do_not_warn=True)
            if waresPrototypesNames is not None:
                self.waresPrototypesNames = waresPrototypesNames.split()

            self.gunAffixGeneratorPrototypeName = safe_check_and_set(self.gunAffixGeneratorPrototypeName, xmlNode,
                                                                     "GunAffixGeneratorPrototype")

        def PostLoad(self, prototype_manager):
            for vehicle_prot_name in self.vehiclePrototypeNames:
                vehicle_prot_id = prototype_manager.GetPrototypeId(vehicle_prot_name)
                if vehicle_prot_id == -1:
                    logger.error(f"Unknown vehicle prototype: '{vehicle_prot_name}' found"
                                 f" for VehiclesGenerator: '{self.prototypeName}'")
                prot = prototype_manager.InternalGetPrototypeInfo(vehicle_prot_name)
                if prot.className != "Vehicle":
                    logger.error(f"Unexpected prototype with class '{prot.className}' found "
                                 "for VehiclesGenerator's VehiclePrototypes, expected 'Vehicle'!")
                self.vehiclePrototypeIds.append(vehicle_prot_id)

            for ware_prot_name in self.waresPrototypesNames:
                ware_prot_id = prototype_manager.GetPrototypeId(ware_prot_name)
                if ware_prot_id == -1:
                    logger.error(f"Unknown ware prototype: '{ware_prot_id}' found"
                                 f" for VehiclesGenerator: '{self.prototypeName}'")
                prot = prototype_manager.InternalGetPrototypeInfo(ware_prot_name)
                if prot.className != "Ware":
                    logger.error(f"Unexpected prototype with class '{prot.className}' found "
                                 "for VehiclesGenerator's WaresPrototypes, expected 'Ware'!")
                self.waresPrototypesIds.append(ware_prot_id)

            if self.gunAffixGeneratorPrototypeName:
                self.gunAffixGeneratorPrototypeId = \
                    prototype_manager.GetPrototypeId(self.gunAffixGeneratorPrototypeName)
                if self.gunAffixGeneratorPrototypeId == -1:
                    logger.error(f"Unknown GunAffix prototype: '{self.gunAffixGeneratorPrototypeName}' found"
                                 f" for VehiclesGenerator: '{self.prototypeName}'")


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
                x_change = first_point['x'] - second_point['x']
                y_change = first_point['y'] - second_point['y']
                segmentLength = sqrt(x_change**2 + y_change**2)
                self.polylineLength += segmentLength
                if i < self.headPosition:
                    self.headOffset += segmentLength

    def LoadPolylinePoints(self, xmlFile, xmlNode):
        polyline = child_from_xml_node(xmlNode, "Polyline")
        if polyline is not None:
            check_mono_xml_node(xmlNode["Polyline"], "Point")
            for child in xmlNode["Polyline"].iterchildren(tag="Point"):
                point = read_from_xml_node(child, "Coord").split()
                if len(point) == 2:
                    point = {"x": float(point[0]),
                             "y": float(point[1])}
                    if point["x"] == 0.0 or point["y"] == 0.0:
                        if self.polylinePoints:
                            self.headPosition = len(self.polylinePoints)
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
                self.zoneInfos.append(zone_info)
            self.vehiclesPrototypeName = read_from_xml_node(xmlNode, "Vehicles")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.vehiclesPrototypeName:
            self.vehiclesPrototypeId = prototype_manager.GetPrototypeId(self.vehiclesPrototypeName)
            if self.vehiclesPrototypeId == -1:
                logger.error(f"Invalid vehicles prototype '{self.vehiclesPrototypeName}' "
                             f"for settlement prototype '{self.prototypeName}'")

    class AuxZoneInfo(object):
        def __init__(self):
            self.action = ""
            self.offset = deepcopy(ZERO_VECTOR)
            self.radius = 10.0


class TownPrototypeInfo(SettlementPrototypeInfo):
    def __init__(self, server):
        SettlementPrototypeInfo.__init__(self, server)
        self.musicName = ""
        self.gateModelName = ""
        self.maxDefenders = 1
        self.desiredGunsInWorkshop = 0
        self.gunAffixesCount = 0
        self.cabinsAndBasketsAffixesCount = 0
        self.numCollisionLayersBelowVehicle = 2
        self.articles = []
        self.resourceIdToRandomCoeffMap = []
        self.gunGeneratorPrototypeName = ""
        self.gunGeneratorPrototypeId = -1
        self.gunAffixGeneratorPrototypeName = ""
        self.gunAffixGeneratorPrototypeId = -1
        self.cabinsAndBasketsAffixGeneratorPrototypeName = ""
        self.cabinsAndBasketsAffixGeneratorPrototypeId = -1
        self.collisionTrimeshAllowed = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SettlementPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            self.musicName = safe_check_and_set(self.musicName, xmlNode, "MusicName")
            self.gateModelName = safe_check_and_set(self.gateModelName, xmlNode, "GateModelFile")
            self.maxDefenders = safe_check_and_set(self.maxDefenders, xmlNode, "MaxDefenders", "int")
            if self.maxDefenders > 5:
                logger.error(f"For Town prototype '{self.prototypeName}' maxDefenders > MAX_VEHICLES_IN_TEAM (5)!")
            self.gunGeneratorPrototypeName = safe_check_and_set(self.gunGeneratorPrototypeName, xmlNode, "GunGenerator")
            desiredGunsInWorkshop = safe_check_and_set(self.desiredGunsInWorkshop, xmlNode,
                                                       "DesiredGunsInWorkshop", "int")
            if desiredGunsInWorkshop >= 0:
                self.desiredGunsInWorkshop = desiredGunsInWorkshop
            self.gunAffixGeneratorPrototypeName = safe_check_and_set(self.gunAffixGeneratorPrototypeName, xmlNode,
                                                                     "GunAffixGenerator")
            gunAffixesCount = safe_check_and_set(self.gunAffixesCount, xmlNode, "GunAffixesCount", "int")
            if gunAffixesCount >= 0:
                self.gunAffixesCount = gunAffixesCount
            self.cabinsAndBasketsAffixGeneratorPrototypeName = safe_check_and_set(
                self.cabinsAndBasketsAffixGeneratorPrototypeName,
                xmlNode,
                "CabinsAndBasketsAffixGenerator")
            cabinsAndBasketsAffixesCount = safe_check_and_set(self.cabinsAndBasketsAffixesCount, xmlNode,
                                                              "CabinsAndBasketsAffixesCount", "int")
            if cabinsAndBasketsAffixesCount >= 0:
                self.cabinsAndBasketsAffixesCount = cabinsAndBasketsAffixesCount

            numCollisionLayersBelowVehicle = safe_check_and_set(self.numCollisionLayersBelowVehicle, xmlNode,
                                                                "NumCollisionLayersBelowVehicle", "int")
            if numCollisionLayersBelowVehicle >= 0:
                self.numCollisionLayersBelowVehicle = numCollisionLayersBelowVehicle
            Article.LoadArticlesFromNode(self.articles, xmlFile, xmlNode, self.theServer.thePrototypeManager)
            self.LoadFromXmlResourceIdToRandomCoeffMap(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def LoadFromXmlResourceIdToRandomCoeffMap(self, xmlFile, xmlNode):
        self.resourceIdToRandomCoeffMap = []
        resource_coeffs = child_from_xml_node(xmlNode, "ResourceCoeff", do_not_warn=True)
        if resource_coeffs is not None:
            for resource_coeff_node in resource_coeffs:
                newRandomCoeff = 1.0
                newRandomCoeff_4 = 0.0
                newRandomCoeff = safe_check_and_set(newRandomCoeff, resource_coeff_node, "Coeff", "float")
                newRandomCoeff_4 = safe_check_and_set(newRandomCoeff_4, resource_coeff_node, "Dispersion", "float")
                resourceName = safe_check_and_set("", resource_coeff_node, "Resource")
                resourceId = self.theServer.theResourceManager.GetResourceId(resourceName)
                if resourceId == -1:
                    logger.error(f"Unknown resource name: {resourceName} for prot: {self.prototypeName}")
                else:
                    coeff = {"first": resourceId,
                             "second": self.RandomCoeffWithDispersion()}
                    coeff["second"].baseCoeff = newRandomCoeff
                    coeff["second"].baseDispersion = newRandomCoeff_4
                    self.resourceIdToRandomCoeffMap.append(coeff)

    def PostLoad(self, prototype_manager):
        SettlementPrototypeInfo.PostLoad(self, prototype_manager)
        self.gunGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.gunGeneratorPrototypeName)
        self.gunAffixGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.gunAffixGeneratorPrototypeName)
        self.cabinsAndBasketsAffixGeneratorPrototypeId = \
            prototype_manager.GetPrototypeId(self.cabinsAndBasketsAffixGeneratorPrototypeName)
        if self.articles:
            for article in self.articles:
                article.PostLoad(prototype_manager)

    class RandomCoeffWithDispersion(object):
        def __init__(self):
            self.baseCoeff = 1.0
            self.baseDispersion = 0.0


class LairPrototypeInfo(SettlementPrototypeInfo):
    def __init__(self, server):
        SettlementPrototypeInfo.__init__(self, server)
        self.maxAttackers = 1
        self.maxDefenders = 1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SettlementPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            self.maxAttackers = safe_check_and_set(self.maxAttackers, xmlNode, "MaxAttackers", "int")
            if self.maxAttackers > 5:
                logger.error(f"Lair {self.prototypeName} attrib MaxAttackers: "
                             f"{self.maxAttackers} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")

            self.maxDefenders = safe_check_and_set(self.maxDefenders, xmlNode, "MaxDefenders", "int")
            if self.maxDefenders > 5:
                logger.error(f"Lair {self.prototypeName} attrib MaxDefenders: "
                             f"{self.maxDefenders} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")
            return STATUS_SUCCESS


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
        self.targetSchwarzPart = 0.0

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
            self.engineModelName = safe_check_and_set(self.engineModelName, xmlNode, "ModelFile")
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
            for attack_node in attack_actions.iterchildren(tag="Attack"):
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

            self.blockingContainerPrototypeName = safe_check_and_set(self.blockingContainerPrototypeName, xmlNode,
                                                                     "ContainerPrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blockingContainerPrototypeId = prototype_manager.GetPrototypeId(self.blockingContainerPrototypeName)


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
            for attack_node in attack_actions.iterchildren(tag="Attack"):
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

    def PostLoad(self, prototype_manager):
        if self.loadPrototypeNames:
            for prot_name in self.loadPrototypeNames:
                prot_id = prototype_manager.GetPrototypeId(prot_name)
                if prot_id == -1:
                    logger.error("Invalid loadPrototypes/IDs for BossMetalArm prototype")
                else:
                    prot = prototype_manager.InternalGetPrototypeInfo(prot_name)
                    if prot.className != "BossMetalArmLoad":
                        logger.error("Invalid class for BossMetalArm LoadPrototype, expected 'BossMetalArmLoad', but "
                                     f"'{prot.className}' given for {self.prototypeName}!")
                    self.loadProrotypeIds.append(prot_id)
        else:
            logger.error(f"Empty loadPrototypes for BossMetalArm prototype {self.prototypeName}!")

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
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWavePrototype")
            self.explosionEffectName = safe_check_and_set(self.explosionEffectName, xmlNode, "ExplosionEffect")

            maxHealth = read_from_xml_node(xmlNode, "MaxHealth")
            if maxHealth is not None:
                self.maxHealth = float(maxHealth)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)


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
            for state_node in states_node.iterchildren(tag="State"):
                state = self.StateInfo()
                state.LoadFromXML(xmlFile, state_node)
            speed = read_from_xml_node(xmlNode, "Speed")
            if speed is not None:
                self.speed = float(speed)
            self.containerPrototypeName = read_from_xml_node(xmlNode, "ContainerPrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for state_info in self.stateInfos:
            state_info.PostLoad(prototype_manager)
        self.containerPrototypeId = prototype_manager.GetPrototypeId(self.containerPrototypeName)

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

        def PostLoad(self, prototype_manager):
            for prot_name in self.loadPrototypeNames:
                self.loadPrototypeIds.append(prototype_manager.GetPrototypeId(prot_name))


class AnimatedComplexPhysicObjPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)


class Boss03PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        AnimatedComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.dronePrototypeIds = []
        self.maxDrones = 1
        self.droneRelPosition = deepcopy(ZERO_VECTOR)
        self.droneRelRotation = deepcopy(IDENTITY_QUATERNION)
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
        self.dronePrototypeNames = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.dronePrototypeNames = read_from_xml_node(xmlNode, "DronePrototypes").split()
            maxDrones = read_from_xml_node(xmlNode, "MaxDrones")
            if maxDrones is not None:
                self.maxDrones = int(maxDrones)

            maxHealth = read_from_xml_node(xmlNode, "MaxHealth")
            if maxHealth is not None:
                self.maxHealth = float(maxHealth)

            maxHorizAngularVelocity = read_from_xml_node(xmlNode, "MaxHorizAngularVelocity")
            if maxHorizAngularVelocity is not None:
                self.maxHorizAngularVelocity = float(maxHorizAngularVelocity)

            horizAngularAcceleration = read_from_xml_node(xmlNode, "HorizAngularAcceleration")
            if horizAngularAcceleration is not None:
                self.horizAngularAcceleration = float(horizAngularAcceleration)

            vertAngularAcceleration = read_from_xml_node(xmlNode, "VertAngularAcceleration")
            if vertAngularAcceleration is not None:
                self.vertAngularAcceleration = float(vertAngularAcceleration)

            maxLinearVelocity = read_from_xml_node(xmlNode, "MaxLinearVelocity")
            if maxLinearVelocity is not None:
                self.maxLinearVelocity = float(maxLinearVelocity)

            linearAcceleration = read_from_xml_node(xmlNode, "LinearAcceleration")
            if linearAcceleration is not None:
                self.linearAcceleration = float(linearAcceleration)

            pathTrackTiltAngle = read_from_xml_node(xmlNode, "PathTrackTiltAngle")
            if pathTrackTiltAngle is not None:
                self.pathTrackTiltAngle = float(pathTrackTiltAngle) * pi / 180  # 0.017453292

            maxShootingTime = read_from_xml_node(xmlNode, "MaxShootingTime")
            if maxShootingTime is not None:
                self.maxShootingTime = float(maxShootingTime)

            defaultHover = read_from_xml_node(xmlNode, "DefaultHover")
            if defaultHover is not None:
                self.defaultHover = float(defaultHover)

            hoverForPlacingDrones = read_from_xml_node(xmlNode, "HoverForPlacingDrones")
            if hoverForPlacingDrones is not None:
                self.hoverForPlacingDrones = float(hoverForPlacingDrones)

            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for prot_name in self.dronePrototypeNames:
            dronePrototypeId = prototype_manager.GetPrototypeId(prot_name)
            if dronePrototypeId == -1:
                logger.error("Invalid drone prototype/prototype ID for Boss03")
            self.dronePrototypeIds.append(dronePrototypeId)


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
            self.stationPrototypeName = read_from_xml_node(xmlNode, "StationPrototype")
            self.dronePrototypeName = read_from_xml_node(xmlNode, "DronePrototype")
            self.timeBetweenDrones = read_from_xml_node(xmlNode, "TimeBetweenDrones").split()
            maxDrones = read_from_xml_node(xmlNode, "MaxDrones")
            if maxDrones is not None:
                maxDrones = int(maxDrones)
                if maxDrones > 0:
                    self.maxDrones = maxDrones
            self.droneSpawningLpNames = read_from_xml_node(xmlNode, "DroneSpawningLps").split()
            stationToPartBindings = child_from_xml_node(xmlNode, "StationToPartBindings")
            check_mono_xml_node(stationToPartBindings, "Station")
            for station_node in stationToPartBindings.iterchildren(tag="Station"):
                station = {"id": read_from_xml_node(station_node, "id"),
                           "parts": read_from_xml_node(station_node, "Parts").split()}
                self.stationToPartBindings.append(station)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        self.stationPrototypeId = prototype_manager.GetPrototypeId(self.stationPrototypeName)
        self.dronePrototypeId = prototype_manager.GetPrototypeId(self.dronePrototypeName)


class BlastWavePrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.waveForceIntensity = 0.0
        self.waveDamageIntensity = 0.0
        self.effectName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("SPHERE")
        waveForceIntensity = read_from_xml_node(xmlNode, "WaveForceIntensity")
        if waveForceIntensity is not None:
            self.waveForceIntensity = float(waveForceIntensity)

        waveDamageIntensity = read_from_xml_node(xmlNode, "WaveDamageIntensity")
        if waveDamageIntensity is not None:
            self.waveDamageIntensity = float(waveDamageIntensity)

        self.effectName = read_from_xml_node(xmlNode, "Effect")
        return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class BulletLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.groupingAngle = 0.0
        self.numBulletsInShot = 1
        self.blastWavePrototypeName = ""
        self.tracerRange = 1
        self.tracerEffectName = ""
        self.damageType = 0


class CompoundVehiclePartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.partInfo = {}

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            parts_description_nodes = child_from_xml_node(xmlNode, "Part", do_not_warn=True)
            if parts_description_nodes is not None:
                descriptions_number = len(parts_description_nodes)
                for i in range(descriptions_number):
                    part_node = parts_description_nodes[i]
                    new_part = self.TPartInfo()
                    part_id = safe_check_and_set(new_part.prototypeId, part_node, "id")
                    new_part.prototypeName = safe_check_and_set(new_part.prototypeName, part_node, "Prototype")
                    new_part.index = i
                    self.partInfo[part_id] = new_part
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        for tpart in self.partInfo.values():
            tpart.prototypeId = prototype_manager.GetPrototypeId(tpart.prototypeName)

    class TPartInfo(object):
        def __init__(self):
            self.prototypeName = ""
            self.prototypeId = ""
            self.index = 0


class CompoundGunPrototypeInfo(CompoundVehiclePartPrototypeInfo):
    def __init__(self, server):
        CompoundVehiclePartPrototypeInfo.__init__(self, server)


class RocketLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.withAngleLimit = True
        self.damageType = 1
        self.withShellsPoolLimit = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.withAngleLimit = parse_str_to_bool(read_from_xml_node(xmlNode, "WithAngleLimit", do_not_warn=True))
            return STATUS_SUCCESS


class RocketVolleyLauncherPrototypeInfo(RocketLauncherPrototypeInfo):
    def __init__(self, server):
        RocketLauncherPrototypeInfo.__init__(self, server)
        self.actionDist = 0.0
        # self.withShellsPoolLimit = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            actionDist = read_from_xml_node(xmlNode, "ActionDist")
            if actionDist is not None:
                self.actionDist = float(actionDist)
            return STATUS_SUCCESS


class ThunderboltLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.damageType = 2
        self.withShellsPoolLimit = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            actionDist = read_from_xml_node(xmlNode, "ActionDist")
            if actionDist is not None:
                self.actionDist = float(actionDist)
            return STATUS_SUCCESS


class PlasmaBunchLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.bunchPrototypeName = ""
        self.damageType = 2
        self.withShellsPoolLimit = True


class MortarPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.damageType = 1
        self.withShellsPoolLimit = True
        self.initialVelocity = 50.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            initialVelocity = read_from_xml_node(xmlNode, "InitialVelocity")
            if initialVelocity is not None:
                self.initialVelocity = float(initialVelocity)
            return STATUS_SUCCESS


class MortarVolleyLauncherPrototypeInfo(MortarPrototypeInfo):
    def __init__(self, server):
        MortarPrototypeInfo.__init__(self, server)


class LocationPusherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)


class MinePusherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.damageType = 1


class TurboAccelerationPusherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.accelerationValue = 1.0
        self.accelerationTime = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            accelerationValue = read_from_xml_node(xmlNode, "AccelerationValue")
            if accelerationValue is not None:
                self.accelerationValue = float(accelerationValue)

            accelerationTime = read_from_xml_node(xmlNode, "AccelerationTime")
            if accelerationTime is not None:
                self.accelerationTime = float(accelerationTime)
            return STATUS_SUCCESS


class ShellPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)


class RocketPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = 1.0
        self.acceleration = 1.0
        self.minTurningRadius = 1.0
        self.flyTime = 1.0
        self.blastWavePrototypeId = -1
        self.blastWavePrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            velocity = read_from_xml_node(xmlNode, "Velocity")
            if velocity is not None:
                self.velocity = float(velocity)

            acceleration = read_from_xml_node(xmlNode, "Acceleration")
            if acceleration is not None:
                self.acceleration = float(acceleration)

            minTurningRadius = read_from_xml_node(xmlNode, "MinTurningRadius")
            if minTurningRadius is not None:
                self.minTurningRadius = float(minTurningRadius)

            flyTime = read_from_xml_node(xmlNode, "FlyTime")
            if flyTime is not None:
                self.flyTime = float(flyTime)

            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWavePrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)
            if self.blastWavePrototypeId == -1:
                logger.error(f"Unknown blast wave prototype name: '{self.blastWavePrototypeName}' "
                             f"for rocket prototype: '{self.prototypeName}'")


class PlasmaBunchPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = 1.0
        self.acceleration = 1.0
        self.flyTime = 1.0
        self.blastWavePrototypeName = ""
        self.blastWavePrototypeId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            velocity = read_from_xml_node(xmlNode, "Velocity")
            if velocity is not None:
                self.velocity = float(velocity)

            acceleration = read_from_xml_node(xmlNode, "Acceleration")
            if acceleration is not None:
                self.acceleration = float(acceleration)

            flyTime = read_from_xml_node(xmlNode, "FlyTime")
            if flyTime is not None:
                self.flyTime = float(flyTime)
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWavePrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)


class MortarShellPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = 1.0
        self.acceleration = 1.0
        self.flyTime = 1.0
        self.blastWavePrototypeId = -1
        self.blastWavePrototypeName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            flyTime = read_from_xml_node(xmlNode, "FlyTime")
            if flyTime is not None:
                self.flyTime = float(flyTime)
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWavePrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)
        if self.blastWavePrototypeId == -1 and self.blastWavePrototypeName:
            logger.error(f"Unknown blast wave prototype name: {self.prototypeName}")


class MinePrototypeInfo(RocketPrototypeInfo):
    def __init__(self, server):
        RocketPrototypeInfo.__init__(self, server)
        self.TTL = 100.0
        self.timeForActivation = 0.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = RocketPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            TTL = read_from_xml_node(xmlNode, "TTL")
            if TTL is not None:
                self.TTL = float(TTL)

            timeForActivation = read_from_xml_node(xmlNode, "TimeForActivation")
            if timeForActivation is not None:
                self.timeForActivation = float(timeForActivation)
            return STATUS_SUCCESS


class ThunderboltPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.flyTime = 1.0
        self.damage = 0.0
        self.averageSegmentLength = 0.1
        self.effectName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            flyTime = read_from_xml_node(xmlNode, "FlyTime")
            if flyTime is not None:
                self.flyTime = float(flyTime)

            damage = read_from_xml_node(xmlNode, "Damage", do_not_warn=True)
            if damage is not None:
                self.damage = float(damage)

            averageSegmentLength = read_from_xml_node(xmlNode, "AverageSegmentLength")
            if averageSegmentLength is not None:
                self.averageSegmentLength = float(averageSegmentLength)

            self.effectName = read_from_xml_node(xmlNode, "Effect")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.averageSegmentLength < 0.01:
            self.averageSegmentLength = 0.01


class BulletPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("RAY")
            return STATUS_SUCCESS


class TemporaryLocationPrototypeInfo(LocationPrototypeInfo):
    def __init__(self, server):
        LocationPrototypeInfo.__init__(self, server)
        self.TTL = 0.0
        self.timeForActivation = 0.0
        self.effectName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = LocationPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            TTL = read_from_xml_node(xmlNode, "TTL")
            if TTL is not None:
                self.TTL = float(TTL)

            timeForActivation = read_from_xml_node(xmlNode, "ActivateTime")
            if timeForActivation is not None:
                self.timeForActivation = float(timeForActivation)

            self.effectName = read_from_xml_node(xmlNode, "Effect")
            return STATUS_SUCCESS


class NailLocationPrototypeInfo(TemporaryLocationPrototypeInfo):
    def __init__(self, server):
        TemporaryLocationPrototypeInfo.__init__(self, server)


class SmokeScreenLocationPrototypeInfo(TemporaryLocationPrototypeInfo):
    def __init__(self, server):
        TemporaryLocationPrototypeInfo.__init__(self, server)


class EngineOilLocationPrototypeInfo(TemporaryLocationPrototypeInfo):
    def __init__(self, server):
        TemporaryLocationPrototypeInfo.__init__(self, server)


class SubmarinePrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)
        self.maxLinearVelocity = 0.0
        self.linearAcceleration = 0.0
        self.platformOpenFps = 2
        self.vehicleMaxSpeed = 72.0
        self.vehicleRelativePosition = deepcopy(ZERO_VECTOR)
        self.isUpdating = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxLinearVelocity = read_from_xml_node(xmlNode, "MaxLinearVelocity")
            if maxLinearVelocity is not None:
                self.maxLinearVelocity = float(maxLinearVelocity)

            linearAcceleration = read_from_xml_node(xmlNode, "LinearAcceleration")
            if linearAcceleration is not None:
                self.linearAcceleration = float(linearAcceleration)

            platformOpenFps = read_from_xml_node(xmlNode, "PlatformOpenFps")
            if platformOpenFps is not None:
                self.platformOpenFps = int(platformOpenFps)

            vehicleMaxSpeed = read_from_xml_node(xmlNode, "VehicleMaxSpeed", do_not_warn=True)
            if vehicleMaxSpeed is not None:
                self.vehicleMaxSpeed = float(vehicleMaxSpeed)

            self.maxLinearVelocity *= 0.27777779  # ~5/18 or 50/180
            self.vehicleMaxSpeed *= 0.27777779
            return STATUS_SUCCESS


class BuildingPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.buildingType = 5

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            buildingTypeName = safe_check_and_set("", xmlNode, "BuildingType")
            self.buildingType = Building.GetBuildingTypeByName(buildingTypeName)
            return STATUS_SUCCESS


class BarPrototypeInfo(BuildingPrototypeInfo):
    def __init__(self, server):
        BuildingPrototypeInfo.__init__(self, server)
        self.withBarman = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = BuildingPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.withBarman = read_from_xml_node(xmlNode, "WithBarman")
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class WorkshopPrototypeInfo(BuildingPrototypeInfo):
    def __init__(self, server):
        BuildingPrototypeInfo.__init__(self, server)


class WarePrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.maxDurability = 1.0
        self.maxItems = 1
        self.priceDispersion = 0.0
        self.modelName = ""
        self.minCount = 0
        self.maxCount = 50

    def LoadFromXML(self, xmlFile, xmlNode):
        result = BuildingPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxItems = read_from_xml_node(xmlNode, "MaxItems", do_not_warn=True)
            if maxItems is not None:
                maxItems = int(maxItems)
                if maxItems >= 0:
                    self.maxItems = maxItems

            maxDurability = read_from_xml_node(xmlNode, "Durability", do_not_warn=True)
            if maxDurability is not None:
                self.maxDurability = float(maxDurability)

            priceDispersion = read_from_xml_node(xmlNode, "PriceDispersion", do_not_warn=True)
            if priceDispersion is not None:
                self.priceDispersion = float(priceDispersion)

            if self.priceDispersion < 0.0 or self.priceDispersion > 100.0:
                logger(f"Price dispersion can't be outside 0.0-100.0 range: see {self.prototypeName}")

            self.modelName = safe_check_and_set(self.modelName, xmlNode, "ModelName")

            minCount = read_from_xml_node(xmlNode, "MinCount", do_not_warn=True)
            if minCount is not None:
                self.minCount = int(minCount)

            maxCount = read_from_xml_node(xmlNode, "MaxCount", do_not_warn=True)
            if maxCount is not None:
                self.maxCount = int(maxCount)
            return STATUS_SUCCESS


class QuestItemPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modelName = ""

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.modelName = safe_check_and_set(self.modelName, xmlNode, "ModelName")
            return STATUS_SUCCESS


class BreakableObjectPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.destroyable = 0
        self.effectType = "WOOD"
        self.destroyEffectType = "BLOW"
        self.brokenModelName = "brokenTest"
        self.destroyedModelName = "brokenTest"
        self.breakEffect = ""
        self.blastWavePrototypeId = -1
        self.blastWavePrototypeName = ""
        self.isUpdating = False

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            destroyable = read_from_xml_node(xmlNode, "Destroyable")
            if destroyable is not None:
                self.destroyable = int(destroyable)

            criticalHitEnergy = read_from_xml_node(xmlNode, "CriticalHitEnergy")
            if criticalHitEnergy is not None:
                self.criticalHitEnergy = float(criticalHitEnergy)

            self.effectType = safe_check_and_set(self.effectType, xmlNode, "EffectType")
            self.destroyEffectType = safe_check_and_set(self.destroyEffectType, xmlNode, "DestroyEffectType")
            self.brokenModelName = safe_check_and_set(self.brokenModelName, xmlNode, "BrokenModel")
            self.destroyedModelName = safe_check_and_set(self.destroyedModelName, xmlNode, "DestroyedModel")
            self.breakEffect = safe_check_and_set(self.breakEffect, xmlNode, "BreakEffect")
            self.blastWavePrototypeName = safe_check_and_set(self.blastWavePrototypeName, xmlNode, "BlastWave")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName)


class ParticleSplinterPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)


class VehicleSplinterPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)


class PhysicUnitPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.walkSpeed = 1.0
        self.turnSpeed = 1.0
        self.maxStandTime = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            walkSpeed = read_from_xml_node(xmlNode, "WalkSpeed", do_not_warn=True)
            if walkSpeed is not None:
                self.walkSpeed = float(walkSpeed)

            maxStandTime = read_from_xml_node(xmlNode, "MaxStandTime", do_not_warn=True)
            if maxStandTime is not None:
                self.maxStandTime = float(maxStandTime)

            turnSpeed = read_from_xml_node(xmlNode, "TurnSpeed", do_not_warn=True)
            if turnSpeed is not None:
                self.turnSpeed = float(turnSpeed)
            return STATUS_SUCCESS


class JointedObjPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class CompositeObjPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class GeomObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)


class RopeObjPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.brokenModel = ""
        self.isUpdating = False

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            self.brokenModel = read_from_xml_node(xmlNode, "BrokenModel")
            return STATUS_SUCCESS


class ObjPrefabPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.objInfos = []
        self.isUpdating = False

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            obj_infos_node = child_from_xml_node(xmlNode, "ObjInfos")
            if obj_infos_node is not None:
                check_mono_xml_node(obj_infos_node, "ObjInfo")
                for obj_info_node in obj_infos_node.iterchildren(tag="ObjInfo"):
                    obj_info = self.ObjInfo()
                    obj_info.prototypeName = read_from_xml_node(obj_info_node, "Prototype")
                    if obj_info.prototypeName is not None:
                        obj_info.relPos = parse_str_to_vector(read_from_xml_node(obj_info_node, "RelPos",
                                                                                 do_not_warn=True))
                        obj_info.relRot = parse_str_to_quaternion(read_from_xml_node(obj_info_node, "RelRot",
                                                                                     do_not_warn=True))
                        obj_info.modelName = safe_check_and_set(obj_info.prototypeName, obj_info_node, "ModelName")
                        scale = read_from_xml_node(obj_info_node, "Scale", do_not_warn=True)
                        if scale is not None:
                            obj_info.scale = float(scale)
                    else:
                        logger.error(f"Invalid object info in {SimplePhysicObjPrototypeInfo.prototypeName}")
                    self.objInfos.append(obj_info)
            else:
                logger.error(f"Missing ObjectsInfo in {SimplePhysicObjPrototypeInfo.prototypeName}")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.objInfos:
            for objInfo in self.objInfos:
                objInfo.prototypeId = prototype_manager.GetPrototypeId(objInfo.prototypeName)

    class ObjInfo(object):
        def __init__(self):
            self.prototypeId = -1
            self.relPos = deepcopy(ZERO_VECTOR)
            self.relRot = deepcopy(IDENTITY_QUATERNION)
            self.scale = 1.0
            self.modelName = ""
            self.prototypeName = ""

        def PostLoad(self, prototype_manager):
            self.prototypeId = prototype_manager.GetPrototypeId(self.prototypeName)
            logger.warning("This is not a fucking useless function after all!")


class BarricadePrototypeInfo(ObjPrefabPrototypeInfo):
    def __init__(self, server):
        ObjPrefabPrototypeInfo.__init__(self, server)
        self.objInfos = []
        self.probability = 1.0

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ObjPrefabPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            probability = read_from_xml_node(xmlNode, "Probability")
            if probability is not None:
                self.probability = float(probability)
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class NpcPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.isUpdating = False


class RepositoryObjectsGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.objectDescriptions = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            objects = child_from_xml_node(xmlNode, "Object")
            for object_node in objects:
                newDescription = self.ObjectDescription()
                newDescription.prototypeName = safe_check_and_set("", xmlNode, "PrototypeName")
                newDescription.prototypeId = -1
                self.objectDescriptions.append(newDescription)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.objectDescriptions:
            for obj_description in self.objectDescriptions:
                obj_description.prototypeId = prototype_manager.GetPrototypeId(obj_description.prototypeName)
                if obj_description.prototypeId == -1:
                    logger.error(f"Unknown Object prototype: '{obj_description.prototypeName}' "
                                 f"for RepositoryObjectsGenerator: '{self.prototypeName}'")

    class ObjectDescription(object):
        def __init__(self):
            self.prototypeName = ""
            self.prototypeId = -1


# dict mapping Object Classes to PrototypeInfo Classes
thePrototypeInfoClassDict = {
    "AffixGenerator": AffixGeneratorPrototypeInfo,
    "ArticulatedVehicle": ArticulatedVehiclePrototypeInfo,
    "Bar": BarPrototypeInfo,
    "Barricade": BarricadePrototypeInfo,
    "Basket": BasketPrototypeInfo,
    "BlastWave": BlastWavePrototypeInfo,
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
    "BreakableObject": BreakableObjectPrototypeInfo,
    "Building": BuildingPrototypeInfo,
    "BulletLauncher": BulletLauncherPrototypeInfo,
    "Bullet": BulletPrototypeInfo,
    "Cabin": CabinPrototypeInfo,
    "CaravanTeam": CaravanTeamPrototypeInfo,
    "Chassis": ChassisPrototypeInfo,
    "Chest": ChestPrototypeInfo,
    "CinematicMover": CinematicMoverPrototypeInfo,
    "CompositeObj": CompositeObjPrototypeInfo,
    "CompoundGun": CompoundGunPrototypeInfo,
    "CompoundVehiclePart": CompoundVehiclePartPrototypeInfo,
    "DummyObject": DummyObjectPrototypeInfo,
    "DynamicQuestConvoy": DynamicQuestConvoyPrototypeInfo,
    "DynamicQuestDestroy": DynamicQuestDestroyPrototypeInfo,
    "DynamicQuestHunt": DynamicQuestHuntPrototypeInfo,
    "DynamicQuestPeace": DynamicQuestPeacePrototypeInfo,
    "DynamicQuestReach": DynamicQuestReachPrototypeInfo,
    "EngineOilLocation": EngineOilLocationPrototypeInfo,
    "Formation": FormationPrototypeInfo,
    "Gadget": GadgetPrototypeInfo,
    "GeomObj": GeomObjPrototypeInfo,
    "InfectionLair": InfectionLairPrototypeInfo,
    "InfectionTeam": InfectionTeamPrototypeInfo,
    "InfectionZone": InfectionZonePrototypeInfo,
    "JointedObj": JointedObjPrototypeInfo,
    "Lair": LairPrototypeInfo,
    "LightObj": LightObjPrototypeInfo,
    "Location": LocationPrototypeInfo,
    "LocationPusher": LocationPusherPrototypeInfo,
    "Mine": MinePrototypeInfo,
    "MinePusher": MinePusherPrototypeInfo,
    "Mortar": MortarPrototypeInfo,
    "MortarShell": MortarShellPrototypeInfo,
    "MortarVolleyLauncher": MortarVolleyLauncherPrototypeInfo,
    "NPCMotionController": NPCMotionControllerPrototypeInfo,
    "NailLocation": NailLocationPrototypeInfo,
    "Npc": NpcPrototypeInfo,
    "ObjPrefab": ObjPrefabPrototypeInfo,
    "ParticleSplinter": ParticleSplinterPrototypeInfo,
    "PhysicUnit": PhysicUnitPrototypeInfo,
    "PlasmaBunchLauncher": PlasmaBunchLauncherPrototypeInfo,
    "PlasmaBunch": PlasmaBunchPrototypeInfo,
    "Player": PlayerPrototypeInfo,
    "QuestItem": QuestItemPrototypeInfo,
    "RadioManager": RadioManagerPrototypeInfo,
    "RepositoryObjectsGenerator": RepositoryObjectsGeneratorPrototypeInfo,
    "RocketLauncher": RocketLauncherPrototypeInfo,
    "Rocket": RocketPrototypeInfo,
    "RocketVolleyLauncher": RocketVolleyLauncherPrototypeInfo,
    "RopeObj": RopeObjPrototypeInfo,
    "SgNodeObj": SgNodeObjPrototypeInfo,
    "SmokeScreenLocation": SmokeScreenLocationPrototypeInfo,
    "StaticAutoGun": StaticAutoGunPrototypeInfo,  # def InternalCopyFrom(self, prot_to_copy_from): self.parent = prot_to_copy_from
    "Submarine": SubmarinePrototypeInfo,
    "Team": TeamPrototypeInfo,
    "TeamTacticWithRoles": TeamTacticWithRolesPrototypeInfo,
    "ThunderboltLauncher": ThunderboltLauncherPrototypeInfo,
    "Thunderbolt": ThunderboltPrototypeInfo,
    "Town": TownPrototypeInfo,
    "Trigger": TriggerPrototypeInfo,
    "TurboAccelerationPusher": TurboAccelerationPusherPrototypeInfo,
    "VagabondTeam": VagabondTeamPrototypeInfo,
    "VehiclePart": VehiclePartPrototypeInfo,
    "Vehicle": VehiclePrototypeInfo,
    "VehicleRecollection": VehicleRecollectionPrototypeInfo,
    "VehicleRoleBarrier": VehicleRoleBarrierPrototypeInfo,
    "VehicleRoleCheater": VehicleRoleCheaterPrototypeInfo,
    "VehicleRoleCoward": VehicleRoleCowardPrototypeInfo,
    "VehicleRoleMeat": VehicleRoleMeatPrototypeInfo,
    "VehicleRoleOppressor": VehicleRoleOppressorPrototypeInfo,
    "VehicleRolePendulum": VehicleRolePendulumPrototypeInfo,
    "VehicleRoleSniper": VehicleRoleSniperPrototypeInfo,
    "VehicleSplinter": VehicleSplinterPrototypeInfo,
    "VehiclesGenerator": VehiclesGeneratorPrototypeInfo,
    "WanderersGenerator": WanderersGeneratorPrototypeInfo,
    "WanderersManager": WanderersManagerPrototypeInfo,
    "Ware": WarePrototypeInfo,
    "Wheel": WheelPrototypeInfo,
    "Workshop": WorkshopPrototypeInfo
}
