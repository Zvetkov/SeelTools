from base_classes import PhysicBody


class VehiclePart(PhysicBody):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 engine_model_name,  # "ModelFile" xml tag
                 mass_value: float = 1.0, collision_infos,
                 price: int, part_name: str, model_parts,  # ???
                 model_file: list = [],  # list of parts found by model_parts
                 node_scale: int = 1, blow_effect_name: str = "ET_PS_HARD_BLOW",
                 durability: float = 0.0, durability_coeffs: list = [0, 0, 0],
                 weapon_prototype_id: int = -1, group_health: list = [],
                 load_points: list = [], bounds_for_meshes: list = [],
                 model_meshes: list = [], repair_coef: float = 1.0,
                 can_be_used_in_autogenerating: bool = True):
        PhysicBody.__init__(self, name, prototype, belong,
                            position, rotation, skin, logo,
                            engine_model_name,  # "ModelFile" xml tag
                            mass_value, collision_infos)
        self.weapon_prototype_id = weapon_prototype_id
        self.bounds_for_meshes = bounds_for_meshes
        self.price = price
        self.part_name = part_name
        self.model_parts = model_parts
        self.group_health = group_health
        self.node_scale = node_scale
        self.load_points = load_points
        self.model_meshes = model_meshes
        self.model_file = model_file
        self.durability = durability
        self.durability_coeffs = durability_coeffs  # : "3 strs"
        self.blow_effect_name = blow_effect_name
        self.can_be_used_in_autogenerating = can_be_used_in_autogenerating
        self.repair_coef = repair_coef
        # self.collision_infos = collision_infos
        # self.verts = verts
        # self.inds = inds
        # self.nums_tris = nums_tris
        # self.verts_stride = verts_stride


class Chassis(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,

                 price: int, part_name: str, model_parts,  # ???
                 model_file: list = [],  # list of parts found by model_parts
                 node_scale: int = 1, blow_effect_name: str = "ET_PS_HARD_BLOW",
                 durability: float = 0.0, durability_coeffs: list = [0, 0, 0],
                 weapon_prototype_id: int = -1, group_health: list = [],
                 load_points: list = [], bounds_for_meshes: list = [],
                 model_meshes: list = [], repair_coef: float = 1.0,
                 can_be_used_in_autogenerating: bool = True,

                 max_health: float = 1.0, max_fuel: float = 1.0,

                 braking_sound_name: str,  # xmlNode, "BrakingSound"
                 pneumo_sound_name: str,  # xmlNode, "PneumoSound"
                 gear_shift_sound_name):  # xmlNode, "GearShiftSound"
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo,
                             engine_model_name,  # "ModelFile" xml tag
                             mass_value, collision_infos,
                             price, part_name, model_parts,
                             model_file, node_scale, blow_effect_name,
                             durability, durability_coeffs,
                             weapon_prototype_id, group_health,
                             load_points, bounds_for_meshes,
                             model_meshes, repair_coef,
                             can_be_used_in_autogenerating)
        self.max_health = max_health
        self.max_fuel = max_fuel

        self.resource_type
        self.model_file
        self.node_scale
        self.price
        self.repair_coef

        self.visible_in_encyclopedia

        self.braking_sound_name = braking_sound_name
        self.pneumo_sound_name = pneumo_sound_name
        self.gear_shift_sound_name = gear_shift_sound_name

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
