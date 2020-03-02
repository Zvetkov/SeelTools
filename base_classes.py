# import os
from warnings import warn
# from lxml import objectify


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
                 money: int,
                 model_name: str,  # xmlNode, "ModelFile"
                 skin_number: int = 0, cfg_number: int = 0,
                 vehicle: Vehicle = None):
        Obj.__init__(self, name, prototype)
        self.money = money
        self.vehicle = vehicle
        self.model_name = model_name
        self.skin_number = skin_number
        self.cfg_number = cfg_number


class PhysicObj(Obj):
    '''Base class for Obj that can be spawned in game worls'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int,
                 intersection_radius: float = 0.0,
                 look_radius: float = 0.0):
        Obj.__init__(self, name, prototype, belong)
        self.intersection_radius = intersection_radius
        self.look_radius = look_radius
        self.position = position
        self.rotation = rotation
        self.skin = skin  # ??? might be optional


class PhysicBody(Obj):
    '''Base class for VehiclePart and SimplePhysicBody'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 engine_model_name,  # "ModelFile" xml tag
                 mass_value: float = 1.0, collision_infos: list = []):
        Obj.__init__(self, name, prototype, belong)
        self.engine_model_name = engine_model_name
        self.mass_value = mass_value
        self.collision_infos = collision_infos
        self.position = position
        self.rotation = rotation
        self.skin = skin
        self.logo = logo


class Npc(Obj):
    '''Npc class used in buildings and in dialogs'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 model_name: str, npc_type: int = 1, skin_number: int = 0,
                 cfg_number: int = 0, hello_reply_names: list = [],
                 spoken_count: int = 0):
        Obj.__init__(self, name, prototype, belong)
        self.npc_type = npc_type
        self.model_name = model_name
        self.skin_number = skin_number
        self.cfg_number = cfg_number
        self.hello_reply_names = hello_reply_names
        self.spoken_count = spoken_count


class Team(Obj):
    '''AI team base class'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 vehicles: list = [], formation: int = 0,
                 decision_matrix_num: int = -1,
                 formation_prototype_name: str = "TEAM_DEFAULT_FORMATION_PROTOTYPE",
                 overrides_dist_between_vehicles: bool = False,
                 formation_dist_between_vehicles: float = 30.0,
                 ):
        Obj.__init__(self, name, prototype, belong)
        self.decision_matrix_num = decision_matrix_num
        self.formation_prototype_name = formation_prototype_name
        self.overrides_dist_between_vehicles = overrides_dist_between_vehicles
        self.formation_dist_between_vehicles = formation_dist_between_vehicles
        self.vehicles = vehicles
        self.formation = formation  # ??? enum would be more usefull


class CaravanTeam(Team):
    '''AI team used for caravans'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 traders_generator_prot_name: str,  # xmlNode, "TradersVehiclesGeneratorName
                 guards_generator_prot_name: str,  # xmlNode, "GuardVehiclesGeneratorName"
                 guard_vehicles: list = [],
                 wares_prototypes: list = []):
        Team.__init__(self, name, prototype, belong)
        self.traders_generator_prot_name = traders_generator_prot_name
        self.guards_generator_prot_name = guards_generator_prot_name
        self.wares_prototypes = wares_prototypes
        self.guard_vehicles = guard_vehicles


class InfectionTeam(Team):
    '''AI team used for spawned cars'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 vehicles_generator_proto_name: str,  # xmlNode, "VehiclesGenerator"
                 items: list = [], critical_team_dist: float = 1000000.0,
                 critical_team_time: float = 0.0,
                 time_beyond_critical_dist: float = 0.0,
                 blind_team_dist: float = 1000000.0,
                 blind_team_time: float = 0.0,
                 time_beyond_blind_dist: float = 0.0):
        Team.__init__(self, name, prototype, belong)
        self.items = items
        self.vehicles_generator_proto_name = vehicles_generator_proto_name
        self.critical_team_dist = critical_team_dist
        self.critical_team_time = critical_team_time
        self.time_beyond_critical_dist = time_beyond_critical_dist
        self.blind_team_dist = blind_team_dist
        self.blind_team_time = blind_team_time
        self.time_beyond_blind_dist = time_beyond_blind_dist


class VagabondTeam(Team):
    '''AI team used for ???'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 vehicles_generator_prototype: str,  # xmlNode, "VehicleGeneratorPrototype"
                 wares_prototypes: list = []):
        Team.__init__(self, name, prototype, belong)
        self.vehicles_generator_prototype = vehicles_generator_prototype
        self.wares_prototypes = wares_prototypes


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
                 position: str, rotation: str, skin: int, logo: int,
                 building_type: int = 5, npcs: list = []):
        Obj.__init__(self, name, prototype, belong)
        self.building_type = building_type
        self.npcs = npcs


class Workshop(Building):
    '''Workshop class used for shops and workshops'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 repositories: list = [], articles: list = [],
                 original_objects_in_repository: list = [],
                 price_coeff_provider: int = 0):  # ??? or 1.0?
        Building.__init__(self, name, prototype, belong)
        self.repositories = repositories
        self.articles = articles
        self.original_objects_in_repository = original_objects_in_repository
        self.price_coeff_provider = price_coeff_provider


class Bar(Building):
    '''Bar class used for bars with and without barman'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 with_barman: float = False,
                 barman: Npc = None):
        Building.__init__(self, name, prototype, belong)
        self.with_barman = with_barman
        self.barman = barman


class Formation(Obj):
    '''Formation of vehicles or baricades'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 dist_between_vehicles: float = 30.0,
                 max_vehicles: int = 5, vehicles: list = [],
                 polyline_points: list = [],
                 polyline_length: float = 0.0,
                 head_offset: float = 0.0,
                 linear_velocity: float = 100.0,
                 head_position: int = 0,
                 angular_velocity: float = 0.5
                 ):
        Obj.__init__(self, name, prototype, belong)
        self.dist_between_vehicles = dist_between_vehicles
        self.max_vehicles = max_vehicles
        self.vehicles = vehicles
        self.polyline_points = polyline_points
        self.polyline_length = polyline_length
        self.head_offset = head_offset
        self.linear_velocity = linear_velocity
        self.head_position = head_position
        self.angular_velocity = angular_velocity


class Gadget(Obj):
    '''Gadget used to equip a vehicle'''
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int,
                 modifications: list = [],
                 model_name: list = [],
                 skin_num: int = 0):
        Obj.__init__(self, name, prototype, belong)
        self.modifications = modifications
        self.model_name = model_name
        self.skin_num = skin_num


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
