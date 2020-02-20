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
                 belong: int = 1000, flags: int = 17,  # what is this magic 17 ???
                 parent_repository: GeomRepository = None):
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
        # resource_id ???


class Player(Obj):
    '''Player class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 money: int, vehicle: Vehicle = None):
        Obj.__init__(self, name, prototype)
        self.money = money
        self.vehicle = vehicle
        # self.model_name
        # self.skin_number
        # self.cfg_number


class PhysicObj(Obj):
    '''Base class for Obj that can be spawned in game worls'''
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


class VehiclePart(PhysicBody):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        PhysicBody.__init__(self, name, prototype, belong,
                            position, rotation, skin, logo)
        warn(f"Not implemented class {self.__name__}")
        pass


class Npc(Obj):
    '''Npc class used in buildings and in dialogs'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Team(Obj):
    '''AI team base class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class CaravanTeam(Team):
    '''AI team used for caravans'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Team.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class InfectionTeam(Team):
    '''AI team used for spawned cars'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Team.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class VagabondTeam(Team):
    '''AI team used for ???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Team.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Trigger(Obj):
    '''Game trigger logic class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Building(Obj):
    '''Buildings base class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Workshop(Building):
    '''Workshop class used for shops and workshops'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Building.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Bar(Building):
    '''Bar class used for bars with and without barman'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Building.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Formation(Obj):
    '''Formation of vehicles or baricades'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


class Gadget(Obj):
    '''Gadget used to equip a vehicle'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Obj.__init__(self, name, prototype, belong)
        warn(f"Not implemented class {self.__name__}")
        pass


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
