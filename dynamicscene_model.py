import sys

from lxml import objectify
from timeit import default_timer as timer

from em_parse import (xml_to_dict, xml_to_objfy,
                      parse_clans_to_native, parse_belong_faction_to_dict,
                      parse_logos_gam)

from em_file_ops import save_to_file

from em_classes import (GenericLocationClass,
                        ClanClass, TownClass, PlayerClass, NpcCLass,
                        VehicleClass, VehicleSoldClass, VehicleSpawnableClass,
                        VehiclePartClass, AutoGunClass, AutoGunCannonClass)

from constants import (OBJECT_NAMES_XML, OBJECT_DESCR_XML,
                       MODEL_ICONS_XML, MODEL_NAMES_XML,
                       CLANDIZ_XML, RELATIONSHIP_XML, BELONG_LOGO_XML, LOGOS_GAM,
                       DIALOGS_GLOBAL_XML, RADIO_SOUNDS_XML,
                       GLOBAL_PROP_XML, GAME_OBJECTS_XML,
                       TOWNS_XML, VEHICLE_PARTS_XML, VEHICLES_XML,
                       DYNAMIC_SCENE_XML)


def main():
    start = timer()

    # creating dictionaries
    object_names_dict = xml_to_dict(OBJECT_NAMES_XML)
    object_desc_dict = xml_to_dict(OBJECT_DESCR_XML)
    model_icons_dict = xml_to_dict(MODEL_ICONS_XML)
    model_names_dict = xml_to_dict(MODEL_NAMES_XML)
    clan_desc_dict = xml_to_dict(CLANDIZ_XML)
    relationship_dict = xml_to_dict(RELATIONSHIP_XML)
    belong_logo_dict = xml_to_dict(BELONG_LOGO_XML)
    dialogs_global_dict = xml_to_dict(DIALOGS_GLOBAL_XML)
    belong_faction_dict = parse_belong_faction_to_dict(RADIO_SOUNDS_XML)

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

    # creating native class object tree for dynamicscene
    clan_tree = parse_clans_to_native(global_prop_tree, clan_desc_dict,
                                      relationship_dict, model_icons_dict,
                                      belong_logo_dict, logos_list,
                                      belong_faction_dict)

    # creating dynamicscene objectify trees
    dynamic_scene_tree = xml_to_objfy(DYNAMIC_SCENE_XML)

    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)

    object_tree = parse_dynamicscene(dynamic_scene_tree,
                                     game_objects_tree,
                                     vehicles_tree,
                                     vehicle_parts_tree,
                                     towns_tree,
                                     object_names_dict,
                                     object_desc_dict,
                                     model_icons_dict,
                                     model_names_dict,
                                     clan_tree,
                                     dialogs_global_dict)
    end = timer()
    print('total time: ', end - start)
    print(object_tree)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_XML)


def parse_dynamicscene(objfy_tree: objectify.ObjectifiedElement,
                       game_objects_tree: objectify.ObjectifiedElement,
                       vehicles_tree: objectify.ObjectifiedElement,
                       vehicle_parts_tree: objectify.ObjectifiedElement,
                       towns_tree: objectify.ObjectifiedElement,
                       object_names_dict: dict,
                       object_desc_dict: dict,
                       model_icons_dict: dict,
                       model_names_dict: dict,
                       clan_tree: dict,
                       dialogs_global_dict: dict):
    ''' Returns dictionary of objects grouped by type
    '''
    tree = {}
    vehicles_proto_dict = {proto.attrib["Name"]: proto for proto in vehicles_tree["Prot_Vehicle"]}
    # player
    if hasattr(objfy_tree, "Obj_player"):
        tree["player"] = PlayerClass(objfy_tree["Obj_player"], vehicles_proto_dict, model_names_dict)

    # towns and villages
    big_towns = [el.attrib["Name"] for el in towns_tree["Dir_BigTowns"]["Prototype"]]
    villages = [el.attrib["Name"] for el in towns_tree["Dir_Villages"]["Prototype"]]
    tree["big_towns"] = []
    tree["villages"] = []
    for town in big_towns:
        if hasattr(objfy_tree, f"Obj_{town}"):
            # need to add info from towns.xml - gameobjects.xml
            tree["big_towns"].append(TownClass(objfy_tree[f"Obj_{town}"],
                                     game_objects_tree,
                                     object_names_dict,
                                     object_desc_dict,
                                     model_icons_dict,
                                     model_names_dict,
                                     clan_tree,
                                     dialogs_global_dict))

    for village in villages:
        if hasattr(objfy_tree, f"Obj_{village}"):
            # need to add info from towns.xml - gameobjects.xml
            tree["villages"].append(TownClass(objfy_tree[f"Obj_{village}"],
                                    game_objects_tree,
                                    object_names_dict,
                                    object_desc_dict,
                                    model_icons_dict,
                                    model_names_dict,
                                    clan_tree,
                                    dialogs_global_dict))

    # generic locations
    if hasattr(objfy_tree, "Obj_genericLocation"):
        tree["generic_locations"] = [GenericLocationClass(generic_loc, dialogs_global_dict)
                                     for generic_loc in objfy_tree["Obj_genericLocation"]]

    return tree


if __name__ == "__main__":
    sys.exit(main())
