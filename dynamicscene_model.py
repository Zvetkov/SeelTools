import sys

from lxml import objectify
from timeit import default_timer as timer

from em_parse import (xml_to_dict, xml_to_objfy,
                      parse_clans_to_native, parse_belong_faction_to_dict,
                      parse_logos_gam, obj_to_simple_dict)

from em_file_ops import save_to_file

from em_classes import (GenericLocationClass,
                        ClanClass, TownClass, PlayerClass, NpcCLass,
                        VehicleClass, VehicleSoldClass, VehicleSpawnableClass,
                        VehiclePartClass, AutoGunClass, AutoGunCannonClass,
                        InfectionZoneClass, HumanClass)

from constants import (GLOBAL_PROP_XML, GAME_OBJECTS_XML,
                       OBJECT_NAMES_XML, OBJECT_DESCR_XML,
                       MODEL_ICONS_XML, MODEL_NAMES_XML,
                       CLANDIZ_XML, RELATIONSHIP_XML, BELONG_LOGO_XML, LOGOS_GAM,
                       DIALOGS_GLOBAL_XML, RADIO_SOUNDS_XML,
                       TOWNS_XML, VEHICLE_PARTS_XML, VEHICLES_XML, GUNS_XML_DICT,
                       DYNAMIC_SCENE_XML)


def main():
    start = timer()

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

    # creating dict of gun_size:{gun_type:obj(gun_prototype)} # ex: big_guns->{Prot_BulletLauncher}->obj(vulcan01)
    guns_dict = {gun_type: xml_to_objfy(GUNS_XML_DICT[gun_type]) for gun_type in GUNS_XML_DICT.keys()}
    # creating dict of gun_prot_name:gun_type # ex: hornet01:BulletLaucher
    guns_proto_dict = {}
    for gun_type in guns_dict.keys():
        print(f"\nstarting to work on {gun_type}")
        guns_proto_dict.update(obj_to_simple_dict(guns_dict[gun_type], "Name", "Class"))

    # radio_sound_dict["farmers"]["Neutral"]["first_see_other"]["samples"]
    radio_sound_dict = xml_to_dict(RADIO_SOUNDS_XML)

    # gam manipulation
    logos_list = parse_logos_gam(LOGOS_GAM)

    # global properties
    global_prop_tree = xml_to_objfy(GLOBAL_PROP_XML)

    game_objects_tree = xml_to_objfy(GAME_OBJECTS_XML)

    towns_tree = xml_to_objfy(TOWNS_XML)
    vehicle_parts_tree = xml_to_objfy(VEHICLE_PARTS_XML)
    vehicles_tree = xml_to_objfy(VEHICLES_XML)
    vehicles_proto_dict = {proto.attrib["Name"]: proto for proto in vehicles_tree["Prot_Vehicle"]}

    # grouping structs to simplify arguments for native object creation
    structs = {'global_prop_tree': global_prop_tree,
               'game_objects_tree': game_objects_tree,
               'clan_desc_dict': clan_desc_dict,
               'belong_logo_dict': belong_logo_dict,
               'belong_faction_dict': belong_faction_dict,
               'relationship_dict': relationship_dict,
               'logos_list': logos_list,
               'vehicles_tree': vehicles_tree,
               'vehicle_parts_tree': vehicle_parts_tree,
               'towns_tree': towns_tree,
               'object_desc_dict': object_desc_dict,
               'object_names_dict': object_names_dict,
               'model_icons_dict': model_icons_dict,
               'model_names_dict': model_names_dict,
               'dialogs_global_dict': dialogs_global_dict}

    # creating native class object tree for dynamicscene
    structs['clan_tree'] = parse_clans_to_native(structs)

    # creating dynamicscene objectify trees
    dynamic_scene_tree = xml_to_objfy(DYNAMIC_SCENE_XML)

    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)


    # object_tree = parse_dynamicscene(dynamic_scene_tree,
    #                                  game_objects_tree,
    #                                  vehicles_tree,
    #                                  vehicle_parts_tree,
    #                                  towns_tree,
    #                                  object_desc_dict,
    #                                  model_icons_dict,
    #                                  model_names_dict,
    #                                  clan_tree,
    #                                  dialogs_global_dict)
    object_tree = parse_dynamicscene(dynamic_scene_tree, structs)
    end = timer()
    print('total time: ', end - start)
    print(object_tree)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_XML)


def parse_dynamicscene(objfy_tree: objectify.ObjectifiedElement,
                       structs: dict):
    ''' Returns dictionary of objects grouped by type
    '''
    tree = {}
    tree["big_towns"] = {}
    tree["villages"] = {}

    tree["unsorted"] = []

    simple_class_dict = {"player": PlayerClass,
                         "genericLocation": GenericLocationClass,
                         "InfectionZone": InfectionZoneClass,
                         "Human": HumanClass}
    simple_classes_names = simple_class_dict.keys()
    for name in simple_classes_names:
        tree[name] = {}
        tree[name]["MISSING_NAME"] = []

    big_towns = [el.attrib["Name"] for el in structs['towns_tree']["Dir_BigTowns"]["Prototype"]]
    villages = [el.attrib["Name"] for el in structs['towns_tree']["Dir_Villages"]["Prototype"]]

    for obj in objfy_tree.iterchildren():
        # named targets for dynamic quest-hunts
        if obj.tag == "TargetNamesForDestroy":
            tree['TargetNamesForDestroy'] = obj.attrib
        # generic locations, player, infection zones, humans
        elif obj.tag in simple_classes_names:
            obj_name = obj.attrib.get('Name')
            if obj_name is None:
                tree[obj.tag]["MISSING_NAME"].append(simple_class_dict[obj.tag](obj, structs))
            else:
                tree[obj.tag][obj_name] = simple_class_dict[obj.tag](obj, structs)
        # towns and villages
        elif obj.tag in big_towns:
            tree["big_towns"][obj] = TownClass(obj, structs)
        elif obj.tag in villages:
            tree["villages"][obj] = TownClass(obj, structs)
        else:
            tree["unsorted"].append(obj)

    return tree


if __name__ == "__main__":
    sys.exit(main())
