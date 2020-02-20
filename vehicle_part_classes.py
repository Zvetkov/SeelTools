from base_classes import VehiclePart


class Chassis(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        # "class"
        self.part_class
        self.resource_type
        self.model_file
        self.node_scale
        self.price
        self.repair_coef
        self.mass
        self.durability
        self.max_health
        self.max_fuel

        self.visible_in_encyclopedia

        self.braking_sound
        self.pneumo_sound
        self.gear_shift_sound
        self.load_points
        self.group_health = {
            "main": 0
        }


class Basket(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class Cabin(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class CompoundVehiclePart(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class Boss03Part(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class Boss04Part(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class Boss04StationPart(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        pass


class CompoundGun(CompoundVehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        CompoundVehiclePart.__init__(self, name, prototype, belong,
                                     position, rotation, skin, logo)
        pass
