from base_classes import PhysicObj
from warnings import warn


class SimplePhysicObj(PhysicObj):
    '''Single physical object'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        PhysicObj.__init__(self, name, prototype, belong,
                           position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Settlement(SimplePhysicObj):
    '''Base class for settlements: lairs, towns, infections lairs'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        SimplePhysicObj.__init__(self, name, prototype, belong,
                                 position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Town(Settlement):
    '''Game town and village class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Settlement.__init__(self, name, prototype, belong,
                            position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Lair(Settlement):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Settlement.__init__(self, name, prototype, belong,
                            position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class InfectionLair(Settlement):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Settlement.__init__(self, name, prototype, belong,
                            position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class ObjPrefab(SimplePhysicObj):
    '''Base class for prefabs'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        SimplePhysicObj.__init__(self, name, prototype, belong,
                                 position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Barricade(ObjPrefab):
    '''Stationary barricade with weapon controled by AI'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ObjPrefab.__init__(self, name, prototype, belong,
                           position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Shell(SimplePhysicObj):
    '''Base class for shell projectiles used by guns'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        SimplePhysicObj.__init__(self, name, prototype, belong,
                                 position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Bullet(Shell):
    '''Bullet shell class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Shell.__init__(self, name, prototype, belong,
                       position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class MortarShell(Shell):
    '''Mortar projectile shell class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Shell.__init__(self, name, prototype, belong,
                       position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class PlasmaBunch(Shell):
    '''Plasma projectile shell class used by plasma launchers'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Shell.__init__(self, name, prototype, belong,
                       position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Rocket(Shell):
    '''Rocket shell class used by rocket launchers'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Shell.__init__(self, name, prototype, belong,
                       position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Mine(Rocket):
    '''Mine "shell" class used by mine pushers'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        Shell.__init__(self, name, prototype, belong,
                       position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class ComplexPhysicObj(PhysicObj):
    '''Physic object that can be composed of multiple parts'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        PhysicObj.__init__(self, name, prototype, belong,
                           position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


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


class Boss04(ComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Boss04Drone(ComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Boss04Station(ComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class AnimatedComplexPhysicObj(ComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class Boss03(AnimatedComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        AnimatedComplexPhysicObj.__init__(self, name, prototype, belong,
                                          position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass


class StaticAutoGun(ComplexPhysicObj):
    '''???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int):
        ComplexPhysicObj.__init__(self, name, prototype, belong,
                                  position, rotation, skin)
        warn(f"Not implemented class {self.__name__}")
        pass
