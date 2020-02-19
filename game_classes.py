import os
from warnings import warn
from lxml import objectify


class Object(object):
    '''Base class'''
    def __init__(self, name: str, prototype: str):
        self.name = name
        self.prototype = prototype
        self.tag_name = None


class Obj(Object):
    '''Base class with belong'''
    def __init__(self, name: str, prototype: str,
                 belong: int = 1000, flags: int = 17,
                 parent_repository: GeomRepository = None):  # what is this magic 17 ???
        Object.__init__(self, name, prototype)
        self.belong = belong
        self.flags = flags
        self.parent_repository = parent_repository


class GeomRepository(Object):
    '''Repository of items'''
    def __init__(self, name: str, prototype: str, belong: int,
                 size_x: int = 1, size_y: int = 1, items: list = []):
        Object.__init__(self, name, prototype)
        self.items = items
        self.size_x = size_x
        self.size_y = size_y
        # self.sort_style
        # self.vehicle


class GeomRepositoryItem(object):
    def __init__(self, origin_x: int = -1, origin_y: int = -1,
                 amount: int = 0, item_type: int = 1):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.amount = amount
        self.item_type = item_type


class Player(Obj):
    '''Player class (singleton?)'''
    def __init__(self, name: str, prototype: str, belong: int,
                 money: int, vehicle: Vehicle = None):
        Obj.__init__(self, name, prototype)
        self.money = money
        self.vehicle = vehicle
        # self.model_name
        # self.skin_number
        # self.cfg_number


class PhysicObj(Obj):
    '''Obj that can be spawned in game worls'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Obj.__init__(self, name, prototype, belong)
        self.position = position
        self.rotation = rotation
        self.skin = skin  # ??? might be optional


class PhysicBody(Obj):
    '''Base class for VehiclePart and SimplePhysicBody'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        self.position = position
        self.rotation = rotation
        self.skin = skin
        self.logo = logo


class Ware(Obj):
    '''Ware than can be sold at the shop'''
    def __init__(self, name: str, prototype: str, belong: int,
                 pos_x: int, pos_y: int, flags: int,
                 prototype_name: str, durability: int,
                 max_durability: int, price: int,
                 damage: int, firing_rate: int,
                 firing_range: int):
        Obj.__init__(self, name, prototype, belong)
        self.pos_xy = [pos_x, pos_y]
        self.flags = flags
        self.prototype_name = prototype_name


class ComplexPhysicObj(PhysicObj):
    '''Physic object that can be composed of multiple parts'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        PhysicObj.__init__(self, name, prototype, belong,
                           position, rotation, skin)
        pass  # ??? what is the difference between Complex and SimplePO


class Vehicle(ComplexPhysicObj):
    '''Vehicle that player of bots can use'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int,
                 cabin: VehiclePart, basket: VehiclePart, chassis: VehiclePart,
                 parts: VehiclePart, repository: GeomRepository):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        self.cabin = cabin
        self.basket = basket
        self.chassis = chassis
        self.parts = parts
        self.repository = repository
