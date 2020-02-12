import os
from warnings import warn
from lxml import objectify


# Base class
class Object(object):
    def create(self, name: str, prototype: str):
        self.name = name
        self.prototype = prototype
        self.tag_name = None

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        self.prototype = element.attrib["Prototype"]
        self.tag_name = element.tag
        self.name = element.attrib.get("Name")
        if self.name is None:
            self.name = "OBJECT_MISSING_NAME"


# Base class with belong
class Obj(Object):
    def create(self, name: str, prototype: str, belong: int):
        Object.create(self, name, prototype)
        self.belong = str(belong)

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        Object.parse_obj(self, element, dicts)
        self.belong = element.attrib.get("Belong")  # not required, example chests on r1m2


class GeomRepository(Object):
    def create(self, name: str, prototype: str, belong: int,
               items: list):
        Object.create(self, name, prototype)
        self.items = items

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        Object.parse_obj(self, element, dicts)
        if element["Repository"].attrib:
            self.items = [Ware(part_element, dicts)
                          for part_element in element["Repository"]["Item"]]


class PhysicObj(Obj):
    def create(self, name: str, prototype: str, belong: int,
               position: str, rotation: str, skin: int):
        Obj.create(self, name, prototype, belong)
        self.position = position
        self.rotation = rotation
        self.skin = skin  # ??? might be optional

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        Obj.parse_obj(self, element, dicts)
        self.position = element.attrib["Pos"]  # "1263.873 308.000 2962.220"
        self.rotation = element.attrib.get("Rot")  # "0.000 -0.721 0.000 -0.693"


class Ware(Obj):
    def create(self, name: str, prototype: str, belong: int,
               pos_x: int, pos_y: int, flags: int,
               prototype: str, prototype_name: str):
        Obj.create(self, name, prototype, belong)
        self.pos_xy = [pos_x, pos_y]
        self.flags = flags
        self.prototype = prototype
        self.prototype_name = prototype_name

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        Obj.parse_obj(self, element, dicts)
        self.pos_xy = [element.attrib["PosX"], element.attrib["PosY"]]  # [0, 0]
        self.flags = element.attrib.get("Flags")  # 16 # ??? is this class really working if missing? example: zoo.ssl
        self.prototype = element.attrib["Prototype"]  # "bugCargo02"
        self.prototype_name = dicts['model_names'][self.prototype]['value']

        # zoo attribs unused in main game
        self.durability = element.attrib.get("Durability")  # ??? check that it works as exoected, only available on zoo
        self.max_durability = element.attrib.get("MaxDurability")  # ??? same as durability
        self.price = element.attrib.get("Price")  # ??? same as durability
        self.damage = element.attrib.get("Damage")  # ??? same as durability
        self.firing_rate = element.attrib.get("FiringRate")  # ??? same as durability
        self.firing_range = element.attrib.get("FiringRange")  # ??? same as durability


class ComplexPhysicObj(PhysicObj):
    def create(self, name: str, prototype: str, belong: int,
               position: str, rotation: str, skin: int):
        PhysicObj.create(self, name, prototype, belong,
                         position, rotation, skin)
        pass  # ??? what is the difference between Complex and SimplePO

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        PhysicObj.parse_obj(self, element, dicts)
        pass  # ??? what is the difference between Complex and SimplePO


class Vehicle(ComplexPhysicObj):
    def create(self, name: str, prototype: str, belong: int,
               position: str, rotation: str, skin: int,
               cabin: VehiclePart, basket: VehiclePart, chassis: VehiclePart,
               parts: VehiclePart, repository: GeomRepository):
        pass

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        self.cabin = None
        self.basket = None
        self.chassis = None
        self.parts = {}
        for part in element["Parts"].iterchildren():
            if part.tag == "CABIN":
                self.cabin = VehiclePartClass(part, dicts)
            elif part.tag == "BASKET":
                self.basket = VehiclePartClass(part, dicts)
            elif part.tag == "CHASSIS":
                self.chassis = VehiclePartClass(part, dicts)
            else:
                self.parts[part.tag] = VehiclePartClass(part, dicts)

        if element["Repository"].attrib:
            self.repository = GeomRepository().parse_obj(
                               [SoldPartClass(part_element, dicts)
                               for part_element in element["Repository"]["Item"]])
        else:
            self.repository = None


class Player(Obj):
    def __init__(self, name: str, prototype: str, belong: int,
                 money: int, vehicle: Vehicle):
        Obj.__init__(self, name, prototype)
        self.belong = str(belong)
        self.money = str(money)

    def parse_obj(self, element: objectify.ObjectifiedElement,
                  dicts: dict = {}):
        Obj.parse_obj(self, element, dicts)
        self.money = element.attrib.get("Money")
        if len(element.getchildren()) == 1:
            self.vehicle = Vehicle().parse_obj(element.getchildren()[0], dicts)
        else:
            self.vehicle = None  # r3m1 player prototype as example
