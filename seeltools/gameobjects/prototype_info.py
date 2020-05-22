from math import pi, sqrt
from copy import deepcopy
from lxml import objectify, etree
from enum import Enum

from seeltools.utilities.log import logger

from seeltools.utilities.parse import (read_from_xml_node, child_from_xml_node, check_mono_xml_node, safe_check_and_set,
                                       parse_str_to_bool, parse_str_to_quaternion, parse_str_to_vector,
                                       parse_model_group_health)

from seeltools.utilities.constants import (STATUS_SUCCESS, DEFAULT_TURNING_SPEED, FiringTypesStruct, DamageTypeStruct,
                                           DESTROY_EFFECT_NAMES, TEAM_DEFAULT_FORMATION_PROTOTYPE, GEOM_TYPE,
                                           ZERO_VECTOR, ONE_VECTOR, IDENTITY_QUATERNION)

from seeltools.utilities.global_functions import GetActionByName, GetActionByNum  # , AIParam

from seeltools.utilities.value_classes import AnnotatedValue, DisplayType, GroupType, SavingType
from seeltools.utilities.helper_functions import value_equel_default

from seeltools.gameobjects.object_classes import *


def vector_short_to_string(value):
    return f'{value["x"]} {value["y"]}'

def vector_to_string(value):
    return f'{value["x"]} {value["y"]} {value["z"]}'


def vector_long_to_string(value):
    return f'{value["x"]} {value["y"]} {value["z"]} {value["w"]}'


def add_value_to_node(node, annotatedValue, func=lambda x: str(x.value)):
    if not value_equel_default(annotatedValue.value, annotatedValue.default_value):
        node.set(annotatedValue.name, func(annotatedValue))


def add_value_to_node_as_child(node, annotatedValue, func):
    if not value_equel_default(annotatedValue.value, annotatedValue.default_value):
        result = func(annotatedValue)
        if isinstance(result, list):
            node.extend(result)
        else:
            node.append(result)


class PrototypeInfo(object):
    '''Base Prototype information class'''
    def __init__(self, server):
        self.theServer = server
        self.className = AnnotatedValue("", "Class", group_type=GroupType.GENERAL,
                                        display_type=DisplayType.CLASS_NAME)
        self.prototypeName = AnnotatedValue("", "Name", group_type=GroupType.GENERAL)
        self.prototypeId = -1
        self.resourceId = AnnotatedValue(-1, "ResourceType", display_type=DisplayType.RESOURCE_ID,
                                         saving_type=SavingType.RESOURCE)
        self.isUpdating = AnnotatedValue(True, "IsUpdating", group_type=GroupType.SECONDARY)
        self.visibleInEncyclopedia = AnnotatedValue(True, "VisibleInEncyclopedia", group_type=GroupType.SECONDARY)
        self.applyAffixes = AnnotatedValue(True, "ApplyAffixes", group_type=GroupType.SECONDARY)
        self.price = AnnotatedValue(0, "Price", group_type=GroupType.SECONDARY)
        self.isAbstract = AnnotatedValue(False, "Abstract", group_type=GroupType.SECONDARY)
        self.parentPrototypeName = AnnotatedValue("", "ParentPrototype", group_type=GroupType.GENERAL,
                                                  display_type=DisplayType.PROTOTYPE_NAME)
        self.parentPrototypeId = -1
        self.protoClassObject = 0
        # custom logic
        self.lookupModelFile = False

    def LoadFromXML(self, xmlFile, xmlNode):
        if xmlNode.tag == "Prototype":
            self.prototypeName.value = read_from_xml_node(xmlNode, "Name")
            self.className.value = read_from_xml_node(xmlNode, "Class")
            self.protoClassObject = globals()[self.className.value]  # getting class object by name
            strResType = read_from_xml_node(xmlNode, "ResourceType", do_not_warn=True)
            self.isUpdating.value = parse_str_to_bool(self.isUpdating.default_value,
                                                      read_from_xml_node(xmlNode, "IsUpdating", do_not_warn=True))
            if strResType is not None:
                self.resourceId.value = self.theServer.theResourceManager.GetResourceId(strResType)
            if strResType is not None and self.resourceId.value == -1:
                if not self.parentPrototypeName.value:
                    logger.info(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName.value}")
                elif self.parent.resourceId == -1:
                    logger.info(f"Invalid ResourceType: {strResType} for prototype {self.prototypeName.value} "
                                f" and its parent {self.parent.prototypeName.value}")

            self.visibleInEncyclopedia.value = parse_str_to_bool(self.visibleInEncyclopedia.default_value,
                                                                 read_from_xml_node(xmlNode,
                                                                                    "VisibleInEncyclopedia",
                                                                                    do_not_warn=True))
            self.applyAffixes.value = parse_str_to_bool(self.applyAffixes.default_value,
                                                        read_from_xml_node(xmlNode, "ApplyAffixes", do_not_warn=True))
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price.value = int(price)
            self.isAbstract.value = parse_str_to_bool(self.isAbstract.default_value,
                                                      read_from_xml_node(xmlNode, "Abstract", do_not_warn=True))
            self.parentPrototypeName.value = read_from_xml_node(xmlNode, "ParentPrototype", do_not_warn=True)
            return STATUS_SUCCESS
        else:
            logger.warning(f"XML Node with unexpected tag {xmlNode.tag} given for PrototypeInfo loading")

    def CopyFrom(self, prot_to_copy_from):
        if self.className.value == prot_to_copy_from.className.value:
            self.InternalCopyFrom(prot_to_copy_from)
        else:
            logger.error(f"Unexpected parent prototype class for {self.prototypeName.value}: "
                         f"expected {self.className.value}, got {prot_to_copy_from.className.value}")

    def InternalCopyFrom(self, prot_to_copy_from):
        logger.error(f"CopyFrom is not implemented for PrototypeInfo {self.prototypeName.value}"
                     f" of class {self.className.value}")

    def PostLoad(self, prototype_manager):
        if self.parentPrototypeName.value:
            self.parentPrototypeId.value = prototype_manager.GetPrototypeId(self.parentPrototypeName.value)
            if self.parentPrototypeId.value == -1:
                logger.error(f"Invalid parent prototype: '{self.parentPrototypeName.value}' "
                             f"for prototype: '{self.prototypeName.value}'")

    def get_etree_prototype(self):
        result = etree.Element("Prototype")

        prot_attribs = vars(self)
        for attrib in prot_attribs.values():
            if isinstance(attrib, AnnotatedValue):
                if (
                    attrib.saving_type != SavingType.IGNORE
                    and attrib.saving_type != SavingType.SPECIFIC
                ):
                    if attrib.saving_type == SavingType.COMMON:
                        add_value_to_node(result, attrib)
                    elif attrib.saving_type == SavingType.RESOURCE:
                        add_value_to_node(result, attrib,
                                          lambda x: self.theServer.theResourceManager.GetResourceName(x.value))
        return result


class PhysicBodyPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.engineModelName = AnnotatedValue("", "ModelFile", group_type=GroupType.VISUAL)
        self.massValue = AnnotatedValue(1.0, "Mass", group_type=GroupType.PRIMARY)
        self.collisionInfos = []
        self.collisionTrimeshAllowed = AnnotatedValue(False, "CollisionTrimeshAllowed",
                                                      group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.engineModelName.value = safe_check_and_set(self.engineModelName.value, xmlNode, "ModelFile")
            if not self.engineModelName.value and not issubclass(type(self), CompoundVehiclePartPrototypeInfo):
                logger.error(f"No model file is provided for prototype {self.prototypeName.value}")
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            self.collisionTrimeshAllowed.value = parse_str_to_bool(self.collisionTrimeshAllowed.default_value,
                                                                   read_from_xml_node(xmlNode,
                                                                                      "CollisionTrimeshAllowed",
                                                                                      do_not_warn=True))
            if mass is not None:
                self.massValue.value = float(mass)
            if self.massValue.value < 0.001:
                logger.error(f"Mass is too low for prototype {self.prototypeName.value}")
            return STATUS_SUCCESS

    def RefreshFromXml(self, xmlFile, xmlNode):
        # originaly DataServer.GetItemByName
        # self.engineModelId = self.server.theAnimatedModelsServer.GetItemByName(self.engineModelName.value)
        # GetCollisionInfoByServerHandle(self.engineModelId, self.collisionInfos, self.collisionTrimeshAllowed)
        pass


# class SimplePhysicBodyPrototypeInfo(PhysicBodyPrototypeInfo):
#     def __init__(self, server):
#         PhysicBodyPrototypeInfo.__init__(self, server)


class VehiclePartPrototypeInfo(PhysicBodyPrototypeInfo):
    def __init__(self, server):
        PhysicBodyPrototypeInfo.__init__(self, server)
        self.weaponPrototypeId = -1
        self.durability = AnnotatedValue(0.0, "Durability", group_type=GroupType.PRIMARY)
        self.loadPoints = AnnotatedValue([], "LoadPoints", group_type=GroupType.SECONDARY,
                                         saving_type=SavingType.SPECIFIC)
        self.blowEffectName = AnnotatedValue("ET_PS_HARD_BLOW", "BlowEffect", group_type=GroupType.SECONDARY)
        self.canBeUsedInAutogenerating = AnnotatedValue(True, "CanBeUsedInAutogenerating", group_type=GroupType.PRIMARY)
        self.repairCoef = AnnotatedValue(1.0, "RepairCoef", group_type=GroupType.SECONDARY)
        self.modelMeshes = []
        self.boundsForMeshes = []
        self.verts = []
        self.inds = []
        self.numsTris = []
        self.vertsStride = []
        self.groupHealth = AnnotatedValue({}, "GroupsHealth", group_type=GroupType.SECONDARY,
                                          saving_type=SavingType.SPECIFIC)
        self.durabilityCoeffsForDamageTypes = AnnotatedValue([0.0, 0.0, 0.0], "DurCoeffsForDamageTypes",
                                                             group_type=GroupType.SECONDARY,
                                                             saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicBodyPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.blowEffectName.value = safe_check_and_set(self.blowEffectName.default_value, xmlNode, "BlowEffect")
            durability = read_from_xml_node(xmlNode, "Durability", do_not_warn=True)
            if durability is not None:
                self.durability.value = float(durability)
            strDurabilityCoeffs = read_from_xml_node(xmlNode, "DurCoeffsForDamageTypes", do_not_warn=True)
            if strDurabilityCoeffs is not None:
                self.durabilityCoeffsForDamageTypes.value = [float(coeff) for coeff in strDurabilityCoeffs.split()]
                for coeff in self.durabilityCoeffsForDamageTypes.value:
                    if coeff < -25.1 or coeff > 25.0:
                        logger.error(f"Invalif DurCoeffsForDamageTypes:{coeff} for {self.prototypeName.value}, "
                                     "should be between -25.0 and 25.0")

            loadPoints = read_from_xml_node(xmlNode, "LoadPoints", do_not_warn=True)
            if loadPoints is not None and loadPoints != "":
                self.loadPoints.value = loadPoints.split()
            price = read_from_xml_node(xmlNode, "Price", do_not_warn=True)
            if price is not None:
                self.price.value = int(price)

            repairCoef = read_from_xml_node(xmlNode, "RepairCoef", do_not_warn=True)
            if repairCoef is not None:
                self.repairCoef.value = float(repairCoef)

            self.canBeUsedInAutogenerating.value = parse_str_to_bool(self.canBeUsedInAutogenerating.default_value,
                                                                     read_from_xml_node(xmlNode,
                                                                                        "CanBeUsedInAutogenerating",
                                                                                        do_not_warn=True))
            # custom implementation. Originally called from PrototypeManager -> RefreshFromXml
            VehiclePartPrototypeInfo.RefreshFromXml(self, xmlFile, xmlNode)
            # custom implementation ends
            return STATUS_SUCCESS

    def RefreshFromXml(self, xmlFile, xmlNode):
        # custom logic
        # original called from VehiclePartPrototypeInfo::_InitModelMeshes
        # PhysicBodyPrototypeInfo.RefreshFromXml(self, xmlFile, xmlNode)

        group_health_node = child_from_xml_node(xmlNode, "GroupsHealth", do_not_warn=True)
        # Cabin, Basket, Chassis will use model file as source of truth
        # all other classes will look in model only if GroupHealth specified in xml
        if self.lookupModelFile or group_health_node is not None:
            # if not self.lookupModelFile and group_health_node is not None:
            #     if str(group_health_node.keys()) == "['Main']":
            #         self.groupHealth.value["Main"] = \
            #             {"value": None,
            #              "id": None,
            #              "variants": None}
            model_path = self.theServer.theAnimatedModelsServer.GetItemByName(self.engineModelName.value).file_name
            model_group_health = parse_model_group_health(model_path)
            for group_health in model_group_health:
                if group_health_node is not None:
                    read_value = read_from_xml_node(group_health_node, group_health, do_not_warn=True)
                else:
                    read_value = None
                if read_value is None:
                    model_group_health[group_health]["health"] = 0.0
                    self.groupHealth.value[group_health] = model_group_health[group_health]
                else:
                    model_group_health[group_health]["health"] = float(read_value)
                    self.groupHealth.value[group_health] = model_group_health[group_health]

    def get_etree_prototype(self):
        result = PhysicBodyPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.loadPoints, lambda x: " ".join(map(str, x.value)))
        add_value_to_node(result, self.durabilityCoeffsForDamageTypes, lambda x: " ".join(map(str, x.value)))

        def prepare_groupHealth(groupHealth):
            groupHealthElement = etree.Element(groupHealth.name)
            for prop in groupHealth.value:
                groupHealthElement.set(prop, str(groupHealth.value[prop]["health"]))
            return groupHealthElement
        add_value_to_node_as_child(result, self.groupHealth, lambda x: prepare_groupHealth(x))
        return result


class ChassisPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.maxHealth = AnnotatedValue(1.0, "MaxHealth", group_type=GroupType.PRIMARY)
        self.maxFuel = AnnotatedValue(1.0, "MaxFuel", group_type=GroupType.PRIMARY)
        self.brakingSoundName = AnnotatedValue("", "BrakingSound", group_type=GroupType.SOUND)
        self.pneumoSoundName = AnnotatedValue("", "PneumoSound", group_type=GroupType.SOUND)
        self.gearShiftSoundName = AnnotatedValue("", "GearShiftSound", group_type=GroupType.SOUND)
        # custom logic
        self.lookupModelFile = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxHealth = read_from_xml_node(xmlNode, "MaxHealth", do_not_warn=True)
            if maxHealth is not None:
                self.maxHealth.value = float(maxHealth)

            maxFuel = read_from_xml_node(xmlNode, "MaxFuel", do_not_warn=True)
            if maxFuel is not None:
                self.maxFuel.value = float(maxFuel)

            self.brakingSoundName.value = read_from_xml_node(xmlNode, "BrakingSound")
            self.pneumoSoundName.value = read_from_xml_node(xmlNode, "PneumoSound")
            self.gearShiftSoundName.value = read_from_xml_node(xmlNode, "GearShiftSound")
            return STATUS_SUCCESS


class CabinPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.maxPower = AnnotatedValue(1.0, "MaxPower", group_type=GroupType.PRIMARY)
        self.maxTorque = AnnotatedValue(1.0, "MaxTorque", group_type=GroupType.PRIMARY)
        self.maxSpeed = AnnotatedValue(1.0 * 0.27777779, "MaxSpeed", group_type=GroupType.PRIMARY,
                                       saving_type=SavingType.SPECIFIC)
        self.fuelConsumption = AnnotatedValue(1.0, "FuelConsumption", group_type=GroupType.PRIMARY)
        self.gadgetSlots = AnnotatedValue([], "GadgetDescription", group_type=GroupType.PRIMARY,
                                          saving_type=SavingType.SPECIFIC)
        self.control = AnnotatedValue(50.0, "Control", group_type=GroupType.PRIMARY)
        self.engineHighSoundName = AnnotatedValue("", "EngineHighSound", group_type=GroupType.SOUND)
        self.engineLowSoundName = AnnotatedValue("", "EngineLowSound", group_type=GroupType.SOUND)
        # custom logic
        self.lookupModelFile = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxPower = read_from_xml_node(xmlNode, self.maxPower.name, do_not_warn=True)
            if maxPower is not None:
                self.maxPower.value = float(maxPower)

            maxTorque = read_from_xml_node(xmlNode, self.maxTorque.name, do_not_warn=True)
            if maxTorque is not None:
                self.maxTorque.value = float(maxTorque)

            maxSpeed = read_from_xml_node(xmlNode, self.maxSpeed.name, do_not_warn=True)
            if maxSpeed is not None:
                self.maxSpeed.value = float(maxSpeed)
                self.maxSpeed.value = self.maxSpeed.value * 0.27777779  # ~5/18 or 50/180

            fuelConsumption = read_from_xml_node(xmlNode, self.fuelConsumption.name, do_not_warn=True)
            if fuelConsumption is not None:
                self.fuelConsumption.value = float(fuelConsumption)

            self.engineHighSoundName.value = safe_check_and_set(self.engineHighSoundName.default_value,
                                                                xmlNode,
                                                                self.engineHighSoundName.name)
            self.engineLowSoundName.value = safe_check_and_set(self.engineLowSoundName.default_value,
                                                               xmlNode,
                                                               self.engineLowSoundName.name)

            control = read_from_xml_node(xmlNode, self.control.name, do_not_warn=True)
            if control is not None:
                self.control.value = float(control)
            if self.control.value < 0.0 or self.control.value > 100.0:
                self.control.value = 100.0

            gadgetDescriptions = child_from_xml_node(xmlNode, self.gadgetSlots.name, do_not_warn=True)
            if gadgetDescriptions is not None:
                check_mono_xml_node(gadgetDescriptions, "Slot")
                for gadget_node in gadgetDescriptions.iterchildren(tag="Slot"):
                    gadget = {"resourceType": read_from_xml_node(gadget_node, "ResourceType"),
                              "maxAmount": int(read_from_xml_node(gadget_node, "MaxAmount"))}
                    self.gadgetSlots.value.append(gadget)
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.maxSpeed, lambda x: str(x.value / 0.27777779))
        # save gadgetSlots

        def render_slot(annotatedValue):
            gadgetSlotsElement = etree.Element(annotatedValue.name)
            for slotItem in annotatedValue.value:
                slotElement = etree.Element("Slot")
                slotElement.set("ResourceType", slotItem["resourceType"])
                slotElement.set("MaxAmount", str(slotItem["maxAmount"]))
                gadgetSlotsElement.append(slotElement)
            return gadgetSlotsElement

        add_value_to_node_as_child(result, self.gadgetSlots, lambda x: render_slot(x))
        # save gadgetSlots end
        return result


class BasketPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.slots = AnnotatedValue([], "Slot", group_type=GroupType.PRIMARY,
                                    saving_type=SavingType.SPECIFIC)
        self.repositorySize = AnnotatedValue({"x": 10, "y": 10}, "RepositorySize",
                                             group_type=GroupType.PRIMARY,
                                             saving_type=SavingType.SPECIFIC)
        # custom logic
        self.lookupModelFile = True

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            repositoryDescriptions = child_from_xml_node(xmlNode, "RepositoryDescription")
            repositorySize = read_from_xml_node(repositoryDescriptions, self.repositorySize.name)
            repositorySize = repositorySize.split()
            self.repositorySize.value = {"x": repositorySize[0],
                                         "y": repositorySize[1]}
            if len(repositoryDescriptions.getchildren()) > 1:
                check_mono_xml_node(repositoryDescriptions, "Slot")
                for slot_node in repositoryDescriptions.iterchildren(tag="Slot"):
                    pos = read_from_xml_node(slot_node, "Pos").split()
                    pos = {"x": pos[0], "y": pos[1]}
                    slot = {"name": read_from_xml_node(slot_node, "Name"),
                            "pos": pos}
                    self.slots.value.append(slot)
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)
        # save RepositoryDescription
        # too complex to be transformed to lambda
        if (
            self.repositorySize.value != self.repositorySize.default_value
            or self.slots.value != self.slots.default_value
        ):
            repositoryDescription = etree.Element("RepositoryDescription")
            repositoryDescription.set(self.repositorySize.name,
                                      f'{self.repositorySize.value["x"]} {self.repositorySize.value["y"]}')
            for slotItem in self.slots.value:
                slotElement = etree.Element("Slot")
                slotElement.set("Name", slotItem["name"])
                slotElement.set("Pos", f'{slotItem["pos"]["x"]} {slotItem["pos"]["y"]}')
                repositoryDescription.append(slotElement)
            result.append(repositoryDescription)
        # save RepositoryDescription end
        return result


class GunPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.barrelModelName = ""
        self.withCharging = AnnotatedValue(True, "WithCharging", group_type=GroupType.PRIMARY)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)
        self.shellPrototypeId = -1
        self.damage = AnnotatedValue(1.0, "Damage", group_type=GroupType.PRIMARY)
        self.damageType = AnnotatedValue(0, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.firingRate = AnnotatedValue(1.0, "FiringRate", group_type=GroupType.PRIMARY)
        self.firingRange = AnnotatedValue(1.0, "FiringRange", group_type=GroupType.PRIMARY)
        self.lowStopAngle = 0.0
        self.highStopAngle = 0.0
        self.ignoreStopAnglesWhenFire = AnnotatedValue(False, "IgnoreStopAnglesWhenFire", group_type=GroupType.PRIMARY)
        self.decalName = AnnotatedValue("", "Decal", group_type=GroupType.PRIMARY)
        self.decalId = -1
        self.recoilForce = AnnotatedValue(0.0, "RecoilForce", group_type=GroupType.PRIMARY)
        self.turningSpeed = AnnotatedValue(DEFAULT_TURNING_SPEED * (pi / 180),  # convert to rads
                                           "TurningSpeed",
                                           group_type=GroupType.PRIMARY,
                                           saving_type=SavingType.SPECIFIC)
        self.chargeSize = AnnotatedValue(20, "ChargeSize", group_type=GroupType.PRIMARY)
        self.reChargingTime = AnnotatedValue(1.0, "RechargingTime", group_type=GroupType.PRIMARY)
        self.reChargingTimePerShell = AnnotatedValue(0.0, "ReChargingTimePerShell", group_type=GroupType.PRIMARY)
        self.shellsPoolSize = AnnotatedValue(12, "ShellsPoolSize", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeId = -1
        self.firingType = AnnotatedValue(-1, "FiringType", group_type=GroupType.PRIMARY,  # default changed
                                         saving_type=SavingType.SPECIFIC)
        self.fireLpMatrices = []
        self.explosionTypeName = AnnotatedValue("BIG", "ExplosionType", group_type=GroupType.PRIMARY)
        self.shellPrototypeName = AnnotatedValue("", "BulletPrototype", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.PRIMARY)

        self.engineModelName = AnnotatedValue("", "ModelFile", group_type=GroupType.VISUAL,
                                              saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.shellPrototypeName.value = safe_check_and_set(self.shellPrototypeName.default_value,
                                                               xmlNode, self.shellPrototypeName.name)
            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value,
                                                                   xmlNode, self.blastWavePrototypeName.name)
            damage = read_from_xml_node(xmlNode, self.damage.name, do_not_warn=True)
            if damage is not None:
                self.damage.value = float(damage)

            firingRate = read_from_xml_node(xmlNode, self.firingRate.name, do_not_warn=True)
            if firingRate is not None:
                self.firingRate.value = float(firingRate)

            firingRange = read_from_xml_node(xmlNode, self.firingRange.name, do_not_warn=True)
            if firingRange is not None:
                self.firingRange.value = float(firingRange)

            self.explosionTypeName.value = safe_check_and_set(self.explosionTypeName.default_value,
                                                              xmlNode, self.explosionTypeName.name)

            recoilForce = read_from_xml_node(xmlNode, self.recoilForce.name, do_not_warn=True)
            if recoilForce is not None:
                self.recoilForce.value = float(recoilForce)

            self.decalName.value = safe_check_and_set(self.decalName.default_value, xmlNode, self.decalName.name)
            self.decalId = f"Placeholder for {self.decalName.value}!"  # DynamicScene.AddDecalName(decalName)

            firingType = read_from_xml_node(xmlNode, self.firingType.name)
            self.firingType.value = GunPrototypeInfo.Str2FiringType(firingType)
            if self.firingType.value is None:
                logger.warning(f"Unknown firing type: {self.firingType.value}!")

            damageTypeName = read_from_xml_node(xmlNode, self.damageType.name, do_not_warn=True)
            if damageTypeName is not None:
                self.damageType.value = GunPrototypeInfo.Str2DamageType(damageTypeName)
            if self.damageType.value is None:
                logger.warning(f"Unknown damage type: {self.damageType.value}")

            self.withCharging.value = parse_str_to_bool(self.withCharging.default_value,
                                                        read_from_xml_node(xmlNode,
                                                                           self.withCharging.name,
                                                                           do_not_warn=True))

            chargeSize = read_from_xml_node(xmlNode, self.chargeSize.name, do_not_warn=True)
            if chargeSize is not None:
                chargeSize = int(chargeSize)
                if chargeSize >= 0:  # ??? whaaat, why should it ever be less than 0?
                    self.chargeSize.value = chargeSize

            reChargingTime = read_from_xml_node(xmlNode, self.reChargingTime.name, do_not_warn=True)
            if reChargingTime is not None:
                self.reChargingTime.value = float(reChargingTime)

            reChargingTimePerShell = read_from_xml_node(xmlNode, self.reChargingTimePerShell.name, do_not_warn=True)
            if reChargingTimePerShell is not None:
                self.reChargingTimePerShell.value = float(reChargingTimePerShell)

            shellsPoolSize = read_from_xml_node(xmlNode, self.shellsPoolSize.name, do_not_warn=True)
            if shellsPoolSize is not None:
                shellsPoolSize = int(shellsPoolSize)
                if shellsPoolSize > 0:
                    self.shellsPoolSize.value = shellsPoolSize
                else:
                    self.withShellsPoolLimit.default_value = False
                    self.withShellsPoolLimit.value = False

            self.withShellsPoolLimit.value = parse_str_to_bool(self.withShellsPoolLimit.default_value,
                                                               read_from_xml_node(xmlNode,
                                                                                  self.withShellsPoolLimit.name,
                                                                                  do_not_warn=True))

            turningSpeed = read_from_xml_node(xmlNode, self.turningSpeed.name, do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed.value = float(turningSpeed)
                # next row was moved under if to avoid double convertation of default. Default also was changed.
                self.turningSpeed.value *= pi / 180  # convert to rads
            # initially in engineModelName we have gun carriage. Here we add Gun suffix to take related model.
            self.engineModelName.value += "Gun"
            self.ignoreStopAnglesWhenFire.value = parse_str_to_bool(
                self.ignoreStopAnglesWhenFire.default_value, read_from_xml_node(xmlNode,
                                                                                self.ignoreStopAnglesWhenFire.name,
                                                                                do_not_warn=True))
            return STATUS_SUCCESS

    def Str2FiringType(firing_type_name: str):
        return FiringTypesStruct.get(firing_type_name)

    def FiringType2Str(firing_type_value: int):
        return list(FiringTypesStruct.keys())[list(FiringTypesStruct.values()).index(firing_type_value)]

    def Str2DamageType(damage_type_name: str):
        return DamageTypeStruct.get(damage_type_name)

    def DamageType2Str(damage_type_value: int):
        return list(DamageTypeStruct.keys())[list(DamageTypeStruct.values()).index(damage_type_value)]

    def PostLoad(self, prototype_manager):
        self.explosionType = "DUMMY_EXPLOSION_TYPE_NOT_IMPLEMENTED_GET_EXPLOSION_TYPE"
        # self.explosionType = prototype_manager.theServer.theDynamicScene.GetExplosionType(self.explosionTypeName)
        self.shellPrototypeId = prototype_manager.GetPrototypeId(self.shellPrototypeName.value)
        if self.shellPrototypeId == -1:  # ??? there also exist check if sheelPrototypeName is not empty. A valid case?
            logger.error(f"Shell prototype {self.shellPrototypeId} is invalid for {self.prototypeName.value}")
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)
        if self.blastWavePrototypeId == -1:
            logger.error(
                f"Unknown blastwave prototype {self.blastWavePrototypeName.value} for {self.prototypeName.value}")

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.engineModelName, lambda x: x.value.strip("Gun"))
        add_value_to_node(result, self.turningSpeed, lambda x: str(x.value / (pi / 180)))
        add_value_to_node(result, self.damageType, lambda x: GunPrototypeInfo.DamageType2Str(x.value))
        add_value_to_node(result, self.firingType, lambda x: GunPrototypeInfo.FiringType2Str(x.value))
        return result


class GadgetPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modifications = AnnotatedValue([], "Modifications", group_type=GroupType.PRIMARY,
                                            display_type=DisplayType.MODIFICATION_INFO,
                                            saving_type=SavingType.SPECIFIC)
        self.modelName = AnnotatedValue("", "ModelFile", group_type=GroupType.VISUAL)
        self.skinNum = AnnotatedValue(0, "SkinNum", group_type=GroupType.VISUAL, display_type=DisplayType.SKIN_NUM)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            modifications = read_from_xml_node(xmlNode, "Modifications").split(";")
            for modification_description in modifications:
                modification_info = self.ModificationInfo(modification_description, self)
                self.modifications.value.append(modification_info)
            self.modelName.value = safe_check_and_set(self.modelName.value, xmlNode, "ModelFile")
            self.skinNum.value = safe_check_and_set(self.skinNum.value, xmlNode, "SkinNum", "int")
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)
        # Modifications start

        def get_string_representation(modification):
            return self.ModificationInfo.get_string_representation(modification, self)

        add_value_to_node(result, self.modifications,
                          lambda x: ";".join(list(map(get_string_representation, x.value))))
        # Modifications end
        return result

    class ModificationInfo(object):  # special save and display needed
        # other ModificationInfo object can be passed to create copy
        def __init__(self, tokens: str, prot_info, other_mod=None):  # tokens=None
            if other_mod is None:
                self.applierInfo = {"applierType": 0,
                                    "targetResourceId": -1,
                                    "targetFiringType": 0}
                self.propertyName = ""
                self.value = ""  # is AIParam() necessary ???
                self.value_type = self.value_type_enum.DEFAULT.value

                self.modificationType = self.modification_type_enum.EMPTY.value
                token_value_part = 2

                token_parts = tokens.split()
                tokens_size = len(token_parts)
                if tokens_size == 4:
                    if token_parts[2] == "+=":
                        self.modificationType = self.modification_type_enum.PLUS_EQUAL.value
                        token_value_part = 3
                    else:
                        logger.error("Unexpected gadget modification token format. "
                                     "For 4-part token format third part should be '+='. "
                                     f"Given tokens: '{tokens}' for prototype: {prot_info.prototypeName.value}")
                elif tokens_size != 3:
                    logger.error("Expected tokens list with size equal to 3 or 4. "
                                 f"Given tokens: '{tokens}' for prototype: {prot_info.prototypeName.value}")

                token_resource_id = prot_info.theServer.theResourceManager.GetResourceId(token_parts[0])
                if token_parts[0] == "VEHICLE":
                    self.applierInfo["applierType"] = self.applier_type_enum.VEHICLE.value
                elif token_resource_id == -1:
                    self.applierInfo["applierType"] = self.applier_type_enum.GUN.value
                    self.applierInfo["targetFiringType"] = GunPrototypeInfo.Str2FiringType(token_parts[0])
                    if self.applierInfo["targetFiringType"] is None:
                        logger.warning(f"Unknown firing type '{token_parts[0]}' "
                                       f"for modification token of prototype: {prot_info.prototypeName.value}")
                else:
                    self.applierInfo["applierType"] = self.applier_type_enum.VEHICLE_PART.value
                    self.applierInfo["targetResourceId"] = token_resource_id
                self.propertyName = token_parts[1]
                if self.modificationType != self.modification_type_enum.EMPTY.value:
                    if self.modificationType == self.modification_type_enum.PLUS_EQUAL.value:
                        self.value = token_parts[token_value_part]
                        self.value_type = self.value_type_enum.ABSOLUTE.value
                    else:
                        logger.error(f"Unexpected modificationType for ModificationInfo '{tokens}'' "
                                     f"of {prot_info.prototypeName.value}")
                else:
                    value = float(token_parts[token_value_part]) * 0.01
                    self.value = value
                    self.value_type = self.value_type_enum.PERCENT.value

            # never used? Can be ignored for saving
            elif other_mod is not None:
                self.applierInfo["applierType"] = other_mod.applierInfo["applierType"]
                self.applierInfo["targetResourceId"] = other_mod.applierInfo["targetResourceId"]
                self.applierInfo["targetFiringType"] = other_mod.applierInfo["targetFiringType"]
                self.propertyName = other_mod.propertyName
                # self.NumFromName = int(other_mod.modificationType)
                self.value = other_mod.value  # ??? some AIParam magic in here

        def get_string_representation(self, prot_info):
            target = ""
            if self.applierInfo["targetResourceId"] != -1:
                target = prot_info.theServer.theResourceManager.GetResourceName(self.applierInfo["targetResourceId"])
            else:
                target = GunPrototypeInfo.FiringType2Str(self.applierInfo["targetFiringType"])
            sign = "+= " if self.modificationType == self.modification_type_enum.PLUS_EQUAL.value else ""
            value = self.value if self.value_type == self.value_type_enum.ABSOLUTE.value else int(self.value / 0.01)

            return f'{target} {self.propertyName} {sign}{value}'

        class applier_type_enum(Enum):
            VEHICLE = 0
            VEHICLE_PART = 1
            GUN = 2

        class modification_type_enum(Enum):
            EMPTY = 0,
            PLUS_EQUAL = 1

        class value_type_enum(Enum):
            DEFAULT = 0,
            PERCENT = 4,
            ABSOLUTE = 5


class WanderersManagerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class WanderersGeneratorPrototypeInfo(PrototypeInfo):  # special save and display needed
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.vehicleDescriptions = AnnotatedValue([], "VehicleDescription", group_type=GroupType.PRIMARY,
                                                  display_type=DisplayType.MODIFICATION_INFO,
                                                  saving_type=SavingType.SPECIFIC)
        self.desiredCountLow = AnnotatedValue(-1, "DesiredCountLow", group_type=GroupType.PRIMARY,
                                              saving_type=SavingType.SPECIFIC)
        self.desiredCountHigh = AnnotatedValue(-1, "DesiredCountHigh", group_type=GroupType.PRIMARY,
                                               saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            desiredCount = read_from_xml_node(xmlNode, "DesiredCount", do_not_warn=True)
            if desiredCount is not None:
                tokensDesiredCount = desiredCount.split("-")
                token_length = len(tokensDesiredCount)
                if token_length == 2:
                    self.desiredCountLow.value = int(tokensDesiredCount[0])
                    self.desiredCountHigh.value = int(tokensDesiredCount[1])
                elif token_length == 1:
                    self.desiredCountLow.value = int(tokensDesiredCount[0])
                    self.desiredCountHigh.value = self.desiredCountLow.value
                else:
                    logger.error(f"WanderersGenerator {self.prototypeName.value} attrib DesiredCount range "
                                 f"should contain one or two numbers but contains {len(tokensDesiredCount.value)}")
                if self.desiredCountLow.value > self.desiredCountHigh.value:
                    logger.error(f"WanderersGenerator {self.prototypeName.value} attrib DesiredCount range invalid: "
                                 f"{self.desiredCountLow.value}-{self.desiredCountHigh.value}, "
                                 "should be from lesser to higher number")
                if self.desiredCountHigh.value > 5:
                    logger.error(f"WanderersGenerator {self.prototypeName.value} attrib DesiredCount high value: "
                                 f"{self.desiredCountHigh.value} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")
            vehicles = child_from_xml_node(xmlNode, "Vehicles")
            check_mono_xml_node(vehicles, "Vehicle")
            for vehicle_node in vehicles.iterchildren("Vehicle"):
                vehicle_description = self.VehicleDescription()
                vehicle_description.LoadFromXML(xmlFile, vehicle_node)
                self.vehicleDescriptions.value.append(vehicle_description)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.vehicleDescriptions:
            for vehicle_description in self.vehicleDescriptions.value:
                vehicle_description.PostLoad(prototype_manager)

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)

        # DesiredCount start
        # Property name different from AnnotatedValue.name
        desired_count = 0
        if self.desiredCountLow.value == self.desiredCountHigh.value:
            desired_count = str(self.desiredCountLow.value)
        else:
            desired_count = f'{self.desiredCountLow.value}-{self.desiredCountHigh.value}'
        result.set("DesiredCount", desired_count)
        # DesiredCount end

        # VehicleDescription start

        def prepare_vehicles(vehicles_array):
            vehiclesTree = etree.Element("Vehicles")
            for vehicle in vehicles_array:
                vehiclesTree.append(self.VehicleDescription.get_etree_prototype(vehicle))
            return vehiclesTree

        add_value_to_node_as_child(result, self.vehicleDescriptions, lambda x: prepare_vehicles(x.value))
        # VehicleDescription end
        return result

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

        def get_etree_prototype(self):
            vehicleTree = etree.Element("Vehicle")
            vehicleTree.set("Prototype", self.prototype)
            children = [
                self.get_etree_node_if_not_default("Cabin", self.cabin),
                self.get_etree_node_if_not_default("Basket", self.basket),
                self.get_etree_node_if_not_default("CabinSmallGun", self.cabinSmallGun),
                self.get_etree_node_if_not_default("CabinBigGun", self.cabinBigGun),
                self.get_etree_node_if_not_default("CabinSpecialWeapon", self.cabinSpecialWeapon),
                self.get_etree_node_if_not_default("BasketSmallGun0", self.basketSmallGun0),
                self.get_etree_node_if_not_default("BasketSmallGun1", self.basketSmallGun1),
                self.get_etree_node_if_not_default("BasketBigGun0", self.basketBigGun0),
                self.get_etree_node_if_not_default("BasketBigGun1", self.basketBigGun1),
                self.get_etree_node_if_not_default("BasketSideGun", self.basketSideGun)
            ]
            for child in children:
                if child is not None:
                    vehicleTree.append(child)
            return vehicleTree

        def get_etree_node_if_not_default(self, nodeName, childProp):
            if childProp.present and childProp.prototypeNames == []:
                return None
            else:
                vehicleTree = etree.Element(nodeName)
                if not childProp.present:
                    vehicleTree.set("Present", str(childProp.present))
                if childProp.prototypeNames != []:
                    vehicleTree.set("Prototypes", " ".join(childProp.prototypeNames))
                return vehicleTree

    class VehiclePartDescription(object):
        def __init__(self):
            self.present = True
            self.prototypeNames = []
            self.prototypeIds = []

        def LoadFromXML(self, xmlFile, xmlNode):
            self.present = parse_str_to_bool(self.present, read_from_xml_node(xmlNode, "Present", do_not_warn=True))
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
        self.affixDescriptions = AnnotatedValue([], "Affix", group_type=GroupType.PRIMARY,
                                                display_type=DisplayType.AFFIX_LIST,
                                                saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            affix_nodes = child_from_xml_node(xmlNode, "Affix")
            for affix in affix_nodes:
                self.affixDescriptions.value.append(read_from_xml_node(affix, "AffixName"))
            return STATUS_SUCCESS

    def GenerateAffixesForObj(self, obj, desiredNumAffixed):
        pass

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)

        # affixDescriptions start

        def prepare_affixe(affix_array):
            result = []
            for affixName in affix_array:
                affix = etree.Element("Affix")
                affix.set("AffixName", affixName)
                result.append(affix)
            return result

        add_value_to_node_as_child(result, self.affixDescriptions, lambda x: prepare_affixe(x.value))
        # affixDescriptions end
        return result

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
        self.intersectionRadius = AnnotatedValue(0.0, "IntersectionRadius", group_type=GroupType.PRIMARY)
        self.lookRadius = AnnotatedValue(0.0, "LookRadius", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            intersectionRadius = read_from_xml_node(xmlNode, "IntersectionRadius", do_not_warn=True)
            if intersectionRadius is not None:
                self.intersectionRadius.value = intersectionRadius
            lookRadius = read_from_xml_node(xmlNode, "LookRadius", do_not_warn=True)
            if lookRadius is not None:
                self.lookRadius.value = lookRadius
            return STATUS_SUCCESS


class SimplePhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)
        self.collisionInfos = []
        self.collisionTrimeshAllowed = AnnotatedValue(False, "CollisionTrimeshAllowed",
                                                      group_type=GroupType.SECONDARY)
        self.geomType = 0
        self.engineModelName = AnnotatedValue("", "ModelFile", group_type=GroupType.VISUAL)
        self.size = AnnotatedValue(deepcopy(ZERO_VECTOR), "Size", group_type=GroupType.SECONDARY,
                                   saving_type=SavingType.SPECIFIC)
        self.radius = AnnotatedValue(1.0, "Radius", group_type=GroupType.SECONDARY)
        self.massValue = AnnotatedValue(1.0, "Mass", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            mass = read_from_xml_node(xmlNode, "Mass", do_not_warn=True)
            if mass is not None:
                self.massValue.value = float(mass)
            # ??? maybe should fallback to "" instead None
            self.engineModelName.value = read_from_xml_node(xmlNode, "ModelFile", do_not_warn=True)
            self.collisionTrimeshAllowed.value = parse_str_to_bool(self.collisionTrimeshAllowed.default_value,
                                                                   read_from_xml_node(xmlNode,
                                                                                      "CollisionTrimeshAllowed",
                                                                                      do_not_warn=True))
            # custom implementation. Originally called from PrototypeManager -> RefreshFromXml
            self.RefreshFromXml(xmlFile, xmlNode)
            # custom implementation ends
            return STATUS_SUCCESS

    def SetGeomType(self, geom_type):
        self.geomType = GEOM_TYPE[geom_type]
        if self.geomType == 6:
            return
        collision_info = CollisionInfo()
        collision_info.Init()
        if self.geomType == 1:
            collision_info.geomType = 1
            collision_info.size["x"] = self.size.value["x"]
            collision_info.size["y"] = self.size.value["y"]
            collision_info.size["z"] = self.size.value["z"]
        elif self.geomType == 2:
            collision_info.geomType = 2
            collision_info.radius = self.radius.value
        elif self.geomType == 5:
            logger.warning(f"Obsolete GeomType: TriMesh! in {self.prototypeName.value}")
        self.collisionInfos.append(collision_info)

    def get_etree_prototype(self):
        result = PhysicObjPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.size, lambda x: vector_to_string(x.value))
        return result

    def RefreshFromXml(self, xmlFile, xmlNode):
        # anim_model_server = self.theServer.theAnimatedModelsServer
        # model_obj = anim_model_server.GetItemByName(self.engineModelName.value)
        # GetCollisionInfoByServerHandle(model_obj, self.collisionInfos, self.collisionTrimeshAllowed)
        # speed = parse_str_to_vector(read_from_xml_node(xmlNode, "Size", do_not_warn=True))
        # sizeFromDataServer = anim_model_server.GetBoundsSizes(self.engineModelName.value)
        # self.radius.value = sizeFromDataServer.y * 0.5
        size = read_from_xml_node(xmlNode, "Size", do_not_warn=True)
        if size is not None:
            self.size.value = parse_str_to_vector(size)
        self.radius.value = safe_check_and_set(self.radius.default_value, xmlNode, "Radius", "float")
        # self.SetGeomType(self.geom_type)


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


class ComplexPhysicObjPrototypeInfo(PhysicObjPrototypeInfo):
    def __init__(self, server):
        PhysicObjPrototypeInfo.__init__(self, server)
        self.partPrototypeIds = []
        self.partPrototypeNames = AnnotatedValue([], "Parts", group_type=GroupType.PRIMARY,
                                                 saving_type=SavingType.SPECIFIC)
        self.massSize = AnnotatedValue(deepcopy(ONE_VECTOR), "MassSize", group_type=GroupType.SECONDARY,
                                       saving_type=SavingType.SPECIFIC)
        self.massTranslation = AnnotatedValue(deepcopy(ZERO_VECTOR), "MassTranslation", group_type=GroupType.SECONDARY,
                                              saving_type=SavingType.SPECIFIC)
        self.partDescription = []
        # custom init for partPrototypeDescription
        self.partPrototypeDescriptions = AnnotatedValue([], "PartsDescription", group_type=GroupType.PRIMARY,
                                                        saving_type=SavingType.SPECIFIC)
        self.allPartNames = []
        self.massShape = AnnotatedValue(0, "MassShape", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            main_part_description_node = child_from_xml_node(xmlNode, "MainPartDescription", do_not_warn=True)
            if main_part_description_node is not None:
                partPrototypeDescriptions = self.ComplexPhysicObjPartDescription()
                partPrototypeDescriptions.LoadFromXML(xmlFile, main_part_description_node, self.theServer)
                self.partPrototypeDescriptions.value = partPrototypeDescriptions
            else:
                if self.parent.partPrototypeDescriptions.value is None:
                    logger.warning(f"Parts description is missing for prototype {self.prototypeName.value}")
            parts_node = child_from_xml_node(xmlNode, "Parts")
            if parts_node is not None:
                check_mono_xml_node(parts_node, "Part")
                for part_node in parts_node.iterchildren(tag="Part"):
                    prototypeId = read_from_xml_node(part_node, "id")
                    prototypeName = read_from_xml_node(part_node, "Prototype")
                    protName = {"name": prototypeName,
                                "id": prototypeId}
                    self.partPrototypeNames.value.append(protName)
            massSize = read_from_xml_node(xmlNode, "MassSize", do_not_warn=True)
            if massSize is not None:
                self.massSize.value = parse_str_to_vector(massSize)
            massTranslation = read_from_xml_node(xmlNode, "MassTranslation", do_not_warn=True)
            if massTranslation is not None:
                self.massTranslation.value = parse_str_to_vector(massTranslation)
            self.massShape.value = safe_check_and_set(self.massShape.value, xmlNode, "MassShape", "int")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        for prot_name in self.partPrototypeNames.value:
            self.partPrototypeIds.append(prototype_manager.GetPrototypeId(prot_name["name"]))
        # unused for the moment
        self.allPartNames = [part.name for part in self.partDescription]

    def get_etree_prototype(self):
        result = PhysicObjPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.massSize, lambda x: vector_to_string(x.value))
        add_value_to_node(result, self.massTranslation, lambda x: vector_to_string(x.value))
        # start partPrototypeDescriptions
        propName = "MainPartDescription"
        add_value_to_node_as_child(result, self.partPrototypeDescriptions,
                                   lambda x: self.ComplexPhysicObjPartDescription.get_etree_prototype(x.value,
                                                                                                      propName,
                                                                                                      self.theServer))
        # Ends partPrototypeDescriptions
        # Start partPrototypeNames

        def get_parts_elem(partPrototypeNames):
            partsContainerElement = etree.Element(partPrototypeNames.name)
            for part in partPrototypeNames.value:
                partElement = etree.Element("Part")
                partElement.set("id", part["id"])
                partElement.set("Prototype", part["name"])
                partsContainerElement.append(partElement)
            return partsContainerElement

        add_value_to_node_as_child(result, self.partPrototypeNames, lambda x: get_parts_elem(x))
        # Ends partPrototypeNames
        return result

    class ComplexPhysicObjPartDescription(Object):
        def __init__(self, prototype_info_object=None):
            Object.__init__(self, prototype_info_object)
            self.partResourceId = -1
            self.lpNames = []
            self.child_descriptions = []  # ??? temporary placeholder for original logic
            self.name = ""

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
                    part_description = ComplexPhysicObjPrototypeInfo.ComplexPhysicObjPartDescription()
                    part_description.LoadFromXML(xmlFile, description_node, server)
                    self.child_descriptions.append(part_description)  # ??? temporary placeholder for original logic

        def get_etree_prototype(self, elementName, server):
            partDescriptionElement = etree.Element(elementName)
            partDescriptionElement.set("id", self.name)
            partDescriptionElement.set("partResourceType",
                                       server.theResourceManager.GetResourceName(self.partResourceId))
            if self.lpNames != []:
                partDescriptionElement.set("lpName", ",".join(self.lpNames))
            for child in self.child_descriptions:
                partDescriptionElement.append(child.get_etree_prototype("PartDescription", server))
            return partDescriptionElement


class StaticAutoGunPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.maxHealth = AnnotatedValue(1.0, "MaxHealth", group_type=GroupType.SECONDARY)
        self.destroyedModelName = AnnotatedValue("", "DestroyedModel", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            if self.parentPrototypeName.value is None:
                self.maxHealth.value = safe_check_and_set(self.maxHealth.default_value, xmlNode,
                                                          self.maxHealth.name, "float")
                self.destroyedModelName.value = safe_check_and_set(self.destroyedModelName.default_value, xmlNode,
                                                                   self.destroyedModelName.name)
            return STATUS_SUCCESS


class VehiclePrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.diffRatio = AnnotatedValue(1.0, "DiffRatio", group_type=GroupType.SECONDARY)
        self.maxEngineRpm = AnnotatedValue(1.0, "MaxEngineRpm", group_type=GroupType.SECONDARY)
        self.lowGearShiftLimit = AnnotatedValue(1.0, "LowGearShiftLimit", group_type=GroupType.SECONDARY)
        self.highGearShiftLimit = AnnotatedValue(1.0, "HighGearShiftLimit", group_type=GroupType.SECONDARY)
        self.selfbrakingCoeff = AnnotatedValue(0.0060000001, "SelfBrakingCoeff", group_type=GroupType.SECONDARY)
        self.steeringSpeed = AnnotatedValue(1.0, "SteeringSpeed", group_type=GroupType.SECONDARY)
        self.takingRadius = AnnotatedValue(1.0, "TakingRadius", group_type=GroupType.SECONDARY)
        self.priority = AnnotatedValue(-56, "Priority", group_type=GroupType.SECONDARY)
        self.hornSoundName = AnnotatedValue("", "HornSound", group_type=GroupType.SECONDARY)
        self.cameraHeight = AnnotatedValue(-1.0, "CameraHeight", group_type=GroupType.SECONDARY)
        self.cameraMaxDist = AnnotatedValue(25.0, "CameraMaxDist", group_type=GroupType.SECONDARY)
        self.destroyEffectNames = AnnotatedValue(["ET_PS_VEH_EXP" for i in range(4)], "DestroyEffectNames",
                                                 group_type=GroupType.SECONDARY, saving_type=SavingType.SPECIFIC)
        self.wheelInfos = AnnotatedValue([], "Wheel", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWave", group_type=GroupType.SECONDARY)
        self.additionalWheelsHover = AnnotatedValue(0.0, "AdditionalWheelsHover", group_type=GroupType.SECONDARY)
        self.driftCoeff = AnnotatedValue(1.0, "DriftCoeff", group_type=GroupType.SECONDARY)
        self.pressingForce = AnnotatedValue(1.0, "PressingForce", group_type=GroupType.SECONDARY)
        self.healthRegeneration = AnnotatedValue(0.0, "HealthRegeneration", group_type=GroupType.SECONDARY)
        self.durabilityRegeneration = AnnotatedValue(0.0, "DurabilityRegeneration", group_type=GroupType.SECONDARY)
        self.visibleInEncyclopedia = AnnotatedValue(False, "VisibleInEncyclopedia", group_type=GroupType.SECONDARY)
        self.decisionMatrixNum = -1
        self.blastWavePrototypeId = -1
        self.decisionMatrixName = AnnotatedValue("", "DecisionMatrix", group_type=GroupType.SECONDARY)  # new logic

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.diffRatio.value = safe_check_and_set(self.diffRatio.default_value, xmlNode,
                                                      self.diffRatio.name, "float")
            self.maxEngineRpm.value = safe_check_and_set(self.maxEngineRpm.default_value, xmlNode,
                                                         self.maxEngineRpm.name, "float")
            self.lowGearShiftLimit.value = safe_check_and_set(self.lowGearShiftLimit.default_value, xmlNode,
                                                              self.lowGearShiftLimit.name, "float")
            self.highGearShiftLimit.value = safe_check_and_set(self.highGearShiftLimit.default_value, xmlNode,
                                                               self.highGearShiftLimit.name, "float")
            self.selfbrakingCoeff.value = safe_check_and_set(self.selfbrakingCoeff.default_value, xmlNode,
                                                             self.selfbrakingCoeff.name, "float")
            self.steeringSpeed.value = safe_check_and_set(self.steeringSpeed.default_value, xmlNode,
                                                          self.steeringSpeed.name, "float")
            decisionMatrixName = read_from_xml_node(xmlNode, self.decisionMatrixName.name, do_not_warn=True)
            self.decisionMatrixName.value = decisionMatrixName  # new logic
            # theAIManager.LoadMatrix(decisionMatrixName)
            # self.decisionMatrixNum = theAIManager.GetMatrixNum(decisionMatrixName)
            self.decisionMatrixNum = f"DummyMatrixNum_{decisionMatrixName}"  # ??? replace when AIManager is implemented
            self.takingRadius.value = safe_check_and_set(self.takingRadius.default_value, xmlNode,
                                                         self.takingRadius.name, "float")
            self.priority.value = safe_check_and_set(self.priority.default_value, xmlNode,
                                                     self.priority.name, "int")
            self.hornSoundName.value = safe_check_and_set(self.hornSoundName.default_value, xmlNode,
                                                          self.hornSoundName.name)
            self.cameraHeight.value = safe_check_and_set(self.cameraHeight.default_value, xmlNode,
                                                         self.cameraHeight.name, "float")
            self.cameraMaxDist.value = safe_check_and_set(self.cameraMaxDist.default_value, xmlNode,
                                                          self.cameraMaxDist.name, "float")
            destroyEffectNames = [read_from_xml_node(xmlNode, name, do_not_warn=True) for name in DESTROY_EFFECT_NAMES]
            for i in range(len(self.destroyEffectNames.value)):
                if destroyEffectNames[i] is not None:
                    self.destroyEffectNames.value[i] = destroyEffectNames[i]
            wheels_info = child_from_xml_node(xmlNode, "Wheels", do_not_warn=True)
            if self.parentPrototypeName.value is not None and wheels_info is not None:
                logger.error(f"Wheels info is present for inherited vehicle {self.prototypeName.value}")
            elif self.parentPrototypeName.value is None and wheels_info is None:
                logger.error(f"Wheels info is not present for parent vehicle {self.prototypeName.value}")
            elif self.parentPrototypeName.value is None and wheels_info is not None:
                check_mono_xml_node(wheels_info, self.wheelInfos.name)
                for wheel_node in wheels_info.iterchildren(tag="Wheel"):
                    steering = read_from_xml_node(wheel_node, "steering", do_not_warn=True)
                    wheel_prototype_name = read_from_xml_node(wheel_node, "Prototype")
                    wheel = self.WheelInfo(wheel_prototype_name, steering)
                    self.wheelInfos.value.append(wheel)
            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value, xmlNode,
                                                                   self.blastWavePrototypeName.name)
            self.additionalWheelsHover.value = safe_check_and_set(self.additionalWheelsHover.default_value, xmlNode,
                                                                  self.additionalWheelsHover.name, "float")
            self.driftCoeff.value = safe_check_and_set(self.driftCoeff.default_value, xmlNode,
                                                       self.driftCoeff.name, "float")
            self.pressingForce.value = safe_check_and_set(self.pressingForce.default_value, xmlNode,
                                                          self.pressingForce.name, "float")
            self.healthRegeneration.value = safe_check_and_set(self.healthRegeneration.default_value, xmlNode,
                                                               self.healthRegeneration.name, "float")
            self.durabilityRegeneration.value = safe_check_and_set(self.durabilityRegeneration.default_value, xmlNode,
                                                                   self.durabilityRegeneration.name, "float")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for wheel_info in self.wheelInfos.value:
            wheel_info.wheelPrototypeId = prototype_manager.GetPrototypeId(wheel_info.wheelPrototypeName)
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    def get_etree_prototype(self):
        result = ComplexPhysicObjPrototypeInfo.get_etree_prototype(self)
        # destroyEffectNames start
        for i in range(len(DESTROY_EFFECT_NAMES)):
            if self.destroyEffectNames.value[i] != self.destroyEffectNames.default_value[i]:
                result.set(DESTROY_EFFECT_NAMES[i], self.destroyEffectNames.value[i])
        # destroyEffectNames ends
        # wheelInfos start

        def add_wheel_info(wheelInfos):
            wheelElement = etree.Element(wheelInfos.name)
            for wheelInfo in wheelInfos.value:
                wheelElement.append(self.WheelInfo.get_etree_prototype(wheelInfo))
            return wheelElement

        add_value_to_node_as_child(result, self.wheelInfos, lambda x: add_wheel_info(x))
        # wheelInfos ends
        return result

    class WheelInfo(object):
        def __init__(self, wheelPrototypeName, steering):
            self.steering = steering
            self.wheelPrototypeName = wheelPrototypeName
            self.wheelPrototypeId = -1

        def PostLoad(self, prototype_manager):
            self.wheelPrototypeId = prototype_manager.GetPrototypeId(self.wheelPrototypeName)

        def get_etree_prototype(self):
            result = etree.Element("Wheel")
            result.set("Prototype", self.wheelPrototypeName)
            if self.steering is not None:
                result.set("steering", self.steering)
            return result


class ArticulatedVehiclePrototypeInfo(VehiclePrototypeInfo):
    def __init__(self, server):
        VehiclePrototypeInfo.__init__(self, server)
        self.trailerPrototypeName = AnnotatedValue("", "TrailerPrototype", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehiclePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.trailerPrototypeName.value = safe_check_and_set(self.trailerPrototypeName.default_value, xmlNode,
                                                                 "TrailerPrototype")
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from

    def PostLoad(self, prototype_manager):
        VehiclePrototypeInfo.PostLoad(self, prototype_manager)
        self.trailerPrototypeId = prototype_manager.GetPrototypeId(self.trailerPrototypeName.value)


class DummyObjectPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.isUpdating.value = False
        self.isUpdating.default_value = False
        self.disablePhysics = AnnotatedValue(False, "DisablePhysics",
                                             group_type=GroupType.SECONDARY)
        self.disableGeometry = AnnotatedValue(False, "DisableGeometry",
                                              group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.disablePhysics.value = parse_str_to_bool(self.disablePhysics.default_value,
                                                          read_from_xml_node(xmlNode,
                                                                             self.disablePhysics.name,
                                                                             do_not_warn=True))
            self.disableGeometry.value = parse_str_to_bool(self.disableGeometry.default_value,
                                                           read_from_xml_node(xmlNode,
                                                                              self.disableGeometry.name,
                                                                              do_not_warn=True))
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
        self.suspensionRange = AnnotatedValue(0.5, "SuspensionRange", group_type=GroupType.SECONDARY)
        self.suspensionModelName = AnnotatedValue("", "SuspensionModelFile", group_type=GroupType.SECONDARY)
        self.suspensionCFM = AnnotatedValue(0.1, "SuspensionCFM", group_type=GroupType.SECONDARY)
        self.suspensionERP = AnnotatedValue(0.80000001, "SuspensionERP", group_type=GroupType.SECONDARY)
        self.mU = AnnotatedValue(1.0, "mU", group_type=GroupType.SECONDARY)
        self.typeName = AnnotatedValue("BIG", "EffectType", group_type=GroupType.SECONDARY)
        self.blowEffectName = AnnotatedValue("ET_PS_HARD_BLOW", "BlowEffect", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            suspensionRange = read_from_xml_node(xmlNode, self.suspensionRange.name, do_not_warn=True)
            if suspensionRange is not None:
                self.suspensionRange.value = float(suspensionRange)

            self.suspensionModelName.value = read_from_xml_node(xmlNode, self.suspensionModelName.name)

            suspensionCFM = read_from_xml_node(xmlNode, self.suspensionCFM.name, do_not_warn=True)
            if suspensionCFM is not None:
                self.suspensionCFM.value = float(suspensionCFM)

            suspensionERP = read_from_xml_node(xmlNode, self.suspensionERP.name, do_not_warn=True)
            if suspensionERP is not None:
                self.suspensionERP.value = float(suspensionERP)

            mU = read_from_xml_node(xmlNode, self.mU.name, do_not_warn=True)
            if mU is not None:
                self.mU.value = float(mU)

            self.typeName.value = safe_check_and_set(self.typeName.default_value, xmlNode, self.typeName.name)
            self.blowEffectName.value = safe_check_and_set(self.blowEffectName.default_value,
                                                           xmlNode,
                                                           self.blowEffectName.name)
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
        self.vehicleFiringRangeCoeff = AnnotatedValue(1.0, "FiringRangeCoeff", display_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            vehicleFiringRangeCoeff = read_from_xml_node(xmlNode, self.vehicleFiringRangeCoeff.name, do_not_warn=True)
            if vehicleFiringRangeCoeff is not None:
                self.vehicleFiringRangeCoeff.value = vehicleFiringRangeCoeff
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
        self.vehicleFiringRangeCoeff.value = 0.30000001
        self.vehicleFiringRangeCoeff.default_value = 0.30000001


class VehicleRoleMeatPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.vehicleFiringRangeCoeff.value = 0.30000001
        self.vehicleFiringRangeCoeff.default_value = 0.30000001


class VehicleRoleOppressorPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.oppressionShift = AnnotatedValue([], "OppressionShift", group_type=GroupType.PRIMARY,
                                              saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            oppressionShift = read_from_xml_node(xmlNode, self.oppressionShift.name)
            self.oppressionShift.value = oppressionShift.split()
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = VehicleRolePrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.oppressionShift, lambda x: " ".join(x.value))
        return result


class VehicleRolePendulumPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)
        self.oppressionShift = AnnotatedValue([], "OppressionShift", group_type=GroupType.PRIMARY,
                                              saving_type=SavingType.SPECIFIC)
        self.a = AnnotatedValue(0.0, "A", group_type=GroupType.PRIMARY)
        self.b = AnnotatedValue(0.0, "B", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = VehicleRolePrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            oppressionShift = read_from_xml_node(xmlNode, self.oppressionShift.name)
            self.oppressionShift.value = oppressionShift.split()
            a_param = read_from_xml_node(xmlNode, self.a.name)
            b_param = read_from_xml_node(xmlNode, self.b.name)
            if a_param is not None:
                self.a.value = float(a_param)
            if b_param is not None:
                self.b.value = float(b_param)
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = VehicleRolePrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.oppressionShift, lambda x: " ".join(x.value))
        return result


class VehicleRoleSniperPrototypeInfo(VehicleRolePrototypeInfo):
    def __init__(self, server):
        VehicleRolePrototypeInfo.__init__(self, server)


class TeamTacticWithRolesPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.rolePrototypeNames = AnnotatedValue([], "RolePrototypeNames", group_type=GroupType.PRIMARY,
                                                 display_type=DisplayType.AFFIX_LIST, saving_type=SavingType.SPECIFIC)
        self.rolePrototypeIds = []

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            check_mono_xml_node(xmlNode, "Role")
            for role in xmlNode.iterchildren(tag="Role"):
                self.rolePrototypeNames.value.append(read_from_xml_node(role, "Prototype"))
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.rolePrototypeNames.value:
            for role_name in self.rolePrototypeNames.value:
                role_prot_id = prototype_manager.GetPrototypeId(role_name)
                if role_prot_id == -1:  # ??? there also exist check if sheelPrototypeName is not empty. A valid case?
                    logger.error(f"Unknown role prototype: '{self.shellPrototypeId}' for prot: "
                                 f"'{self.prototypeName.value}'")
                else:
                    self.rolePrototypeIds.append(role_prot_id)

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)
        if self.rolePrototypeNames.value != self.rolePrototypeNames.default_value:
            for role in self.rolePrototypeNames.value:
                roleElement = etree.Element("Role")
                roleElement.set("Prototype", str(role))
                result.append(roleElement)
        return result


class NPCMotionControllerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)


class TeamPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.decisionMatrixNum = -1
        # placeholder for AIManager functionality ???
        self.decisionMatrixName = AnnotatedValue("", "DecisionMatrix", group_type=GroupType.PRIMARY)
        self.removeWhenChildrenDead = AnnotatedValue(True, "RemoveWhenChildrenDead", group_type=GroupType.SECONDARY)
        self.formationPrototypeName = AnnotatedValue(TEAM_DEFAULT_FORMATION_PROTOTYPE, "Prototype",
                                                     group_type=GroupType.PRIMARY, saving_type=SavingType.SPECIFIC)
        self.formationPrototypeId = -1
        self.overridesDistBetweenVehicles = AnnotatedValue(False, "OverridesDistBetweenVehicles",
                                                           group_type=GroupType.SECONDARY, read_only=True,
                                                           saving_type=SavingType.IGNORE)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)
        self.formationDistBetweenVehicles = AnnotatedValue(30.0, "DistBetweenVehicles", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.decisionMatrixName.value = read_from_xml_node(xmlNode, "DecisionMatrix")
            self.removeWhenChildrenDead.value = parse_str_to_bool(self.removeWhenChildrenDead.default_value,
                                                                  read_from_xml_node(xmlNode, "RemoveWhenChildrenDead",
                                                                                     do_not_warn=True))
            formation = child_from_xml_node(xmlNode, "Formation", do_not_warn=True)
            if formation is not None:
                self.formationPrototypeName.value = read_from_xml_node(formation, "Prototype")
                distBetweenVehicles = read_from_xml_node(formation, "DistBetweenVehicles", do_not_warn=True)
                if distBetweenVehicles is not None:
                    self.overridesDistBetweenVehicles.value = True
                    self.formationDistBetweenVehicles.value = float(distBetweenVehicles)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.formationPrototypeId = prototype_manager.GetPrototypeId(self.formationPrototypeName.value)

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)
        # formation starts
        if (
            self.formationPrototypeName.value != self.formationPrototypeName.default_value
            or self.formationDistBetweenVehicles.value != self.formationDistBetweenVehicles.default_value
        ):
            formation = etree.Element("Formation")
            formation.set("Prototype", str(self.formationPrototypeName.value))
            if(self.formationDistBetweenVehicles.value != self.formationDistBetweenVehicles.default_value):
                formation.set("DistBetweenVehicles", str(self.formationDistBetweenVehicles.value))
            result.append(formation)
        # formation ends
        return result


class CaravanTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.tradersGeneratorPrototypeName = AnnotatedValue("", "TradersVehiclesGeneratorName",
                                                            group_type=GroupType.PRIMARY)
        self.guardsGeneratorPrototypeName = AnnotatedValue("", "GuardVehiclesGeneratorName",
                                                           group_type=GroupType.PRIMARY)
        self.tradersGeneratorPrototypeId = -1
        self.guardsGeneratorPrototypeId = -1
        self.waresPrototypes = AnnotatedValue([], "WaresPrototypes", group_type=GroupType.PRIMARY,
                                              display_type=DisplayType.WARES_LIST, saving_type=SavingType.SPECIFIC)
        self.formationPrototypeName.value = TEAM_DEFAULT_FORMATION_PROTOTYPE
        self.formationPrototypeName.default_value = TEAM_DEFAULT_FORMATION_PROTOTYPE

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.tradersGeneratorPrototypeName.value = safe_check_and_set(self.tradersGeneratorPrototypeName.value,
                                                                          xmlNode, "TradersVehiclesGeneratorName")
            self.guardsGeneratorPrototypeName.value = safe_check_and_set(self.guardsGeneratorPrototypeName.value,
                                                                         xmlNode, "GuardVehiclesGeneratorName")
            waresPrototypes = read_from_xml_node(xmlNode, "WaresPrototypes", do_not_warn=True)
            if waresPrototypes is not None:
                self.waresPrototypes.value = waresPrototypes.split()
            if self.tradersGeneratorPrototypeName.value is not None:
                if self.waresPrototypes.value is None:
                    logger.error(f"No wares for caravan with traders: {self.prototypeName.value}")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        TeamPrototypeInfo.PostLoad(self, prototype_manager)
        self.tradersGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.tradersGeneratorPrototypeName.value)
        if self.tradersGeneratorPrototypeId == -1:
            logger.error(f"Unknown VehiclesGenerator '{self.tradersGeneratorPrototypeName.value}' "
                         f"for traders of CaravanTeam {self.prototypeName.value}")

        self.guardsGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.guardsGeneratorPrototypeName.value)
        if self.guardsGeneratorPrototypeId == -1:
            logger.error(f"Unknown VehiclesGenerator '{self.guardsGeneratorPrototypeName.value}' "
                         f"for guards of CaravanTeam {self.prototypeName.value}")

    def get_etree_prototype(self):
        result = TeamPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.waresPrototypes, lambda x: " ".join(x.value))
        return result


class VagabondTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.vehiclesGeneratorPrototype = AnnotatedValue("", "VehicleGeneratorPrototype",
                                                         group_type=GroupType.SECONDARY)
        self.waresPrototypes = AnnotatedValue([], "WaresPrototypes", group_type=GroupType.SECONDARY,
                                              saving_type=SavingType.SPECIFIC)
        self.removeWhenChildrenDead = AnnotatedValue(True, "RemoveWhenChildrenDead", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.vehiclesGeneratorPrototype.value = read_from_xml_node(xmlNode, self.vehiclesGeneratorPrototype.name)
            self.waresPrototypes.value = read_from_xml_node(xmlNode, self.waresPrototypes.name).split()
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = TeamPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.waresPrototypes, lambda x: " ".join(x.value))
        return result


class InfectionTeamPrototypeInfo(TeamPrototypeInfo):
    def __init__(self, server):
        TeamPrototypeInfo.__init__(self, server)
        self.items = AnnotatedValue([], "Vehicles", group_type=GroupType.PRIMARY,
                                    saving_type=SavingType.SPECIFIC)
        self.vehiclesGeneratorProtoName = AnnotatedValue("", "VehiclesGenerator", group_type=GroupType.PRIMARY)
        self.vehiclesGeneratorProtoId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = TeamPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.vehiclesGeneratorProtoName.value = safe_check_and_set(self.vehiclesGeneratorProtoName.default_value,
                                                                       xmlNode,
                                                                       self.vehiclesGeneratorProtoName.name)
            vehicles = child_from_xml_node(xmlNode, "Vehicles", do_not_warn=True)
            if vehicles is not None and len(vehicles.getchildren()) >= 1:
                check_mono_xml_node(vehicles, "Vehicle")
                for vehicle in vehicles.iterchildren(tag="Vehicle"):
                    item = {"protoName": read_from_xml_node(vehicle, "PrototypeName"),
                            "count": int(read_from_xml_node(vehicle, "Count"))}
                    self.items.value.append(item)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        TeamPrototypeInfo.PostLoad(self, prototype_manager)
        self.vehiclesGeneratorProtoId = prototype_manager.GetPrototypeId(self.vehiclesGeneratorProtoName.value)
        if self.vehiclesGeneratorProtoId == -1:
            if not self.items.value:
                if self.vehiclesGeneratorProtoName.value:
                    logger.error(f"Unknown '{self.vehiclesGeneratorProtoName.value}' VehiclesGenerator "
                                 f"for infection team '{self.prototypeName.value}'")
                else:
                    logger.error(f"No vehicle generator and no vehicles for InfectionTeam '{self.prototypeName.value}'")

    def get_etree_prototype(self):
        result = TeamPrototypeInfo.get_etree_prototype(self)
        # Vehicles start (ignore default)
        vehiclesTree = etree.Element("Vehicles")
        for vehicle in self.items.value:
            vehicle_node = etree.Element("Vehicle")
            vehicle_node.set("PrototypeName", str(vehicle["protoName"]))
            vehicle_node.set("Count", str(vehicle["count"]))
            vehiclesTree.append(vehicle_node)
        result.append(vehiclesTree)
        # Vehicles end
        return result


class InfectionZonePrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.minDistToPlayer = AnnotatedValue(100.0, "MinDistToPlayer", group_type=GroupType.PRIMARY)
        self.criticalTeamDist = AnnotatedValue(1000000.0, "CriticalTeamDist", group_type=GroupType.PRIMARY)
        self.criticalTeamTime = AnnotatedValue(0.0, "CriticalTeamTime", group_type=GroupType.PRIMARY)
        self.blindTeamDist = AnnotatedValue(1000000.0, "BlindTeamDist", group_type=GroupType.PRIMARY)
        self.blindTeamTime = AnnotatedValue(0.0, "BlindTeamTime", group_type=GroupType.PRIMARY)
        self.dropOutSegmentAngle = AnnotatedValue(180, "DropOutSegmentAngle", group_type=GroupType.PRIMARY)

        # DropOutTimeOut  # used in ai::InfectionZone::Registration()
        self.dropOutTimeOut = AnnotatedValue(0, "DropOutTimeOut", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            minDistToPlayer = read_from_xml_node(xmlNode, self.minDistToPlayer.name, do_not_warn=True)
            if minDistToPlayer is not None:
                self.minDistToPlayer.value = float(minDistToPlayer)

            criticalTeamDist = read_from_xml_node(xmlNode, self.criticalTeamDist.name, do_not_warn=True)
            if criticalTeamDist is not None:
                self.criticalTeamDist.value = float(criticalTeamDist)

            criticalTeamTime = read_from_xml_node(xmlNode, self.criticalTeamTime.name, do_not_warn=True)
            if criticalTeamTime is not None:
                self.criticalTeamTime.value = float(criticalTeamTime)

            blindTeamDist = read_from_xml_node(xmlNode, self.blindTeamDist.name, do_not_warn=True)
            if blindTeamDist is not None:
                self.blindTeamDist.value = float(blindTeamDist)

            blindTeamTime = read_from_xml_node(xmlNode, self.blindTeamTime.name, do_not_warn=True)
            if blindTeamTime is not None:
                self.blindTeamTime.value = float(blindTeamTime)

            dropOutSegmentAngle = read_from_xml_node(xmlNode, self.dropOutSegmentAngle.name, do_not_warn=True)
            if dropOutSegmentAngle is not None:
                self.dropOutSegmentAngle.value = int(dropOutSegmentAngle)

            dropOutTimeOut = read_from_xml_node(xmlNode, self.dropOutTimeOut.name, do_not_warn=True)
            if dropOutTimeOut is not None:
                self.dropOutTimeOut.value = float(dropOutTimeOut)
            return STATUS_SUCCESS


class VehiclesGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.vehicleDescriptions = AnnotatedValue([], "VehicleDescription", group_type=GroupType.PRIMARY,
                                                  display_type=DisplayType.MODIFICATION_INFO,
                                                  saving_type=SavingType.SPECIFIC)

        # moved init of desiredCount values and partOfSchwartz`s from LoadFromXML
        self.desiredCountLow = AnnotatedValue(-1, "DesiredCountLow", group_type=GroupType.PRIMARY,
                                              saving_type=SavingType.SPECIFIC)
        self.desiredCountHigh = AnnotatedValue(-1, "DesiredCountHigh", group_type=GroupType.PRIMARY,
                                               saving_type=SavingType.SPECIFIC)

        self.partOfSchwartzForCabin = AnnotatedValue(0.25, "partOfSchwartzForCabin", group_type=GroupType.PRIMARY)
        self.partOfSchwartzForBasket = AnnotatedValue(0.25, "partOfSchwartzForBasket", group_type=GroupType.PRIMARY)
        self.partOfSchwartzForGuns = AnnotatedValue(0.5, "partOfSchwartzForGuns", group_type=GroupType.PRIMARY)
        self.partOfSchwartzForWares = AnnotatedValue(0.0, "partOfSchwartzForWares", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            desiredCount = read_from_xml_node(xmlNode, "DesiredCount")
            if desiredCount is not None:
                tokensDesiredCount = desiredCount.split("-")
                token_length = len(tokensDesiredCount)

                if token_length == 2:
                    self.desiredCountLow.value = int(tokensDesiredCount[0])
                    self.desiredCountHigh.value = int(tokensDesiredCount[1])
                elif token_length == 1:
                    self.desiredCountLow.value = int(tokensDesiredCount[0])
                    self.desiredCountHigh.value = self.desiredCountLow.value
                else:
                    logger.error(f"VehicleGenerator {self.prototypeName.value} attrib DesiredCount range "
                                 f"should contain one or two numbers but contains {len(tokensDesiredCount.value)}")
                if self.desiredCountLow.value > self.desiredCountHigh.value:
                    logger.error(f"VehicleGenerator {self.prototypeName.value} attrib DesiredCount range invalid: "
                                 f"{self.desiredCountLow.value}-{self.desiredCountHigh.value}, "
                                 "should be from lesser to higher number")
                if self.desiredCountHigh.value > 5:
                    logger.error(f"VehicleGenerator {self.prototypeName.value} attrib DesiredCount high value: "
                                 f"{self.desiredCountHigh.value} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")

            if len(xmlNode.getchildren()) > 1:
                check_mono_xml_node(xmlNode, "Description")
                for description_entry in xmlNode.iterchildren(tag="Description"):
                    veh_description = self.VehicleDescription(xmlFile, description_entry)
                    self.vehicleDescriptions.value.append(veh_description)

            partOfSchwartzForCabin = read_from_xml_node(xmlNode, "partOfSchwartzForCabin", do_not_warn=True)
            if partOfSchwartzForCabin is not None:
                self.partOfSchwartzForCabin.value = float(partOfSchwartzForCabin)

            partOfSchwartzForBasket = read_from_xml_node(xmlNode, "partOfSchwartzForBasket", do_not_warn=True)
            if partOfSchwartzForBasket is not None:
                self.partOfSchwartzForBasket.value = float(partOfSchwartzForBasket)

            partOfSchwartzForGuns = read_from_xml_node(xmlNode, "partOfSchwartzForGuns", do_not_warn=True)
            if partOfSchwartzForGuns is not None:
                self.partOfSchwartzForGuns.value = float(partOfSchwartzForGuns)

            partOfSchwartzForWares = read_from_xml_node(xmlNode, "partOfSchwartzForWares", do_not_warn=True)
            if partOfSchwartzForWares is not None:
                self.partOfSchwartzForWares.value = float(partOfSchwartzForWares)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.vehicleDescriptions:
            for vehicle_description in self.vehicleDescriptions.value:
                vehicle_description.PostLoad(prototype_manager)

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)

        # DesiredCount start
        # Property name not equel to annotatedValue.Name
        desired_count = 0
        if self.desiredCountLow.value == self.desiredCountHigh.value:
            desired_count = str(self.desiredCountLow.value)
        else:
            desired_count = f'{self.desiredCountLow.value}-{self.desiredCountHigh.value}'
        result.set("DesiredCount", desired_count)
        # DesiredCount end

        add_value_to_node_as_child(result, self.vehicleDescriptions,
                                   lambda x: list(map(self.VehicleDescription.get_etree_prototype, x.value)))
        return result

    class VehicleDescription(object):
        def __init__(self, xmlFile, xmlNode):
            self.waresPrototypesNames = []
            self.waresPrototypesIds = []

            self.vehiclePrototypeNames = []
            self.vehiclePrototypeIds = []

            self.gunAffixGeneratorPrototypeName = ""
            self.gunAffixGeneratorPrototypeId = -1
            # mode partOfSchwartz from LoadFromXMK
            self.partOfSchwartz = -1.0
            self.LoadFromXML(xmlFile, xmlNode)

        def LoadFromXML(self, xmlFile, xmlNode):
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
                                 f" for VehiclesGenerator: '{self.prototypeName.value}'")
                prot = prototype_manager.InternalGetPrototypeInfo(vehicle_prot_name)
                if prot.className.value != "Vehicle":
                    logger.error(f"Unexpected prototype with class '{prot.className.value}' found "
                                 "for VehiclesGenerator's VehiclePrototypes, expected 'Vehicle'!")
                self.vehiclePrototypeIds.append(vehicle_prot_id)

            for ware_prot_name in self.waresPrototypesNames:
                ware_prot_id = prototype_manager.GetPrototypeId(ware_prot_name)
                if ware_prot_id == -1:
                    logger.error(f"Unknown ware prototype: '{ware_prot_id}' found"
                                 f" for VehiclesGenerator: '{self.prototypeName.value}'")
                prot = prototype_manager.InternalGetPrototypeInfo(ware_prot_name)
                if prot.className.value != "Ware":
                    logger.error(f"Unexpected prototype with class '{prot.className.value}' found "
                                 "for VehiclesGenerator's WaresPrototypes, expected 'Ware'!")
                self.waresPrototypesIds.append(ware_prot_id)

            if self.gunAffixGeneratorPrototypeName:
                self.gunAffixGeneratorPrototypeId = \
                    prototype_manager.GetPrototypeId(self.gunAffixGeneratorPrototypeName)
                if self.gunAffixGeneratorPrototypeId == -1:
                    logger.error(f"Unknown GunAffix prototype: '{self.gunAffixGeneratorPrototypeName}' found"
                                 f" for VehiclesGenerator: '{self.prototypeName.value}'")

        def get_etree_prototype(self):
            description_node = etree.Element("Description")
            description_node.set("VehiclesPrototypes", " ".join(self.vehiclePrototypeNames))
            description_node.set("WaresPrototypes", " ".join(self.waresPrototypesNames))
            description_node.set("GunAffixGeneratorPrototype", self.gunAffixGeneratorPrototypeName)
            description_node.set("PartOfSchwartz", str(self.partOfSchwartz))
            return description_node


class FormationPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.maxVehicles = 5
        self.polylinePoints = AnnotatedValue([], "Polyline", group_type=GroupType.SECONDARY,
                                             saving_type=SavingType.SPECIFIC)
        self.polylineLength = 0.0
        self.headOffset = 0.0
        self.linearVelocity = AnnotatedValue(100.0, "LinearVelocity", group_type=GroupType.SECONDARY)
        self.headPosition = 0
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)
        self.angularVelocity = AnnotatedValue(0.5, "AngularVelocity", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            linearVelocity = read_from_xml_node(xmlNode, self.linearVelocity.name, do_not_warn=True)
            if linearVelocity is not None:
                self.linearVelocity.value = float(linearVelocity)

            angularVelocity = read_from_xml_node(xmlNode, self.angularVelocity.name, do_not_warn=True)
            if angularVelocity is not None:
                self.angularVelocity.value = float(angularVelocity)

            self.LoadPolylinePoints(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.CalcPolylineLengths()

    def CalcPolylineLengths(self):
        self.polylineLength = 0.0
        self.headOffset = 0.0
        if self.polylinePoints.value:
            for i in range(len(self.polylinePoints.value) - 1):
                first_point = self.polylinePoints.value[i]
                second_point = self.polylinePoints.value[i + 1]
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
                        if self.polylinePoints.value:
                            self.headPosition = len(self.polylinePoints.value)
                        else:
                            self.headPosition = 0
                    self.polylinePoints.value.append(point)
                else:
                    logger.error(f"Unexpected coordinate format for Formation {self.prototypeName.value}, "
                                 "expected two numbers")

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)

        def prepare_polylines(polylinePoints):
            polyline_element = etree.Element(polylinePoints.name)
            for item in polylinePoints.value:
                point_element = etree.Element("Point")
                point_element.set("Coord", vector_short_to_string(item))
                polyline_element.append(point_element)
            return polyline_element
        add_value_to_node_as_child(result, self.polylinePoints, lambda x: prepare_polylines(x))
        return result


class SettlementPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.zoneInfos = []  # newer used
        self.vehiclesPrototypeId = -1
        self.vehiclesPrototypeName = AnnotatedValue("", "Vehicles", group_type=GroupType.SECONDARY)

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
            self.vehiclesPrototypeName.value = safe_check_and_set(self.vehiclesPrototypeName.default_value, xmlNode,
                                                                  self.vehiclesPrototypeName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.vehiclesPrototypeName.value:
            self.vehiclesPrototypeId = prototype_manager.GetPrototypeId(self.vehiclesPrototypeName.value)
            if self.vehiclesPrototypeId == -1:
                logger.error(f"Invalid vehicles prototype '{self.vehiclesPrototypeName.value}' "
                             f"for settlement prototype '{self.prototypeName.value}'")

    class AuxZoneInfo(object):
        def __init__(self):
            self.action = ""
            self.offset = deepcopy(ZERO_VECTOR)
            self.radius = 10.0


class InfectionLairPrototypeInfo(SettlementPrototypeInfo):
    def __init__(self, server):
        SettlementPrototypeInfo.__init__(self, server)


class TownPrototypeInfo(SettlementPrototypeInfo):
    def __init__(self, server):
        SettlementPrototypeInfo.__init__(self, server)
        self.musicName = AnnotatedValue("", "MusicName", group_type=GroupType.SECONDARY)
        self.gateModelName = AnnotatedValue("", "GateModelFile", group_type=GroupType.SECONDARY)
        self.maxDefenders = AnnotatedValue(1, "MaxDefenders", group_type=GroupType.SECONDARY)
        self.gunGeneratorPrototypeName = AnnotatedValue("", "GunGenerator", group_type=GroupType.SECONDARY)
        self.desiredGunsInWorkshop = AnnotatedValue(0, "DesiredGunsInWorkshop", group_type=GroupType.SECONDARY)
        self.gunAffixGeneratorPrototypeName = AnnotatedValue("", "GunAffixGenerator", group_type=GroupType.SECONDARY)
        self.gunAffixesCount = AnnotatedValue(0, "GunAffixesCount", group_type=GroupType.SECONDARY)
        self.cabinsAndBasketsAffixGeneratorPrototypeName = AnnotatedValue("", "CabinsAndBasketsAffixGenerator",
                                                                          group_type=GroupType.SECONDARY)
        self.cabinsAndBasketsAffixesCount = AnnotatedValue(0, "CabinsAndBasketsAffixesCount",
                                                           group_type=GroupType.SECONDARY)
        self.numCollisionLayersBelowVehicle = AnnotatedValue(2, "NumCollisionLayersBelowVehicle",
                                                             group_type=GroupType.SECONDARY)
        self.articles = AnnotatedValue([], "Articles", group_type=GroupType.SECONDARY, saving_type=SavingType.SPECIFIC)
        self.collisionTrimeshAllowed = AnnotatedValue(True, "CollisionTrimeshAllowed", group_type=GroupType.SECONDARY)

        self.resourceIdToRandomCoeffMap = []
        self.gunGeneratorPrototypeId = -1
        self.gunAffixGeneratorPrototypeId = -1
        self.cabinsAndBasketsAffixGeneratorPrototypeId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SettlementPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            self.musicName.value = safe_check_and_set(self.musicName.default_value, xmlNode, self.musicName.name)
            self.gateModelName.value = safe_check_and_set(self.gateModelName.default_value, xmlNode,
                                                          self.gateModelName.name)
            self.maxDefenders.value = safe_check_and_set(self.maxDefenders.default_value, xmlNode,
                                                         self.maxDefenders.name, "int")
            if self.maxDefenders.value > 5:
                logger.error(f"For Town prototype '{self.prototypeName.value}' maxDefenders > MAX_VEHICLES_IN_TEAM (5)")
            self.gunGeneratorPrototypeName.value = safe_check_and_set(self.gunGeneratorPrototypeName.default_value,
                                                                      xmlNode, self.gunGeneratorPrototypeName.name)
            desiredGunsInWorkshop = safe_check_and_set(self.desiredGunsInWorkshop.default_value, xmlNode,
                                                       self.desiredGunsInWorkshop.name, "int")
            if desiredGunsInWorkshop >= 0:
                self.desiredGunsInWorkshop.value = desiredGunsInWorkshop
            self.gunAffixGeneratorPrototypeName.value = safe_check_and_set(
                self.gunAffixGeneratorPrototypeName.default_value, xmlNode,
                self.gunAffixGeneratorPrototypeName.name)
            gunAffixesCount = safe_check_and_set(self.gunAffixesCount.default_value, xmlNode,
                                                 self.gunAffixesCount.name, "int")
            if gunAffixesCount >= 0:
                self.gunAffixesCount.value = gunAffixesCount
            self.cabinsAndBasketsAffixGeneratorPrototypeName.value = safe_check_and_set(
                self.cabinsAndBasketsAffixGeneratorPrototypeName.default_value,
                xmlNode,
                self.cabinsAndBasketsAffixGeneratorPrototypeName.name)
            cabinsAndBasketsAffixesCount = safe_check_and_set(self.cabinsAndBasketsAffixesCount.default_value, xmlNode,
                                                              self.cabinsAndBasketsAffixesCount.name, "int")
            if cabinsAndBasketsAffixesCount >= 0:
                self.cabinsAndBasketsAffixesCount.value = cabinsAndBasketsAffixesCount

            numCollisionLayersBelowVehicle = safe_check_and_set(self.numCollisionLayersBelowVehicle.default_value,
                                                                xmlNode,
                                                                self.numCollisionLayersBelowVehicle.name, "int")
            if numCollisionLayersBelowVehicle >= 0:
                self.numCollisionLayersBelowVehicle.value = numCollisionLayersBelowVehicle
            Article.LoadArticlesFromNode(self.articles.value, xmlFile, xmlNode, self.theServer.thePrototypeManager)
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
                    logger.error(f"Unknown resource name: {resourceName} for prot: {self.prototypeName.value}")
                else:
                    coeff = {"first": resourceId,
                             "second": self.RandomCoeffWithDispersion()}
                    coeff["second"].baseCoeff = newRandomCoeff
                    coeff["second"].baseDispersion = newRandomCoeff_4
                    self.resourceIdToRandomCoeffMap.append(coeff)

    def PostLoad(self, prototype_manager):
        SettlementPrototypeInfo.PostLoad(self, prototype_manager)
        self.gunGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.gunGeneratorPrototypeName.value)
        self.gunAffixGeneratorPrototypeId = prototype_manager.GetPrototypeId(self.gunAffixGeneratorPrototypeName.value)
        self.cabinsAndBasketsAffixGeneratorPrototypeId = \
            prototype_manager.GetPrototypeId(self.cabinsAndBasketsAffixGeneratorPrototypeName.value)
        if self.articles.value:
            for article in self.articles.value:
                article.PostLoad(prototype_manager)

    def get_etree_prototype(self):
        result = SettlementPrototypeInfo.get_etree_prototype(self)
        if self.articles.value != self.articles.value:
            for articleItem in self.articles.value:
                result.append(Article.get_etree_prototype(articleItem))
        return result

    class RandomCoeffWithDispersion(object):
        def __init__(self):
            self.baseCoeff = 1.0
            self.baseDispersion = 0.0


class LairPrototypeInfo(SettlementPrototypeInfo):
    def __init__(self, server):
        SettlementPrototypeInfo.__init__(self, server)
        self.maxAttackers = AnnotatedValue(1, "MaxAttackers", group_type=GroupType.SECONDARY)
        self.maxDefenders = AnnotatedValue(1, "MaxDefenders", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SettlementPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            self.maxAttackers.value = safe_check_and_set(self.maxAttackers.default_value, xmlNode,
                                                         self.maxAttackers.name, "int")
            if self.maxAttackers.value > 5:
                logger.error(f"Lair {self.prototypeName.value} attrib MaxAttackers: "
                             f"{self.maxAttackers.value} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")

            self.maxDefenders.value = safe_check_and_set(self.maxDefenders.default_value, xmlNode,
                                                         self.maxDefenders.name, "int")
            if self.maxDefenders.value > 5:
                logger.error(f"Lair {self.prototypeName.value} attrib MaxDefenders: "
                             f"{self.maxDefenders.value} is higher than permitted MAX_VEHICLES_IN_TEAM: 5")
            return STATUS_SUCCESS


class PlayerPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modelName = AnnotatedValue("", "ModelFile", group_type=GroupType.SECONDARY)
        self.skinNumber = AnnotatedValue(0, "SkinNum", group_type=GroupType.SECONDARY)
        self.cfgNumber = AnnotatedValue(0, "CfgNum", group_type=GroupType.SECONDARY)
        # ??? some magic with World SceneGraph

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.modelName.value = read_from_xml_node(xmlNode, self.modelName.name)
            skinNum = read_from_xml_node(xmlNode, self.skinNumber.name, do_not_warn=True)
            if skinNum is not None:
                skinNum = int(skinNum)
                if skinNum > 0:
                    self.skinNumber.value = skinNum

            cfgNum = read_from_xml_node(xmlNode, self.cfgNumber.name, do_not_warn=True)
            if cfgNum is not None:
                cfgNum = int(cfgNum)
                if cfgNum > 0:
                    self.cfgNumber.value = cfgNum
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
        self.minReward = AnnotatedValue(-1, "MinReward", group_type=GroupType.PRIMARY)  # default changed

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            minReward = read_from_xml_node(xmlNode, "MinReward")
            if minReward is not None:
                self.minReward.value = int(minReward)
            return STATUS_SUCCESS


class DynamicQuestConvoyPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = AnnotatedValue(0.0, "PlayerSchwarzPart", group_type=GroupType.SECONDARY)
        self.criticalDistFromPlayer = AnnotatedValue(100.0, "CriticalDistFromPlayer", group_type=GroupType.SECONDARY)
        self.criticalTime = AnnotatedValue(20.0, "CriticalTime", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, self.playerSchwarzPart.name)
            if playerSchwarzPart is not None:
                self.playerSchwarzPart.value = float(playerSchwarzPart)

            criticalDistFromPlayer = read_from_xml_node(xmlNode, self.criticalDistFromPlayer.name)
            if criticalDistFromPlayer is not None:
                self.criticalDistFromPlayer.value = float(criticalDistFromPlayer)

            criticalTime = read_from_xml_node(xmlNode, self.criticalTime.name)
            if criticalTime is not None:
                self.criticalTime.value = float(criticalTime)

            return STATUS_SUCCESS


class DynamicQuestDestroyPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.targetSchwarzPart = AnnotatedValue(0.0, "TargetSchwarzPart", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            targetSchwarzPart = read_from_xml_node(xmlNode, self.targetSchwarzPart.name)
            if targetSchwarzPart is not None:
                self.targetSchwarzPart.value = float(targetSchwarzPart)
            return STATUS_SUCCESS


class DynamicQuestHuntPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = AnnotatedValue(0.0, "PlayerSchwarzPart", group_type=GroupType.SECONDARY)
        self.huntSeasonLength = AnnotatedValue(0.0, "HuntSeasonLength", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, self.playerSchwarzPart.name)
            if playerSchwarzPart is not None:
                self.playerSchwarzPart.value = float(playerSchwarzPart)

            huntSeasonLength = read_from_xml_node(xmlNode, self.huntSeasonLength.name)
            if huntSeasonLength is not None:
                self.huntSeasonLength.value = float(huntSeasonLength)
            return STATUS_SUCCESS


class DynamicQuestPeacePrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerMoneyPart = AnnotatedValue(0.0, "PlayerMoneyPart", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerMoneyPart = read_from_xml_node(xmlNode, self.playerMoneyPart.name)
            if playerMoneyPart is not None:
                self.playerMoneyPart.value = float(playerMoneyPart)
            return STATUS_SUCCESS


class DynamicQuestReachPrototypeInfo(DynamicQuestPrototypeInfo):
    def __init__(self, server):
        DynamicQuestPrototypeInfo.__init__(self, server)
        self.playerSchwarzPart = AnnotatedValue(0.0, "PlayerSchwarzPart", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DynamicQuestPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            playerSchwarzPart = read_from_xml_node(xmlNode, self.playerSchwarzPart.name)
            if playerSchwarzPart is not None:
                self.playerSchwarzPart.value = float(playerSchwarzPart)
            return STATUS_SUCCESS


class SgNodeObjPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.engineModelName = AnnotatedValue("", "ModelFile", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.engineModelName.value = safe_check_and_set(self.engineModelName.default_value, xmlNode,
                                                            self.engineModelName.name)
            return STATUS_SUCCESS


class LightObjPrototypeInfo(SgNodeObjPrototypeInfo):
    def __init__(self, server):
        SgNodeObjPrototypeInfo.__init__(self, server)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)


class BossArmPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.frameToPickUpLoad = AnnotatedValue(0, "FrameToPickUpLoad", group_type=GroupType.SECONDARY)
        self.turningSpeed = AnnotatedValue(0.5, "TurningSpeed", group_type=GroupType.PRIMARY)
        self.lpIdForLoad = -1
        # custom display load value
        self.strLoadPoint = AnnotatedValue("", "LoadPointForLoad", group_type=GroupType.SECONDARY)
        # end
        self.cruticalNumExplodedLoads = AnnotatedValue(1, "CriticalNumExplodedLoads", group_type=GroupType.PRIMARY)
        self.attacks = AnnotatedValue([], "AttackActions", group_type=GroupType.SECONDARY,
                                      saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed", do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed.value = float(turningSpeed)

            frameToPickUpLoad = read_from_xml_node(xmlNode, "FrameToPickUpLoad", do_not_warn=True)
            if frameToPickUpLoad is not None:
                self.frameToPickUpLoad.value = int(frameToPickUpLoad)

            attack_actions = child_from_xml_node(xmlNode, self.attacks.name)
            check_mono_xml_node(attack_actions, "Attack")
            for attack_node in attack_actions.iterchildren(tag="Attack"):
                action = self.AttackActionInfo()
                action.LoadFromXML(attack_node)
                self.attacks.value.append(action)

            cruticalNumExplodedLoads = read_from_xml_node(xmlNode, "CriticalNumExplodedLoads", do_not_warn=True)
            if cruticalNumExplodedLoads is not None:
                self.cruticalNumExplodedLoads.value = int(cruticalNumExplodedLoads)
            # custom implementation. Originally called from PrototypeManager -> RefreshFromXml
            self.RefreshFromXml(xmlFile, xmlNode)
            # custom implementation ends
            return STATUS_SUCCESS

    def RefreshFromXml(self, xmlFile, xmlNode):
        # VehiclePartPrototypeInfo.RefreshFromXml(self, xmlFile, xmlNode)
        # model_obj = anim_model_server.GetItemByName(self.engineModelName.value)
        # if model_obj != -1:
        self.strLoadPoint.value = safe_check_and_set(self.strLoadPoint.default_value, xmlNode, "LoadPointForLoad")
        # m3d::AnimatedModel::GetLoadPointIdByName used to get actual 'lpIdForLoad'

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)

        def prepare_attacsElement(attacks):
            attacksElement = etree.Element(attacks.name)
            for attackItem in attacks.value:
                attacksElement.append(self.AttackActionInfo.get_etree_prototype(attackItem))
            return attacksElement
        add_value_to_node_as_child(result, self.attacks, lambda x: prepare_attacsElement(x))
        return result

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

        def get_etree_prototype(self):
            attack_node = etree.Element("Attack")
            attack_node.set("Action", GetActionByNum(self.action))
            attack_node.set("FrameToReleaseLoad", str(self.frameToReleaseLoad))
            return attack_node


class Boss02ArmPrototypeInfo(BossArmPrototypeInfo):
    def __init__(self, server):
        BossArmPrototypeInfo.__init__(self, server)
        self.frameToPickUpContainerForBlock = AnnotatedValue(0, "FrameToPickUpContainerForBlock",
                                                             group_type=GroupType.SECONDARY)
        self.frameToReleaseContainerForBlock = AnnotatedValue(0, "FrameToReleaseContainerForBlock",
                                                              group_type=GroupType.SECONDARY)
        self.frameToPickUpContainerForDie = AnnotatedValue(0, "FrameToPickUpContainerForDie",
                                                           group_type=GroupType.SECONDARY)
        self.frameToReleaseContainerForDie = AnnotatedValue(0, "FrameToReleaseContainerForDie",
                                                            group_type=GroupType.SECONDARY)
        self.actionForBlock = AnnotatedValue(-1, "ActionForBlock", group_type=GroupType.PRIMARY,
                                             saving_type=SavingType.SPECIFIC)
        self.actionForDie = AnnotatedValue(-1, "ActionForDie", group_type=GroupType.PRIMARY,
                                           saving_type=SavingType.SPECIFIC)
        self.blockingContainerPrototypeId = -1
        self.blockingContainerPrototypeName = AnnotatedValue("", "ContainerPrototype", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode: objectify.ObjectifiedElement):
        result = BossArmPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            frameToPickUpContainerForBlock = read_from_xml_node(xmlNode, "FrameToPickUpContainerForBlock",
                                                                do_not_warn=True)
            if frameToPickUpContainerForBlock is not None:
                self.frameToPickUpContainerForBlock.value = int(frameToPickUpContainerForBlock)

            frameToReleaseContainerForBlock = read_from_xml_node(xmlNode, "FrameToReleaseContainerForBlock",
                                                                 do_not_warn=True)
            if frameToReleaseContainerForBlock is not None:
                self.frameToReleaseContainerForBlock.value = int(frameToReleaseContainerForBlock)

            frameToPickUpContainerForDie = read_from_xml_node(xmlNode, "FrameToPickUpContainerForDie",
                                                              do_not_warn=True)
            if frameToPickUpContainerForDie is not None:
                self.frameToPickUpContainerForDie.value = int(frameToPickUpContainerForDie)

            frameToReleaseContainerForDie = read_from_xml_node(xmlNode, "FrameToReleaseContainerForDie",
                                                               do_not_warn=True)
            if frameToReleaseContainerForDie is not None:
                self.frameToReleaseContainerForDie.value = int(frameToReleaseContainerForDie)

            actionForBlock = read_from_xml_node(xmlNode, "ActionForBlock")
            self.actionForBlock.value = GetActionByName(actionForBlock)

            actionForDie = read_from_xml_node(xmlNode, "ActionForDie")
            self.actionForDie.value = GetActionByName(actionForDie)

            self.blockingContainerPrototypeName.value = \
                safe_check_and_set(self.blockingContainerPrototypeName.default_value,
                                   xmlNode, "ContainerPrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blockingContainerPrototypeId = prototype_manager.GetPrototypeId(self.blockingContainerPrototypeName.value)

    def get_etree_prototype(self):
        result = BossArmPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.actionForBlock, lambda x: GetActionByNum(x.value))
        add_value_to_node(result, self.actionForDie, lambda x: GetActionByNum(x.value))
        return result


class BossMetalArmPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.explosionEffectName = AnnotatedValue("", "ExplosionEffect", group_type=GroupType.SECONDARY)
        # isn't initialised here for this class in original but is loaded in LoadFromXML
        self.frameToPickUpLoad = AnnotatedValue(0, "FrameToPickUpLoad", group_type=GroupType.SECONDARY)
        # end
        self.turningSpeed = AnnotatedValue(0.5, "TurningSpeed", group_type=GroupType.SECONDARY)
        self.lpIdForLoad = -1
        self.loadProrotypeIds = []
        self.attacks = AnnotatedValue([], "AttackActions", group_type=GroupType.PRIMARY,
                                      saving_type=SavingType.SPECIFIC)
        self.numExplodedLoadsToDie = AnnotatedValue(1, "NumExplodedLoadsToDie", group_type=GroupType.PRIMARY)
        self.loadPrototypeNames = AnnotatedValue([], "LoadPrototypes", group_type=GroupType.PRIMARY,
                                                 saving_type=SavingType.SPECIFIC)
        # custom display load value
        self.strLoadPoint = AnnotatedValue("", "LoadPointForLoad", group_type=GroupType.SECONDARY)
        # end

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            self.explosionEffectName.value = read_from_xml_node(xmlNode, "ExplosionEffect")
            turningSpeed = read_from_xml_node(xmlNode, "TurningSpeed", do_not_warn=True)
            if turningSpeed is not None:
                self.turningSpeed.value = float(turningSpeed)

            frameToPickUpLoad = read_from_xml_node(xmlNode, "FrameToPickUpLoad", do_not_warn=True)
            if frameToPickUpLoad is not None:
                self.frameToPickUpLoad.value = float(frameToPickUpLoad)

            attack_actions = child_from_xml_node(xmlNode, "AttackActions")
            check_mono_xml_node(attack_actions, "Attack")
            for attack_node in attack_actions.iterchildren(tag="Attack"):
                action = self.AttackActionInfo()
                action.LoadFromXML(attack_node)
                self.attacks.value.append(action)

            loadPrototypeNames = read_from_xml_node(xmlNode, "LoadPrototypes", do_not_warn=True)
            if loadPrototypeNames is not None:
                self.loadPrototypeNames.value = loadPrototypeNames.split()

            numExplodedLoadsToDie = read_from_xml_node(xmlNode, "NumExplodedLoadsToDie", do_not_warn=True)
            if numExplodedLoadsToDie is not None:
                self.numExplodedLoadsToDie.value = int(numExplodedLoadsToDie)
            self.RefreshFromXml(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def RefreshFromXml(self, xmlFile, xmlNode):
        self.strLoadPoint.value = safe_check_and_set(self.strLoadPoint.default_value, xmlNode, "LoadPointForLoad")

    def PostLoad(self, prototype_manager):
        if self.loadPrototypeNames.value:
            for prot_name in self.loadPrototypeNames.value:
                prot_id = prototype_manager.GetPrototypeId(prot_name)
                if prot_id == -1:
                    logger.error("Invalid loadPrototypes/IDs for BossMetalArm prototype")
                else:
                    prot = prototype_manager.InternalGetPrototypeInfo(prot_name)
                    if prot.className.value != "BossMetalArmLoad":
                        logger.error("Invalid class for BossMetalArm LoadPrototype, expected 'BossMetalArmLoad', but "
                                     f"'{prot.className.value}' given for {self.prototypeName.value}!")
                    self.loadProrotypeIds.append(prot_id)
        else:
            logger.error(f"Empty loadPrototypes for BossMetalArm prototype {self.prototypeName.value}!")

    def get_etree_prototype(self):
        result = SimplePhysicObjPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.loadPrototypeNames, lambda x: " ".join(x.value))

        def prepare_attack_actions(attacks):
            attacksElement = etree.Element(attacks.name)
            for attack in attacks.value:
                attacksElement.append(self.AttackActionInfo.get_etree_prototype(attack))
            return attacksElement

        add_value_to_node_as_child(result, self.attacks, lambda x: prepare_attack_actions(x))
        return result

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

        def get_etree_prototype(self):
            attackElement = etree.Element("Attack")
            attackElement.set("Action", GetActionByNum(self.action))
            attackElement.set("FrameToReleaseLoad", str(self.frameToReleaseLoad))
            return attackElement


class BossMetalArmLoadPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)
        self.blastWavePrototypeId = -1
        self.explosionEffectName = AnnotatedValue("", "ExplosionEffect", group_type=GroupType.SECONDARY)
        self.maxHealth = AnnotatedValue(1.0, "MaxHealth", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.SECONDARY)
        self.isUpdating = AnnotatedValue(True, "IsUpdating", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DummyObjectPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value, xmlNode,
                                                                   "BlastWavePrototype")
            self.explosionEffectName.value = safe_check_and_set(self.explosionEffectName.default_value, xmlNode,
                                                                "ExplosionEffect")

            maxHealth = read_from_xml_node(xmlNode, "MaxHealth")
            if maxHealth is not None:
                self.maxHealth.value = float(maxHealth)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)


class Boss03PartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)


class Boss04PartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)


class Boss04DronePrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.maxLinearVelocity = AnnotatedValue(0.0, "MaxLinearVelocity", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxLinearVelocity = read_from_xml_node(xmlNode, "MaxLinearVelocity")
            if maxLinearVelocity is not None:
                self.maxLinearVelocity.value = float(maxLinearVelocity)
            return STATUS_SUCCESS


class Boss04StationPartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.criticalMeshGroupIds = []
        self.collisionTrimeshAllowed = AnnotatedValue(False, "CollisionTrimeshAllowed",
                                                      group_type=GroupType.SECONDARY)
        self.maxHealth = 0.0
        # custom value, only created and used in RefreshFromXml in original
        self.strCriticalMeshGroups = AnnotatedValue("", "CriticalMeshGroups", group_type=GroupType.SECONDARY,
                                                    saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        # custom implementation. Originally called from PrototypeManager -> RefreshFromXml
        result = VehiclePartPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.RefreshFromXml(xmlFile, xmlNode)
            return STATUS_SUCCESS

    def RefreshFromXml(self, xmlFile, xmlNode):
        strCriticalMeshGroups = read_from_xml_node(xmlNode, "CriticalMeshGroups", do_not_warn=True)
        if strCriticalMeshGroups is not None:
            self.strCriticalMeshGroups.value = strCriticalMeshGroups.split()

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.strCriticalMeshGroups, lambda x: " ".join(x.value))
        return result


class Boss04StationPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)


class Boss02PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.stateInfos = AnnotatedValue([], "States", group_type=GroupType.SECONDARY, saving_type=SavingType.SPECIFIC)
        self.speed = AnnotatedValue(1.0, "Speed", group_type=GroupType.SECONDARY)
        self.containerPrototypeId = -1
        self.relPosForContainerPickUp = {}
        self.relRotForContainerPickUp = {}
        self.relPosForContainerPutDown = {}
        self.containerPrototypeName = AnnotatedValue("", "ContainerPrototype", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            states_node = child_from_xml_node(xmlNode, "States")
            check_mono_xml_node(states_node, "State")
            for state_node in states_node.iterchildren(tag="State"):
                state = self.StateInfo()
                state.LoadFromXML(xmlFile, state_node)
                self.stateInfos.value.append(state)
            speed = read_from_xml_node(xmlNode, "Speed")
            if speed is not None:
                self.speed.value = float(speed)
            self.containerPrototypeName.value = read_from_xml_node(xmlNode, "ContainerPrototype")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for state_info in self.stateInfos.value:
            state_info.PostLoad(prototype_manager)
        self.containerPrototypeId = prototype_manager.GetPrototypeId(self.containerPrototypeName.value)

    def get_etree_prototype(self):
        result = ComplexPhysicObjPrototypeInfo.get_etree_prototype(self)

        def get_states(stateInfos):
            states_element = etree.Element("States")
            for state in stateInfos:
                states_element.append(self.StateInfo.get_etree_prototype(state))
            return states_element
        add_value_to_node_as_child(result, self.stateInfos, lambda x: get_states(x.value))

        return result

    class StateInfo(object):
        def __init__(self):
            self.loadPrototypeIds = []
            self.loadPrototypeNames = []
            self.position = deepcopy(ZERO_VECTOR)

        def LoadFromXML(self, xmlFile, xmlNode):
            self.loadPrototypeNames = read_from_xml_node(xmlNode, "LoadPrototypes").split()
            position = read_from_xml_node(xmlNode, "RelPos")
            position = position.split()
            self.position = {"x": position[0],
                             "y": position[1],
                             "z": position[2]}

        def PostLoad(self, prototype_manager):
            for prot_name in self.loadPrototypeNames:
                self.loadPrototypeIds.append(prototype_manager.GetPrototypeId(prot_name))

        def get_etree_prototype(self):
            state_element = etree.Element("State")
            state_element.set("LoadPrototypes", " ".join(map(str, self.loadPrototypeNames)))
            state_element.set("RelPos", vector_to_string(self.position))
            return state_element


class AnimatedComplexPhysicObjPrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)


class Boss03PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        AnimatedComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.dronePrototypeNames = AnnotatedValue([], "DronePrototypes", group_type=GroupType.PRIMARY,
                                                  saving_type=SavingType.SPECIFIC)
        self.dronePrototypeIds = []
        self.maxDrones = AnnotatedValue(1, "MaxDrones", group_type=GroupType.PRIMARY)
        self.maxHealth = AnnotatedValue(1.0, "MaxHealth", group_type=GroupType.PRIMARY)
        self.droneRelPosition = deepcopy(ZERO_VECTOR)
        self.droneRelRotation = deepcopy(IDENTITY_QUATERNION)
        self.maxHorizAngularVelocity = AnnotatedValue(0.0, "MaxHorizAngularVelocity", group_type=GroupType.SECONDARY)
        self.horizAngularAcceleration = AnnotatedValue(0.0, "HorizAngularAcceleration", group_type=GroupType.SECONDARY)
        self.maxVertAngularVelocity = AnnotatedValue(0.0, "MaxVertAngularVelocity", group_type=GroupType.SECONDARY)
        self.vertAngularAcceleration = AnnotatedValue(0.0, "VertAngularAcceleration", group_type=GroupType.SECONDARY)
        self.maxLinearVelocity = AnnotatedValue(0.0, "MaxLinearVelocity", group_type=GroupType.SECONDARY)
        self.linearAcceleration = AnnotatedValue(0.0, "LinearAcceleration", group_type=GroupType.SECONDARY)
        self.pathTrackTiltAngle = AnnotatedValue(0.0, "PathTrackTiltAngle", group_type=GroupType.SECONDARY,
                                                 saving_type=SavingType.SPECIFIC)
        self.maxShootingTime = AnnotatedValue(1.0, "MaxShootingTime", group_type=GroupType.PRIMARY)
        self.defaultHover = AnnotatedValue(10.0, "DefaultHover", group_type=GroupType.SECONDARY)
        self.hoverForPlacingDrones = AnnotatedValue(10.0, "HoverForPlacingDrones", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.dronePrototypeNames.value = read_from_xml_node(xmlNode, "DronePrototypes").split()
            # experimental do_not_warn
            maxDrones = read_from_xml_node(xmlNode, "MaxDrones", do_not_warn=True)
            if maxDrones is not None:
                self.maxDrones.value = int(maxDrones)

            # experimental do_not_warn
            maxHealth = read_from_xml_node(xmlNode, "MaxHealth", do_not_warn=True)
            if maxHealth is not None:
                self.maxHealth.value = float(maxHealth)

            # experimental do_not_warn
            maxHorizAngularVelocity = read_from_xml_node(xmlNode, "MaxHorizAngularVelocity", do_not_warn=True)
            if maxHorizAngularVelocity is not None:
                self.maxHorizAngularVelocity.value = float(maxHorizAngularVelocity)

            # experimental do_not_warn
            horizAngularAcceleration = read_from_xml_node(xmlNode, "HorizAngularAcceleration", do_not_warn=True)
            if horizAngularAcceleration is not None:
                self.horizAngularAcceleration.value = float(horizAngularAcceleration)

            # experimental do_not_warn
            maxVertAngularVelocity = read_from_xml_node(xmlNode, "MaxVertAngularVelocity", do_not_warn=True)
            if maxVertAngularVelocity is not None:
                self.maxVertAngularVelocity.value = float(maxVertAngularVelocity)

            # experimental do_not_warn
            vertAngularAcceleration = read_from_xml_node(xmlNode, "VertAngularAcceleration", do_not_warn=True)
            if vertAngularAcceleration is not None:
                self.vertAngularAcceleration.value = float(vertAngularAcceleration)

            # experimental do_not_warn
            maxLinearVelocity = read_from_xml_node(xmlNode, "MaxLinearVelocity", do_not_warn=True)
            if maxLinearVelocity is not None:
                self.maxLinearVelocity.value = float(maxLinearVelocity)

            # experimental do_not_warn
            linearAcceleration = read_from_xml_node(xmlNode, "LinearAcceleration", do_not_warn=True)
            if linearAcceleration is not None:
                self.linearAcceleration.value = float(linearAcceleration)

            pathTrackTiltAngle = read_from_xml_node(xmlNode, "PathTrackTiltAngle")
            if pathTrackTiltAngle is not None:
                self.pathTrackTiltAngle.value = float(pathTrackTiltAngle) * pi / 180  # 0.017453292

            maxShootingTime = read_from_xml_node(xmlNode, "MaxShootingTime")
            if maxShootingTime is not None:
                self.maxShootingTime.value = float(maxShootingTime)

            defaultHover = read_from_xml_node(xmlNode, "DefaultHover")
            if defaultHover is not None:
                self.defaultHover.value = float(defaultHover)

            hoverForPlacingDrones = read_from_xml_node(xmlNode, "HoverForPlacingDrones")
            if hoverForPlacingDrones is not None:
                self.hoverForPlacingDrones.value = float(hoverForPlacingDrones)

            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        for prot_name in self.dronePrototypeNames.value:
            dronePrototypeId = prototype_manager.GetPrototypeId(prot_name)
            if dronePrototypeId == -1:
                logger.error("Invalid drone prototype/prototype ID for Boss03")
            self.dronePrototypeIds.append(dronePrototypeId)

    def get_etree_prototype(self):
        result = ComplexPhysicObjPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.dronePrototypeNames, lambda x: " ".join(x.value))
        add_value_to_node(result, self.pathTrackTiltAngle, lambda x: str(x.value / pi * 180))
        return result


class Boss04PrototypeInfo(ComplexPhysicObjPrototypeInfo):
    def __init__(self, server):
        ComplexPhysicObjPrototypeInfo.__init__(self, server)
        self.stationPrototypeName = AnnotatedValue("", "StationPrototype", group_type=GroupType.PRIMARY)
        self.dronePrototypeName = AnnotatedValue("", "DronePrototype", group_type=GroupType.PRIMARY)
        defaultTime = {"x": 10.0, "y": 20.0}
        self.timeBetweenDrones = AnnotatedValue(defaultTime, "TimeBetweenDrones", group_type=GroupType.PRIMARY,
                                                saving_type=SavingType.SPECIFIC)
        self.stationPrototypeId = -1
        self.dronePrototypeId = -1
        self.maxDrones = AnnotatedValue(0, "MaxDrones", group_type=GroupType.PRIMARY)
        self.stationToPartBindings = AnnotatedValue([], "StationToPartBindings", group_type=GroupType.SECONDARY,
                                                    saving_type=SavingType.SPECIFIC)
        self.droneSpawningLpIds = []
        self.droneSpawningLpNames = AnnotatedValue([], "DroneSpawningLps", group_type=GroupType.SECONDARY,
                                                   saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ComplexPhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.stationPrototypeName.value = read_from_xml_node(xmlNode, "StationPrototype")
            self.dronePrototypeName.value = read_from_xml_node(xmlNode, "DronePrototype")
            self.timeBetweenDrones.value = parse_str_to_vector(read_from_xml_node(xmlNode, "TimeBetweenDrones"), size=2)
            maxDrones = read_from_xml_node(xmlNode, "MaxDrones")
            if maxDrones is not None:
                maxDrones = int(maxDrones)
                if maxDrones > 0:
                    self.maxDrones.value = maxDrones
            self.droneSpawningLpNames.value = read_from_xml_node(xmlNode, "DroneSpawningLps").split()
            stationToPartBindings = child_from_xml_node(xmlNode, "StationToPartBindings")
            check_mono_xml_node(stationToPartBindings, "Station")
            for station_node in stationToPartBindings.iterchildren(tag="Station"):
                station = {"id": read_from_xml_node(station_node, "id"),
                           "parts": read_from_xml_node(station_node, "Parts").split()}
                self.stationToPartBindings.value.append(station)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        ComplexPhysicObjPrototypeInfo.PostLoad(self, prototype_manager)
        self.stationPrototypeId = prototype_manager.GetPrototypeId(self.stationPrototypeName.value)
        self.dronePrototypeId = prototype_manager.GetPrototypeId(self.dronePrototypeName.value)

    def get_etree_prototype(self):
        result = ComplexPhysicObjPrototypeInfo.get_etree_prototype(self)

        def prepare_station_parts(stationToPartBindings):
            stationToPartBindingsElement = etree.Element(stationToPartBindings.name)
            for part in stationToPartBindings.value:
                partElement = etree.Element("Station")
                partElement.set("id", part["id"])
                partElement.set("Parts", " ".join(part["parts"]))
                stationToPartBindingsElement.append(partElement)
            return stationToPartBindingsElement
        add_value_to_node(result, self.timeBetweenDrones, lambda x: vector_short_to_string(x.value))
        add_value_to_node(result, self.droneSpawningLpNames, lambda x: " ".join(x.value))
        add_value_to_node_as_child(result, self.stationToPartBindings, lambda x: prepare_station_parts(x))
        return result


class BlastWavePrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.waveForceIntensity = AnnotatedValue(0.0, "WaveForceIntensity", group_type=GroupType.PRIMARY)
        self.waveDamageIntensity = AnnotatedValue(0.0, "WaveDamageIntensity", group_type=GroupType.PRIMARY)
        self.effectName = AnnotatedValue("", "Effect", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("SPHERE")
            waveForceIntensity = read_from_xml_node(xmlNode, "WaveForceIntensity")
            if waveForceIntensity is not None:
                self.waveForceIntensity.value = float(waveForceIntensity)

            waveDamageIntensity = read_from_xml_node(xmlNode, "WaveDamageIntensity")
            if waveDamageIntensity is not None:
                self.waveDamageIntensity.value = float(waveDamageIntensity)

            self.effectName.value = safe_check_and_set(self.effectName.default_value, xmlNode, "Effect")
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class BulletLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.groupingAngle = AnnotatedValue(0.0, "GroupingAngle", group_type=GroupType.SECONDARY,
                                            saving_type=SavingType.SPECIFIC)
        self.numBulletsInShot = AnnotatedValue(1, "NumBulletsInShot", group_type=GroupType.SECONDARY)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.PRIMARY)
        self.tracerRange = AnnotatedValue(1, "TracerRange", group_type=GroupType.SECONDARY)
        self.tracerEffectName = AnnotatedValue("", "TracerEffect", group_type=GroupType.SECONDARY)
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(0, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            # groupingAngle implemented partially. Check ai::BulletLauncherPrototypeInfo::LoadFromXML
            groupingAngle = read_from_xml_node(xmlNode, self.groupingAngle.name, do_not_warn=True)
            if groupingAngle is not None:
                self.groupingAngle.value = float(groupingAngle)
                self.groupingAngle.value = (self.groupingAngle.value * 0.017453292) * 0.5

            numBulletsInShot = read_from_xml_node(xmlNode, self.numBulletsInShot.name, do_not_warn=True)
            if numBulletsInShot is not None:
                self.numBulletsInShot.value = int(numBulletsInShot)

            tracerRange = read_from_xml_node(xmlNode, self.tracerRange.name, do_not_warn=True)
            if tracerRange is not None:
                self.tracerRange.value = int(tracerRange)

            self.blastWavePrototypeName.value = read_from_xml_node(xmlNode, self.blastWavePrototypeName.name, True)
            self.tracerEffectName.value = read_from_xml_node(xmlNode, self.tracerEffectName.name, True)
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = GunPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.groupingAngle, lambda x: str((x.value / 0.5) / 0.017453292))
        return result


class CompoundVehiclePartPrototypeInfo(VehiclePartPrototypeInfo):
    def __init__(self, server):
        VehiclePartPrototypeInfo.__init__(self, server)
        self.partInfo = AnnotatedValue({}, "PartInfo", group_type=GroupType.PRIMARY,
                                       saving_type=SavingType.SPECIFIC)

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
                    self.partInfo.value[part_id] = new_part
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        for tpart in self.partInfo.value.values():
            tpart.prototypeId = prototype_manager.GetPrototypeId(tpart.prototypeName)

    def get_etree_prototype(self):
        result = VehiclePartPrototypeInfo.get_etree_prototype(self)
        if self.partInfo.value != self.partInfo.default_value:
            for key in self.partInfo.value:
                partElement = etree.Element("Part")
                partElement.set("id", key)
                partElement.set("Prototype", self.partInfo.value[key].prototypeName)
                result.append(partElement)
        return result

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
        self.withAngleLimit = AnnotatedValue(True, "WithAngleLimit", group_type=GroupType.PRIMARY)
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(1, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.withAngleLimit.value = parse_str_to_bool(self.withAngleLimit.default_value,
                                                          read_from_xml_node(xmlNode,
                                                                             self.withAngleLimit.name,
                                                                             do_not_warn=True))
            return STATUS_SUCCESS


class RocketVolleyLauncherPrototypeInfo(RocketLauncherPrototypeInfo):
    def __init__(self, server):
        RocketLauncherPrototypeInfo.__init__(self, server)
        self.actionDist = AnnotatedValue(0.0, "ActionDist", group_type=GroupType.PRIMARY)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            actionDist = read_from_xml_node(xmlNode, self.actionDist.name)
            if actionDist is not None:
                self.actionDist.value = float(actionDist)
            return STATUS_SUCCESS


class ThunderboltLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(2, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)
        self.actionDist = AnnotatedValue(0.0, "ActionDist", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            actionDist = read_from_xml_node(xmlNode, self.actionDist.name)
            if actionDist is not None:
                self.actionDist.value = float(actionDist)
            return STATUS_SUCCESS


class PlasmaBunchLauncherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        # never used
        self.bunchPrototypeName = ""
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(2, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)


class MortarPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(1, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)
        self.withShellsPoolLimit = AnnotatedValue(True, "WithShellsPoolLimit", group_type=GroupType.PRIMARY)
        self.initialVelocity = AnnotatedValue(50.0, "InitialVelocity", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            initialVelocity = read_from_xml_node(xmlNode, self.initialVelocity.name)
            if initialVelocity is not None:
                self.initialVelocity.value = float(initialVelocity)
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
        # damageType save and load implemented in parrent
        self.damageType = AnnotatedValue(1, "DamageType", group_type=GroupType.PRIMARY,
                                         saving_type=SavingType.SPECIFIC)


class TurboAccelerationPusherPrototypeInfo(GunPrototypeInfo):
    def __init__(self, server):
        GunPrototypeInfo.__init__(self, server)
        self.accelerationValue = AnnotatedValue(1.0, "AccelerationValue", group_type=GroupType.PRIMARY)
        self.accelerationTime = AnnotatedValue(0.0, "AccelerationTime", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = GunPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            accelerationValue = read_from_xml_node(xmlNode, self.accelerationValue.name)
            if accelerationValue is not None:
                self.accelerationValue.value = float(accelerationValue)

            accelerationTime = read_from_xml_node(xmlNode, self.accelerationTime.name)
            if accelerationTime is not None:
                self.accelerationTime.value = float(accelerationTime)
            return STATUS_SUCCESS


class ShellPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)


class RocketPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = AnnotatedValue(1.0, "Velocity", group_type=GroupType.PRIMARY)
        self.acceleration = AnnotatedValue(1.0, "Acceleration", group_type=GroupType.PRIMARY)
        self.minTurningRadius = AnnotatedValue(1.0, "MinTurningRadius", group_type=GroupType.PRIMARY)
        self.flyTime = AnnotatedValue(1.0, "FlyTime", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeId = -1
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        self.SetGeomType("BOX")
        if result == STATUS_SUCCESS:
            velocity = read_from_xml_node(xmlNode, self.velocity.name)
            if velocity is not None:
                self.velocity.value = float(velocity)

            acceleration = read_from_xml_node(xmlNode, self.acceleration.name)
            if acceleration is not None:
                self.acceleration.value = float(acceleration)

            minTurningRadius = read_from_xml_node(xmlNode, self.minTurningRadius.name)
            if minTurningRadius is not None:
                self.minTurningRadius.value = float(minTurningRadius)

            flyTime = read_from_xml_node(xmlNode, self.flyTime.name)
            if flyTime is not None:
                self.flyTime.value = float(flyTime)

            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value,
                                                                   xmlNode,
                                                                   self.blastWavePrototypeName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName.value:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)
            if self.blastWavePrototypeId == -1:
                logger.error(f"Unknown blast wave prototype name: '{self.blastWavePrototypeName.value}' "
                             f"for rocket prototype: '{self.prototypeName.value}'")


class PlasmaBunchPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = AnnotatedValue(1.0, "Velocity", group_type=GroupType.PRIMARY)
        self.acceleration = AnnotatedValue(1.0, "Acceleration", group_type=GroupType.PRIMARY)
        self.flyTime = AnnotatedValue(1.0, "FlyTime", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            velocity = read_from_xml_node(xmlNode, self.velocity.name)
            if velocity is not None:
                self.velocity.value = float(velocity)

            acceleration = read_from_xml_node(xmlNode, self.acceleration.name)
            if acceleration is not None:
                self.acceleration.value = float(acceleration)

            flyTime = read_from_xml_node(xmlNode, self.flyTime.name)
            if flyTime is not None:
                self.flyTime.value = float(flyTime)

            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value,
                                                                   xmlNode,
                                                                   self.blastWavePrototypeName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName.value:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)
            if self.blastWavePrototypeId == -1:
                logger.error(f"Unknown blast wave prototype name: '{self.blastWavePrototypeName.value}' "
                             f"for plasma prototype: '{self.prototypeName.value}'")


class MortarShellPrototypeInfo(ShellPrototypeInfo):
    def __init__(self, server):
        ShellPrototypeInfo.__init__(self, server)
        self.velocity = 1.0
        self.acceleration = 1.0
        self.flyTime = AnnotatedValue(1.0, "FlyTime", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWavePrototype", group_type=GroupType.PRIMARY)
        self.blastWavePrototypeId = -1

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ShellPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            flyTime = read_from_xml_node(xmlNode, self.flyTime.name)
            if flyTime is not None:
                self.flyTime.value = float(flyTime)

            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value,
                                                                   xmlNode,
                                                                   self.blastWavePrototypeName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName.value:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)
            if self.blastWavePrototypeId == -1:
                logger.error(f"Unknown blast wave prototype name: '{self.blastWavePrototypeName.value}' "
                             f"for Mortar prototype: '{self.prototypeName.value}'")


class MinePrototypeInfo(RocketPrototypeInfo):
    def __init__(self, server):
        RocketPrototypeInfo.__init__(self, server)
        self.TTL = AnnotatedValue(100.0, "TTL", group_type=GroupType.SECONDARY)
        self.timeForActivation = AnnotatedValue(0.0, "TimeForActivation", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = RocketPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            TTL = read_from_xml_node(xmlNode, self.TTL.name)
            if TTL is not None:
                self.TTL.value = float(TTL)

            timeForActivation = read_from_xml_node(xmlNode, self.timeForActivation.name)
            if timeForActivation is not None:
                self.timeForActivation.value = float(timeForActivation)
            return STATUS_SUCCESS


class ThunderboltPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.flyTime = AnnotatedValue(1.0, "FlyTime", group_type=GroupType.SECONDARY)
        self.damage = AnnotatedValue(0.0, "Damage", group_type=GroupType.SECONDARY)
        self.averageSegmentLength = AnnotatedValue(0.1, "AverageSegmentLength", group_type=GroupType.SECONDARY)
        self.effectName = AnnotatedValue("", "Effect", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            flyTime = read_from_xml_node(xmlNode, self.flyTime.name)
            if flyTime is not None:
                self.flyTime.value = float(flyTime)

            damage = read_from_xml_node(xmlNode, self.damage.name, do_not_warn=True)
            if damage is not None:
                self.damage.value = float(damage)

            averageSegmentLength = read_from_xml_node(xmlNode, self.averageSegmentLength.name)
            if averageSegmentLength is not None:
                self.averageSegmentLength.value = float(averageSegmentLength)

            self.effectName.value = read_from_xml_node(xmlNode, self.effectName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.averageSegmentLength.value < 0.01:
            self.averageSegmentLength.value = 0.01


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
        self.TTL = AnnotatedValue(0.0, "TTL", group_type=GroupType.SECONDARY)
        self.timeForActivation = AnnotatedValue(0.0, "ActivateTime", group_type=GroupType.SECONDARY)
        self.effectName = AnnotatedValue(False, "Effect", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = LocationPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            TTL = read_from_xml_node(xmlNode, self.TTL.name)
            if TTL is not None:
                self.TTL.value = float(TTL)

            timeForActivation = read_from_xml_node(xmlNode, self.timeForActivation.name)
            if timeForActivation is not None:
                self.timeForActivation.value = float(timeForActivation)

            self.effectName.value = read_from_xml_node(xmlNode, self.effectName.name)
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
        self.maxLinearVelocity = AnnotatedValue(0.0 * 0.27777779, "MaxLinearVelocity",
                                                group_type=GroupType.PRIMARY,
                                                saving_type=SavingType.SPECIFIC)
        self.linearAcceleration = AnnotatedValue(0.0, "LinearAcceleration", group_type=GroupType.SECONDARY)
        self.platformOpenFps = AnnotatedValue(2, "PlatformOpenFps", group_type=GroupType.SECONDARY)
        self.vehicleMaxSpeed = AnnotatedValue(72.0 * 0.27777779, "VehicleMaxSpeed",
                                              group_type=GroupType.PRIMARY,
                                              saving_type=SavingType.SPECIFIC)
        self.vehicleRelativePosition = deepcopy(ZERO_VECTOR)
        self.isUpdating = AnnotatedValue(True, "IsUpdating", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = DummyObjectPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxLinearVelocity = read_from_xml_node(xmlNode, self.maxLinearVelocity.name)
            if maxLinearVelocity is not None:
                self.maxLinearVelocity.value = float(maxLinearVelocity)
                self.maxLinearVelocity.value = self.maxLinearVelocity.value * 0.27777779  # ~5/18 or 50/180

            linearAcceleration = read_from_xml_node(xmlNode, self.linearAcceleration.name)
            if linearAcceleration is not None:
                self.linearAcceleration.value = float(linearAcceleration)

            platformOpenFps = read_from_xml_node(xmlNode, self.platformOpenFps.name)
            if platformOpenFps is not None:
                self.platformOpenFps.value = int(platformOpenFps)

            vehicleMaxSpeed = read_from_xml_node(xmlNode, self.vehicleMaxSpeed.name, do_not_warn=True)
            if vehicleMaxSpeed is not None:
                self.vehicleMaxSpeed.value = float(vehicleMaxSpeed)
                self.vehicleMaxSpeed.value = self.vehicleMaxSpeed.value * 0.27777779  # ~5/18 or 50/180
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = DummyObjectPrototypeInfo.get_etree_prototype(self)
        add_value_to_node(result, self.maxLinearVelocity, lambda x: str(x.value / 0.27777779))
        add_value_to_node(result, self.vehicleMaxSpeed, lambda x: str(x.value / 0.27777779))
        return result


class BuildingPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.buildingType = AnnotatedValue(5, "BuildingType", group_type=GroupType.SECONDARY,
                                           saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            buildingTypeName = safe_check_and_set("", xmlNode, self.buildingType.name)
            self.buildingType.value = Building.GetBuildingTypeByName(buildingTypeName)
            return STATUS_SUCCESS

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)
        if self.buildingType.value is not None:
            add_value_to_node(result, self.buildingType, lambda x: Building.GetBuildingTypeNameByNum(x.value))
        return result


class BarPrototypeInfo(BuildingPrototypeInfo):
    def __init__(self, server):
        BuildingPrototypeInfo.__init__(self, server)
        self.withBarman = AnnotatedValue(True, "WithBarman", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = BuildingPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.withBarman.value = parse_str_to_bool(self.withBarman.default_value,
                                                      read_from_xml_node(xmlNode,
                                                                         self.withBarman.name,
                                                                         do_not_warn=True))
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class WorkshopPrototypeInfo(BuildingPrototypeInfo):
    def __init__(self, server):
        BuildingPrototypeInfo.__init__(self, server)


class WarePrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.maxItems = AnnotatedValue(1, "MaxItems", group_type=GroupType.SECONDARY)
        self.maxDurability = AnnotatedValue(1.0, "Durability", group_type=GroupType.SECONDARY)
        self.priceDispersion = AnnotatedValue(0.0, "PriceDispersion", group_type=GroupType.SECONDARY)
        self.modelName = AnnotatedValue("", "ModelFile", group_type=GroupType.SECONDARY)
        self.minCount = AnnotatedValue(0, "MinCount", group_type=GroupType.SECONDARY)
        self.maxCount = AnnotatedValue(50, "MaxCount", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            maxItems = read_from_xml_node(xmlNode, self.maxItems.name, do_not_warn=True)
            if maxItems is not None:
                maxItems = int(maxItems)
                if maxItems >= 0:
                    self.maxItems.value = maxItems

            maxDurability = read_from_xml_node(xmlNode, self.maxDurability.name, do_not_warn=True)
            if maxDurability is not None:
                self.maxDurability.value = float(maxDurability)

            priceDispersion = read_from_xml_node(xmlNode, self.priceDispersion.name, do_not_warn=True)
            if priceDispersion is not None:
                self.priceDispersion.value = float(priceDispersion)

            if self.priceDispersion.value < 0.0 or self.priceDispersion.value > 100.0:
                logger(f"Price dispersion can't be outside 0.0-100.0 range: see {self.prototypeName.value}")

            self.modelName.value = safe_check_and_set(self.modelName.default_value, xmlNode, self.modelName.name)

            minCount = read_from_xml_node(xmlNode, self.minCount.name, do_not_warn=True)
            if minCount is not None:
                self.minCount.value = int(minCount)

            maxCount = read_from_xml_node(xmlNode, self.maxCount.name, do_not_warn=True)
            if maxCount is not None:
                self.maxCount.value = int(maxCount)
            return STATUS_SUCCESS


class QuestItemPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.modelName = AnnotatedValue("", "ModelFile", group_type=GroupType.VISUAL)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.modelName.value = safe_check_and_set(self.modelName.value, xmlNode, "ModelFile")
            return STATUS_SUCCESS


class BreakableObjectPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.destroyable = AnnotatedValue(-1, "Destroyable", group_type=GroupType.SECONDARY)  # default changed
        self.criticalHitEnergy = AnnotatedValue(None, "CriticalHitEnergy", group_type=GroupType.SECONDARY)
        self.effectType = AnnotatedValue("WOOD", "EffectType", group_type=GroupType.SECONDARY)
        self.destroyEffectType = AnnotatedValue("BLOW", "DestroyEffectType", group_type=GroupType.SECONDARY)
        self.brokenModelName = AnnotatedValue("brokenTest", "BrokenModel", group_type=GroupType.SECONDARY)
        self.destroyedModelName = AnnotatedValue("brokenTest", "DestroyedModel", group_type=GroupType.SECONDARY)
        self.breakEffect = AnnotatedValue("", "BreakEffect", group_type=GroupType.SECONDARY)
        self.blastWavePrototypeId = -1
        self.blastWavePrototypeName = AnnotatedValue("", "BlastWave", group_type=GroupType.SECONDARY)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            destroyable = read_from_xml_node(xmlNode, self.destroyable.name)
            if destroyable is not None:
                self.destroyable.value = int(destroyable)

            criticalHitEnergy = read_from_xml_node(xmlNode, self.criticalHitEnergy.name)
            if criticalHitEnergy is not None:
                self.criticalHitEnergy.value = float(criticalHitEnergy)

            self.effectType.value = safe_check_and_set(self.effectType.default_value, xmlNode, self.effectType.name)
            self.destroyEffectType.value = safe_check_and_set(self.destroyEffectType.default_value, xmlNode,
                                                              self.destroyEffectType.name)
            self.brokenModelName.value = safe_check_and_set(self.brokenModelName.default_value, xmlNode,
                                                            self.brokenModelName.name)
            self.destroyedModelName.value = safe_check_and_set(self.destroyedModelName.default_value, xmlNode,
                                                               self.destroyedModelName.name)
            self.breakEffect.value = safe_check_and_set(self.breakEffect.default_value, xmlNode, self.breakEffect.name)
            self.blastWavePrototypeName.value = safe_check_and_set(self.blastWavePrototypeName.default_value, xmlNode,
                                                                   self.blastWavePrototypeName.name)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.blastWavePrototypeName.value:
            self.blastWavePrototypeId = prototype_manager.GetPrototypeId(self.blastWavePrototypeName.value)


class ParticleSplinterPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)


class VehicleSplinterPrototypeInfo(DummyObjectPrototypeInfo):
    def __init__(self, server):
        DummyObjectPrototypeInfo.__init__(self, server)


class PhysicUnitPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.walkSpeed = AnnotatedValue(1.0, "WalkSpeed", group_type=GroupType.SECONDARY)
        self.turnSpeed = AnnotatedValue(1.0, "MaxStandTime", group_type=GroupType.SECONDARY)
        self.maxStandTime = AnnotatedValue(1.0, "TurnSpeed", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("FROM_MODEL")
            walkSpeed = read_from_xml_node(xmlNode, self.walkSpeed.name, do_not_warn=True)
            if walkSpeed is not None:
                self.walkSpeed.value = float(walkSpeed)

            maxStandTime = read_from_xml_node(xmlNode, self.maxStandTime.name, do_not_warn=True)
            if maxStandTime is not None:
                self.maxStandTime.value = float(maxStandTime)

            turnSpeed = read_from_xml_node(xmlNode, self.turnSpeed.name, do_not_warn=True)
            if turnSpeed is not None:
                self.turnSpeed.value = float(turnSpeed)
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
        self.brokenModel = AnnotatedValue("", "BrokenModel", group_type=GroupType.PRIMARY)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = SimplePhysicObjPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            self.SetGeomType("BOX")
            self.brokenModel.value = read_from_xml_node(xmlNode, "BrokenModel")
            return STATUS_SUCCESS


class ObjPrefabPrototypeInfo(SimplePhysicObjPrototypeInfo):
    def __init__(self, server):
        SimplePhysicObjPrototypeInfo.__init__(self, server)
        self.objInfos = AnnotatedValue([], "ObjInfos", group_type=GroupType.SECONDARY, saving_type=SavingType.SPECIFIC)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)

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
                        logger.error(f"Invalid object info in {SimplePhysicObjPrototypeInfo.prototypeName.value}")
                    self.objInfos.value.append(obj_info)
            else:
                logger.error(f"Missing ObjectsInfo in {SimplePhysicObjPrototypeInfo.prototypeName.value}")
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.objInfos.value:
            for objInfo in self.objInfos.value:
                objInfo.prototypeId = prototype_manager.GetPrototypeId(objInfo.prototypeName)

    def get_etree_prototype(self):
        result = SimplePhysicObjPrototypeInfo.get_etree_prototype(self)

        def prepare_objInfosElement(objInfos):
            objInfosElement = etree.Element(objInfos.name)
            for objInfoItem in objInfos.value:
                objInfosElement.append(self.ObjInfo.get_etree_prototype(objInfoItem))
            return objInfosElement
        add_value_to_node_as_child(result, self.objInfos, lambda x: prepare_objInfosElement(x))
        return result

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

        def get_etree_prototype(self):
            objInfo_node = etree.Element("ObjInfo")
            objInfo_node.set("Prototype", str(self.prototypeName))
            objInfo_node.set("RelPos", vector_to_string(self.relPos))
            objInfo_node.set("RelRot", vector_long_to_string(self.relRot))
            objInfo_node.set("ModelName", str(self.modelName))
            objInfo_node.set("Scale", str(self.scale))
            return objInfo_node


class BarricadePrototypeInfo(ObjPrefabPrototypeInfo):
    def __init__(self, server):
        ObjPrefabPrototypeInfo.__init__(self, server)
        self.objInfos = AnnotatedValue([], "ObjInfos", group_type=GroupType.PRIMARY, saving_type=SavingType.SPECIFIC)
        self.probability = AnnotatedValue(1.0, "Probability", group_type=GroupType.PRIMARY)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = ObjPrefabPrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            probability = read_from_xml_node(xmlNode, "Probability")
            if probability is not None:
                self.probability.value = float(probability)
            return STATUS_SUCCESS

    def InternalCopyFrom(self, prot_to_copy_from):
        self.parent = prot_to_copy_from


class NpcPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.isUpdating = AnnotatedValue(False, "IsUpdating", group_type=GroupType.SECONDARY)


class RepositoryObjectsGeneratorPrototypeInfo(PrototypeInfo):
    def __init__(self, server):
        PrototypeInfo.__init__(self, server)
        self.objectDescriptions = AnnotatedValue([], "Objects", group_type=GroupType.SECONDARY,
                                                 saving_type=SavingType.SPECIFIC)

    def LoadFromXML(self, xmlFile, xmlNode):
        result = PrototypeInfo.LoadFromXML(self, xmlFile, xmlNode)
        if result == STATUS_SUCCESS:
            objects = child_from_xml_node(xmlNode, "Object")
            for object_node in objects:
                newDescription = self.ObjectDescription()
                newDescription.prototypeName = safe_check_and_set("", object_node, "PrototypeName")
                newDescription.prototypeId = -1
                self.objectDescriptions.value.append(newDescription)
            return STATUS_SUCCESS

    def PostLoad(self, prototype_manager):
        if self.objectDescriptions.value:
            for obj_description in self.objectDescriptions.value:
                obj_description.prototypeId = prototype_manager.GetPrototypeId(obj_description.prototypeName)
                if obj_description.prototypeId == -1:
                    logger.error(f"Unknown Object prototype: '{obj_description.prototypeName.value}' "
                                 f"for RepositoryObjectsGenerator: '{self.prototypeName.value}'")

    def get_etree_prototype(self):
        result = PrototypeInfo.get_etree_prototype(self)
        if self.objectDescriptions.value != self.objectDescriptions.default_value:
            for objectItem in self.objectDescriptions.value:
                result.append(self.ObjectDescription.get_etree_prototype(objectItem))
        return result

    class ObjectDescription(object):
        def __init__(self):
            self.prototypeName = ""
            self.prototypeId = -1

        def get_etree_prototype(self):
            object_node = etree.Element("Object")
            object_node.set("PrototypeName", str(self.prototypeName))
            return object_node


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
    "StaticAutoGun": StaticAutoGunPrototypeInfo,
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
