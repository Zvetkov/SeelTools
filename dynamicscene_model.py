import sys

from warnings import warn
from lxml import objectify
from timeit import default_timer as timer

from em_parse import (xml_to_dict, xml_to_objfy, objfy_to_dict,
                      parse_clans_to_native, parse_belong_faction_to_dict,
                      parse_logos_gam, obj_to_simple_dict)

from em_file_ops import save_to_file

from em_classes import (GenericLocationClass, WorldGameObject,
                        ClanClass, TownClass, PlayerClass, NpcCLass,
                        VehicleClass, VehicleSoldClass, VehicleSpawnableClass,
                        VehiclePartClass, AutoGunClass, AutoGunCannonClass,
                        InfectionZoneClass, HumanClass, ChestClass,
                        LiveCaravanManagerClass, BarricadeClass, CableClass,
                        BossClass)

from constants import (GLOBAL_PROP_XML, GAME_OBJECTS_XML, DYNAMIC_SCENE_XML,
                       RESOURCE_TYPES_XML, OBJECT_NAMES_XML, OBJECT_DESCR_XML,
                       MODEL_ICONS_XML, MODEL_NAMES_XML,
                       CLANDIZ_XML, RELATIONSHIP_XML, BELONG_LOGO_XML, LOGOS_GAM,
                       DIALOGS_GLOBAL_XML, RADIO_SOUNDS_XML,
                       TOWNS_XML, VEHICLE_PARTS_XML, VEHICLES_XML, GUNS_XML_DICT,
                       PREFABS_XML, BREAKABLE_OBJ_XML, MISC_XML, BOSSES_XML)

from global_properties import theServer


def main():
    start = timer()

    server = theServer

    # global properties
    global_prop_tree = xml_to_objfy(GLOBAL_PROP_XML)
    game_objects_tree = xml_to_objfy(GAME_OBJECTS_XML)
    resource_types_tree = xml_to_objfy(RESOURCE_TYPES_XML)

    towns_tree = xml_to_objfy(TOWNS_XML)
    breakable_obj_tree = xml_to_objfy(BREAKABLE_OBJ_XML)
    misc_tree = xml_to_objfy(MISC_XML)
    prefabs_tree = xml_to_objfy(PREFABS_XML)
    vehicle_parts_tree = xml_to_objfy(VEHICLE_PARTS_XML)
    vehicles_tree = xml_to_objfy(VEHICLES_XML)
    bosses_tree = xml_to_objfy(BOSSES_XML)

    # creating dictionaries
    object_desc_dict = xml_to_dict(OBJECT_DESCR_XML)
    object_names_dict = xml_to_dict(OBJECT_NAMES_XML)
    model_icons_dict = xml_to_dict(MODEL_ICONS_XML)
    model_names_dict = xml_to_dict(MODEL_NAMES_XML)
    clan_desc_dict = xml_to_dict(CLANDIZ_XML)
    relationship_dict = xml_to_dict(RELATIONSHIP_XML)
    belong_logo_dict = xml_to_dict(BELONG_LOGO_XML)
    dialogs_global_dict = xml_to_dict(DIALOGS_GLOBAL_XML)
    belong_faction_dict = parse_belong_faction_to_dict(RADIO_SOUNDS_XML)

    # radio_sound_dict["farmers"]["Neutral"]["first_see_other"]["samples"]
    radio_sound_dict = xml_to_dict(RADIO_SOUNDS_XML)

    # creating dict of gun_size:{gun_type:obj(gun_prototype)} # ex: big_guns->{Prot_BulletLauncher}->obj(vulcan01)
    guns_dict = {gun_type: xml_to_objfy(GUNS_XML_DICT[gun_type]) for gun_type in GUNS_XML_DICT.keys()}
    # creating dict of gun_prot_name:gun_type # ex: hornet01:BulletLaucher
    guns_proto_dict = {}
    for gun_type in guns_dict.keys():
        # print(f"\nstarting to work on {gun_type}")
        guns_proto_dict.update(obj_to_simple_dict(guns_dict[gun_type], "Name", "Class"))

    # gam manipulation
    logos_list = parse_logos_gam(LOGOS_GAM)

    # prot dicts - need to (maybe) simplify and use objfy_to_dict instead
    # we can add "list" key to all dicts containing keys of dict, to not call .keys() more than once ???
    auto_guns_dict = {el.attrib["Name"]: el for el in game_objects_tree["Dir_StaticAutoGuns"]["Prototype"]}
    big_towns_dict = {el.attrib["Name"]: el for el in towns_tree["Dir_BigTowns"]["Prototype"]}
    villages_dict = {el.attrib["Name"]: el for el in towns_tree["Dir_Villages"]["Prototype"]}
    barricades_dict = {el.attrib["Name"]: el for el in prefabs_tree["Prot_Barricade"]}
    humans_dict = {el.attrib["Name"]: el for el in breakable_obj_tree['Prot_PhysicUnit']}
    breakables_dict = {el.attrib["Name"]: el for el in breakable_obj_tree['Prot_BreakableObject']}
    cables_dict = {el.attrib["Name"]: el for el in breakable_obj_tree['Prot_RopeObj']}
    vehicles_dict = {el.attrib["Name"]: el for el in vehicles_tree["Prot_Vehicle"]}
    lights_dict = {el.attrib["Name"]: el for el in misc_tree["Prot_LightObj"]}
    bosses_list = [boss.attrib["Name"].lower() for boss in resource_types_tree["Type_BOSS"].iterchildren()]

    lists = {"bosses": bosses_list}

    # grouping structs to simplify arguments for native object creation
    structs = {'global_prop': global_prop_tree,
               'game_objects': game_objects_tree,
               'vehicles': vehicles_tree,
               'vehicle_parts': vehicle_parts_tree,
               'towns': towns_tree,
               'prefabs': prefabs_tree,
               'breakable_obj': breakable_obj_tree}

    dicts = {'clan_desc': clan_desc_dict,
             'belong_logo': belong_logo_dict,
             'belong_faction': belong_faction_dict,
             'relationship': relationship_dict,
             'object_desc': object_desc_dict,
             'object_names': object_names_dict,
             'model_icons': model_icons_dict,
             'model_names': model_names_dict,
             'dialogs_global': dialogs_global_dict,
             'logos_list': logos_list,  # logos_list is not a dict by has the same purpose
             'auto_guns': auto_guns_dict,
             'big_towns': big_towns_dict,
             'villages': villages_dict,
             'barricades': barricades_dict,
             'humans': humans_dict,
             'breakables': breakables_dict,
             'cables': cables_dict,
             'vehicles': vehicles_dict,
             'lights': lights_dict,
             'lists': lists}

    # creating native class object tree for dynamicscene
    structs['clan'] = parse_clans_to_native(structs, dicts)

    # creating dynamicscene objectify trees
    dynamic_scene_tree = xml_to_objfy(DYNAMIC_SCENE_XML)

    object_tree = parse_dynamicscene(dynamic_scene_tree, structs, dicts)
    end = timer()
    print('total time: ', end - start)

    sizes = [(len(object_tree[key]), key) for key in object_tree.keys()]
    sizes.sort(reverse=True)
    for v, k in sizes:
        print(f"{v}: {k} size")

    print(object_tree)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_XML)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)


def parse_dynamicscene(objfy_tree: objectify.ObjectifiedElement,
                       structs: dict, dicts: dict):
    ''' Returns dictionary of objects grouped by type
    '''
    tree = {}
    tree["big_towns"] = {}
    tree["villages"] = {}
    tree["unsorted"] = []
    tree["suspect_error"] = []
    big_towns = dicts["big_towns"].keys()
    villages = dicts["villages"].keys()

    simple_class_dict = {"player": PlayerClass,
                         "genericLocation": GenericLocationClass,
                         "InfectionZone": InfectionZoneClass,
                         "someChest": ChestClass,
                         "LiveCaravanManager": LiveCaravanManagerClass
                         }
    simple_classes_names = simple_class_dict.keys()
    for name in simple_classes_names:
        tree[name] = {}

    simple_multi_prot_dict = {}
    for barricade in dicts["barricades"].keys():
        simple_multi_prot_dict[barricade] = BarricadeClass
    for human in dicts["humans"].keys():
        simple_multi_prot_dict[human] = HumanClass
    for breakable in dicts["breakables"].keys():
        simple_multi_prot_dict[breakable] = WorldGameObject
    for cable in dicts["cables"].keys():
        simple_multi_prot_dict[cable] = CableClass
    for light in dicts["lights"].keys():
        simple_multi_prot_dict[light] = WorldGameObject
    for boss in dicts["lists"]["bosses"]:
        simple_multi_prot_dict[boss] = BossClass
    simple_multi_prot_names = simple_multi_prot_dict.keys()
    tree["HumanClass"] = []
    tree["BarricadeClass"] = []
    tree["WorldGameObject"] = []
    tree["CableClass"] = []
    tree["BossClass"] = []

    for obj in objfy_tree.iterchildren():
        # named targets for dynamic quest-hunts
        if obj.tag == "TargetNamesForDestroy":
            tree['TargetNamesForDestroy'] = obj.attrib
        # generic locations, player, infection zones, chests
        elif obj.tag in simple_classes_names:
            obj_name = obj.attrib.get('Name')
            if obj_name is None:
                if tree[obj.tag].get("MISSING_NAME") is None:
                    tree[obj.tag]["MISSING_NAME"] = []
                tree[obj.tag]["MISSING_NAME"].append(simple_class_dict[obj.tag](obj, dicts))
            else:
                tree[obj.tag][obj_name] = simple_class_dict[obj.tag](obj, dicts)
        # humans, breakables
        elif obj.tag in simple_multi_prot_names:
            obj_class = simple_multi_prot_dict[obj.tag]
            obj_name = obj.attrib.get('Name')
            tree[obj_class.__name__].append(obj_class(obj, dicts))
        # towns and villages
        elif obj.tag in big_towns:
            tree["big_towns"][obj.tag] = TownClass(obj, dicts)
        elif obj.tag in villages:
            tree["villages"][obj.tag] = TownClass(obj, dicts)
        elif obj.tag == "settlementTeam":
            warn("settlementTeam element found in root")
            tree["suspect_error"].append(obj)
        else:
            tree["unsorted"].append(obj)

    return tree


if __name__ == "__main__":
    sys.exit(main())
