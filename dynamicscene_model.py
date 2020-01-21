import os
import sys

from chardet import detect
from lxml import etree, objectify

GAME_FOLDER = "D:/Steam/steamapps/common/Hard Truck Apocalypse"

DYNAMIC_SCENE_XML = os.path.join(GAME_FOLDER, "data", "maps", "r1m1",
                                 "dynamicscene.xml")
OBJECT_NAMES_XML = os.path.join(GAME_FOLDER, "data", "maps", "r1m1",
                                "object_names.xml")  # data/maps/r1m1/object_names.xml
OBJECT_DESCR_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                                "objectdiz.xml")  # "data\if\strings\objectdiz.xml"
CLANDIZ_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                           "clansdiz.xml")  # data/if/strings/clansdiz.xml
GLOBAL_PROP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                               "globalproperties.xml")  # data\gamedata\globalproperties.xml"
RELATIONSHIP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                                "relationship.xml")  # data/gamedata/relationship.xml
MODEL_ICONS_XML = os.path.join(GAME_FOLDER, "data", "if", "ico",
                               "modelicons.xml")  # data/if/ico/modelicons.xml map with name
MODEL_NAMES_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                               "model_names.xml")  # data\if\diz\model_names.xml
BELONG_LOGO_XML = os.path.join(GAME_FOLDER, "data", "models",
                               "belongstologos.xml")  # "data\models\belongstologos.xml"
LOGOS_GAM = os.path.join(GAME_FOLDER, "data", "models", "logos",
                         "logos.gam")  # "data\models\logos\logos.gam"
RADIO_SOUNDS_XML = os.path.join(GAME_FOLDER, "data", "sounds", "radio",
                                "radiosounds.xml")  # "data\sounds\radio\radiosounds.xml"
DIALOGS_GLOBAL_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                                  "dialogsglobal.xml")  # data\if\diz\dialogsglobal.xml
GAME_OBJECTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                "gameobjects.xml")  # \data\gamedata\gameobjects\gameobjects.xml
TOWNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                         "towns.xml")  # \data\gamedata\gameobjects\gameobjects.xml
VEHICLE_PARTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                 "vehicleparts.xml")  # data\gamedata\gameobjects\vehicleparts.xml

# DYNAMIC_SCENE_XML = os.path.join(os.path.dirname(__file__), "dummy_files",
#                                  "dynamicscene.xml")
# DYNAMIC_SCENE_SHORT = os.path.join(os.path.dirname(__file__), "dummy_files",
#                                    "dynamicsceneshort.xml")
# DYNAMIC_SCENE_SHORTER = os.path.join(os.path.dirname(__file__), "dummy_files",
#                                    "dynamicsceneshorter.xml")
# DYNAMIC_SCENE_CHANGED = os.path.join(os.path.dirname(__file__), "dummy_files",
#                                      "dynamicscenemod.xml")
# DYNAMIC_SCENE_RAW = os.path.join(os.path.dirname(__file__), "dummy_files",
#                                  "dynamicsceneraw.xml")
# CLANDIZ = os.path.join(os.path.dirname(__file__), "dummy_files",
#                        "clansdiz.xml")  # if/strings/clansdiz.xml
# OBJECT_NAMES = os.path.join(os.path.dirname(__file__), "dummy_files",
#                             "object_names.xml")  # maps/r1m1/object_names.xml
# OBJECT_DESCRIPTION = os.path.join(os.path.dirname(__file__), "dummy_files",
#                             "objectdiz.xml")  # "data\if\strings\objectdiz.xml"


def main():
    # creating dictionaries
    object_names_dict = parse_file_to_dict(OBJECT_NAMES_XML)
    object_desc_dict = parse_file_to_dict(OBJECT_DESCR_XML)
    model_icons_dict = parse_file_to_dict(MODEL_ICONS_XML)
    model_names_dict = parse_file_to_dict(MODEL_NAMES_XML)
    clan_desc_dict = parse_file_to_dict(CLANDIZ_XML)
    relationship_dict = parse_file_to_dict(RELATIONSHIP_XML)
    belong_logo_dict = parse_file_to_dict(BELONG_LOGO_XML)
    dialogs_global_dict = parse_file_to_dict(DIALOGS_GLOBAL_XML)
    belong_faction_dict = parse_belong_faction_to_dict(RADIO_SOUNDS_XML)

    # radio_sound_dict["farmers"]["Neutral"]["first_see_other"]["samples"]
    radio_sound_dict = parse_file_to_dict(RADIO_SOUNDS_XML)

    # gam manipulation
    logos_list = parse_logos_gam(LOGOS_GAM)

    # global properties
    global_prop_tree = parse_file_to_objectify(GLOBAL_PROP_XML)

    game_objects_tree = parse_file_to_objectify(GAME_OBJECTS_XML)

    towns_tree = parse_file_to_objectify(TOWNS_XML)
    vehicle_parts_tree = parse_file_to_objectify(VEHICLE_PARTS_XML, recover=True)

    # creating native class object tree for dynamicscene
    clan_tree = parse_clans_to_native(global_prop_tree, clan_desc_dict,
                                      relationship_dict, model_icons_dict,
                                      belong_logo_dict, logos_list,
                                      belong_faction_dict)

    # creating dynamicscene objectify trees
    dynamic_scene_tree = parse_file_to_objectify(DYNAMIC_SCENE_XML)

    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)

    object_tree = parse_objectify_to_native(dynamic_scene_tree,
                                            game_objects_tree,
                                            vehicle_parts_tree,
                                            towns_tree,
                                            object_names_dict,
                                            object_desc_dict,
                                            model_icons_dict,
                                            model_names_dict,
                                            clan_tree,
                                            dialogs_global_dict)
    print(object_tree)


# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


def parse_logos_gam(path: str):
    logo_list = []
    with open(path, "rb") as f:
        str_from_file = f.read()
    logo_list_raw = str_from_file.split(b".dds")
    for byte_str in logo_list_raw:
        logo_list.append(byte_str[byte_str.rindex(b"\x00") + 1:].decode("latin-1"))
    return logo_list


def objectify_to_dict(element):
    if element.tag == "Object":
        return element.attrib["Name"], \
            dict(map(objectify_to_dict, element)) or element.attrib
    elif element.tag == "string":
        return element.attrib["id"], \
            dict(map(objectify_to_dict, element)) or element.attrib["value"]
    elif element.tag == "Belong":
        return element.attrib["id"], \
            dict(map(objectify_to_dict, element)) or element.attrib["logo"]
    elif element.tag == "set":
        return f"{element.attrib['forwhom']}_{element.attrib['tolerance']}", \
            dict(map(objectify_to_dict, element)) or element.attrib
    elif element.tag == "Group" or element.tag == "Reply":
        return element.attrib['name'], \
            dict(map(objectify_to_dict, element)) or element.attrib
    elif (element.tag == "Sound" or element.tag == "Item"):
        return element.attrib['id'], \
            dict(map(objectify_to_dict, element)) or element.attrib
    # elif element.tag == "Item":
    #     return element.attrib['id'], \
    #         dict(map(objectify_to_dict, element)) or element.attrib
    else:  # if element.tag == "ObjectNames" or element.tag == "resource"
        return element.tag, \
            dict(map(objectify_to_dict, element)) or element.attrib


def parse_file_to_dict(path=OBJECT_NAMES_XML):
    dictionary = ()
    from_codec = get_encoding_type(path)
    with open(path, "r", encoding=from_codec) as f:
        str_from_file = f.read().encode(from_codec)  # ('cp1251')
        parser = etree.ETCompatXMLParser(encoding=from_codec)
        objectify.enable_recursive_str()
    objfy = objectify.fromstring(str_from_file, parser)
    dictionary = objectify_to_dict(objfy)
    return dictionary[1]


def parse_belong_faction_to_dict(path=RADIO_SOUNDS_XML):
    dictionary = ()
    from_codec = get_encoding_type(path)
    with open(path, "r", encoding=from_codec) as f:
        str_from_file = f.read().encode(from_codec)  # ('cp1251')
        parser = etree.ETCompatXMLParser(encoding=from_codec)
        objectify.enable_recursive_str()
    objfy = objectify.fromstring(str_from_file, parser)
    dictionary = {}
    for child in objfy.iterchildren():
        for belong in child.attrib["belongs"].split():
            dictionary[belong] = child.attrib["name"]
    return dictionary


def parse_file_to_objectify(path=DYNAMIC_SCENE_XML, recover: bool = False):
    from_codec = get_encoding_type(path)
    with open(path, "r", encoding=from_codec) as f:
        parser_recovery = objectify.makeparser(recover=True)
        objectify.enable_recursive_str()
        objfy = objectify.parse(f, parser_recovery)
    objectify_tree = objfy.getroot()

    for obj in objectify_tree.iterchildren():
        tag_object_dynamicscene(obj)
    return objectify_tree


def parse_clans_to_native(global_props: objectify.ObjectifiedElement,
                          clan_desc_dict: dict, relationship_dict: dict,
                          model_icons_dict: dict, belong_logo_dict: dict,
                          logos_list: list, belong_faction_dict: dict):
    tree = {}
    belongs = global_props["Belongs"].attrib["Values"].split()
    for belong in belongs:
        tree[belong] = ClanClass(belong, clan_desc_dict, relationship_dict,
                                 model_icons_dict, belong_logo_dict,
                                 logos_list, belong_faction_dict)
    pass
    return tree


def tag_object_dynamicscene(obj: objectify.ObjectifiedElement, parent: str = ""):
    if obj.countchildren() > 0:
        for obj_ch in obj.iterchildren():
            tag_object_dynamicscene(obj_ch, obj.tag)
    # towns.xml uses scheme similar but not exactly matching dynamicscene.xml
    # This solution is a bit shit and it's shit because I don't yet know what the hell in
    # this spagetti of xmls will be needed and what info is relevant for tool's functions.
    # I defenitely will not forget to replace this with more elegant parser /s
    if obj.tag == 'Object' and parent != "Prototype":
        obj.tag = f'Obj_{obj.attrib["Prototype"]}'
    elif obj.tag == 'Folder':
        obj.tag = f'Dir_{obj.attrib["Name"]}'


def parse_objectify_to_native(objfy_tree: objectify.ObjectifiedElement,
                              game_objects_tree: objectify.ObjectifiedElement,
                              vehicle_parts_tree: objectify.ObjectifiedElement,
                              towns_tree: objectify.ObjectifiedElement,
                              object_names_dict: dict,
                              object_desc_dict: dict,
                              model_icons_dict: dict,
                              model_names_dict: dict,
                              clan_tree: dict,
                              dialogs_global_dict: dict):
    ''' Returns dictionary of objects grouped by class
    '''
    tree = {}

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
        tree["generic_locations"] = [GenericLocationClass(generic_loc)
                                     for generic_loc in objfy_tree["Obj_genericLocation"]]

    if hasattr(objfy_tree, "Obj_player"):
        tree["player"] = PlayerClass(objfy_tree["Obj_player"])


    return tree


def save_to_file(objectify_tree: objectify.ObjectifiedElement, path,
                 machina_beautify: bool = True):
    ''' Saves ObjectifiedElement tree to file at path, will format and
    beautify file in the style very similar to original Ex Machina
    dynamicscene.xml files by default. Can skip beautifier and save raw
    lxml formated file.
    '''
    xml_string = etree.tostring(objectify_tree,
                                pretty_print=True,
                                xml_declaration=True,
                                encoding='windows-1251',
                                standalone=True)
    with open(path, "wb") as writer:
        if machina_beautify:
            writer.write(machina_xml_beautify(xml_string))
        else:
            writer.write(xml_string)


def machina_xml_beautify(xml_string: str):
    ''' Format and beautify xml string in the style very similar to
    original Ex Machina dynamicscene.xml files.'''
    beautified_string = b""
    previous_line_indent = -1

    # As first line of xml file is XML Declaration, we want to exclude it
    # from Beautifier to get rid of checks for every line down the line
    xml_string_first_line = xml_string[:xml_string.find(b"\n<")]

    for i, line in enumerate(xml_string[xml_string.find(b"\n<")
                             + 1:].splitlines()):
        line_stripped = line.lstrip()
        # calculating indent level of parent line to indent attributes
        # lxml use spaces for indents, game use tabs, so indents maps 2:1
        line_indent = (len(line) - len(line_stripped)) // 2

        line = _split_tag_on_attributes(line_stripped, line_indent)
        # manually tabulating lines according to saved indent level
        line = line_indent * b"\t" + line + b"\n"

        # in EM xmls every first and only first tag of its tree level is
        # separated by a new line
        if line_indent == previous_line_indent:
            line = b"\n" + line

        # we need to know indentation of previous tag to decide if tag is
        # first for its tree level, as described above
        previous_line_indent = line_indent

        beautified_string += line
    return xml_string_first_line + b"\n" + beautified_string


def _split_tag_on_attributes(xml_line: str, line_indent: int):
    white_space_index = xml_line.find(b" ")
    quotmark_index = xml_line.find(b'"')

    # true when no tag attribute contained in string
    if white_space_index == -1 or quotmark_index == -1:
        return xml_line

    elif white_space_index < quotmark_index:
        # next tag attribute found, now indent found attribute and
        # recursively start work on a next line part
        return (xml_line[:white_space_index] + b"\n" + b"\t" * (line_indent + 1)
                + _split_tag_on_attributes(xml_line[white_space_index + 1:],
                                           line_indent))
    else:
        # searching where attribute values ends and new attribute starts
        second_quotmark_index = xml_line.find(b'"', quotmark_index + 1) + 1
        return (xml_line[:second_quotmark_index]
                + _split_tag_on_attributes(xml_line[second_quotmark_index:],
                                           line_indent))


class GameObject(object):
    def __init__(self, element: objectify.ObjectifiedElement):
        self.name = element.attrib["Name"]
        self.belong = element.attrib["Belong"]
        self.prototype = element.attrib["Prototype"]
        self.tag_name = element.tag


class ClanClass(object):
    def __init__(self, belong: str, clan_desc: dict, relationship_dict: dict,
                 model_icons_dict: dict, belong_logo_dict: dict,
                 logos_list: list, belong_faction_dict: dict):  # can belong be any random str or just some int range?
        self.belong = belong  # 1008
        self.name = f"Belong_{belong}"  # "Belong_1008" if/strings/clansdiz.xml, map with belong
        self.full_name = clan_desc[self.name]  # "Союз Фермеров" same as name
        self.member_name = clan_desc[f"{self.name}_abb"]  # "СФ" - same as name
        allies = relationship_dict.get(f"{belong}_ally")
        neutral = relationship_dict.get(f"{belong}_neutral")
        enemy = relationship_dict.get(f"{belong}_enemy")
        self.relationship = {"ally": allies["who"].split() if allies is not None else [],
                             "neutral": neutral["who"].split() if neutral is not None else [],
                             "enemy": enemy["who"].split() if enemy is not None else []}
        #                    {"ally": [1100], - data/gamedata/relationship.xml
        #                    "neutral": [1003, 1009, 1010, 1011, 1051, 1052],
        #                    "enemy": []}

        # if/ico/modelicons.xml map with name
        self.icons = {"small": model_icons_dict[self.name]["file"],  # "data/if/ico/clans/farmers_union02.dds",
                      "big": model_icons_dict[self.name]["file1"]}  # "data/if/ico/clans/farmers_union03.dds"}

        # ("Фермеры работают с землей, как их предки когда-то."
        # " Так как еда нужна всем и всегда, а больше брать с"
        # " них нечего – спокойно существуют в полном"
        # " опасностей мире.")  # same as name
        self.description = clan_desc[f"{self.name}_diz"]

        self.logo_id = belong_logo_dict[belong]  # 10 - farmers_union, models/belongstologos.xml

        # models/logos/farmers_union.dds" - models/logos/logos.gam, id from 0 to 25 in order of listing
        self.logo = f"data\\if\\models\\logos\\{logos_list[int(self.logo_id)]}.dds"
        self.radio_group_name = belong_faction_dict.get(belong)  # "farmers" - sounds/radio/radiosounds.xml


class TownClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 game_objects_tree: objectify.ObjectifiedElement,
                 object_names_dict: dict,
                 object_desc_dict: dict,
                 model_icons_dict: dict,
                 model_names_dict: dict,
                 clan_tree: dict,
                 dialogs_global_dict: dict):
        GameObject.__init__(self, element)
        self.full_name = object_names_dict[self.name]["FullName"]  # "Южный"  # r1m1/object_names.xml map with name
        self.on_map = os.path.dirname(element.base).split("/")[-1]  # "r1m1"  # dir of dynamicscene
        self.clan = clan_tree.get(self.belong)  # map with clans on belong ??? wtf is 1080 belong
        self.position = element.attrib["Pos"]  # "1263.873 308.000 2962.220"
        self.rotation = element.attrib["Rot"]  # "0.000 -0.721 0.000 -0.693"
        self.pov_in_interface = element.attrib["PointOfViewInInterface"]  # "-35.000 60.000 35.000"
        self.caravans_dest = element.attrib["CaravansDest"]  # "" wtf ???
        # ??? need to check what buildings are always required and which can be ommited
        if hasattr(element, "Obj_bar"):
            bar = element["Obj_bar"]
        elif hasattr(element, "Obj_barWithoutBarman"):
            bar = element["Obj_barWithoutBarman"]
        else:
            bar = None
        self.bar = BarClass(bar, self.name, dialogs_global_dict) if bar is not None else None  # "TheTown_Bar"
        self.shop = ShopClass(element["Obj_shop"], model_names_dict) if hasattr(element, "Obj_shop") else None  # "TheTown_Shop"
        self.workshop = WorkshopClass(element["Obj_workshop"], model_names_dict)  # "TheTown_Workshop"
        self.town_enter = None
        self.town_defend = None
        self.town_deploy = None
        self.parts = None  # ??? wtf is this and what it is doing here?
        self.auto_guns = None
        self.generic_locs = []
        for generic_loc in element["Obj_genericLocation"]:
            name = generic_loc.attrib.get("Name")
            if name == f"{self.name}_enter":
                self.town_enter = GenericLocationClass(generic_loc)  # "TheTown_enter"
            elif name == f"{self.name}_defend":
                self.town_defend = GenericLocationClass(generic_loc)  # "TheTown_defend"
            elif name == f"{self.name}_deploy":
                self.town_deploy = GenericLocationClass(generic_loc)  # "TheTown_deploy"
            else:
                self.generic_locs.append(GenericLocationClass(generic_loc))

        self.auto_guns = []
        auto_guns_list = [prototype.attrib["Name"] for prototype in game_objects_tree["Dir_StaticAutoGuns"]["Prototype"]]
        for auto_gun_prototype in auto_guns_list:
            if hasattr(element, f"Obj_{auto_gun_prototype}"):
                # ["staticAutoGun045"]
                self.auto_guns.extend([AutoGunClass(auto_gun) for auto_gun in element[f"Obj_{auto_gun_prototype}"]])

        # {"Points": ["1220.000 2970.000", "1260.000 2966.500"],
        #  "CameraPoints": ["-95.811 24.235 8.577", "-35.000 60.000 35.000"]}
        # attrib id dictionary containing points, dict will evaluate to false if there is no points
        if hasattr(element["EntryPath"], "Point") and hasattr(element["EntryPath"], "CameraPoint"):
            self.entry_path = {"Points":
                               [el.attrib.get("Pos") for el in element["EntryPath"]["Point"]],
                               "CameraPoints":
                               [el.attrib.get("Pos") for el in element["EntryPath"]["CameraPoint"]]}
        else:
            self.entry_path = None

        # {"Points": ["1260.000 2966.500", "1220.000 2970.000"],
        #  "CameraPoints": ["-35.000 60.000 35.000", "-95.811 24.235 8.577"]}
        if hasattr(element["ExitPath"], "Point") and hasattr(element["ExitPath"], "CameraPoint"):
            self.exit_path = {"Points":
                              [el.attrib.get("Pos") for el in element["ExitPath"]["Point"]],
                              "CameraPoints":
                              [el.attrib.get("Pos") for el in element["ExitPath"]["CameraPoint"]]}
        else:
            self.exit_path = None

        self.town_icon = model_icons_dict[self.prototype]  # "icn_town.dds"  # if/ico/modelicons.xml

        # ("Крохотный город, существующий лишь торговлей"
        #  " с заезжими северными купцами.")  # "data\if\strings\objectdiz.xml")
        self.description = object_desc_dict[f"{self.on_map}_{self.name}_diz"]

        # maybe too ambitious and unnecessary, if\diz\questinfoglobal.xml
        # map on tag <Map name="r1m1" targetObjName="self.name"/>
        # or from gamedata/quests.xml
        self.placeholder_role_in_quest = ["Buyer_Quest1",
                                          "d_FindBenInSouth_Quest",
                                          "d_FindFelix_Quest"]


class BarClass(GameObject):
    def __init__(self,
                 element: objectify.ObjectifiedElement,
                 parent_name: str,
                 dialogs_global_dict: dict):
        GameObject.__init__(self, element)
        self.parent_town_name = parent_name
        self.npcs = [NpcCLass(npc_element, self.name, dialogs_global_dict) for npc_element in element["Obj_NPC"]]
        if element.tag == "Obj_bar":
            self.withoutbarmen = False
            self.barman = [npc.name for npc in self.npcs if npc.type == "BARMAN"][0]
        else:
            self.withoutbarment = True
            self.barman = None


class WorkshopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.parent_town_name = element.attrib["Name"].replace("_Workshop", "")
        
        if hasattr(element, "CabinsAndBaskets"):
            self.cabins_and_baskets = [SoldPartClass(part_element, model_names_dict)
                                       for part_element in element["CabinsAndBaskets"]["Item"]]
        else:
            self.cabins_and_baskets = None

        if hasattr(element, "Vehicles"):
            if hasattr(element["Vehicles"], "Item"):
                self.vehicles = [VehicleClass(vehicle_element, model_names_dict)
                                 for vehicle_element in element["Vehicles"]["Item"]]
        else:
            self.vehicles = None


class ShopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.parent_town_name = element.attrib["Name"].replace("_Shop", "")
        self.guns_and_gadgets = [SoldPartClass(part_element, model_names_dict)
                                 for part_element in element["GunsAndGadgets"]["Item"]]


class NpcCLass(GameObject):
    def __init__(self,
                 element: objectify.ObjectifiedElement,
                 parent_name: str,
                 dialogs_global_dict: dict):
        GameObject.__init__(self, element)
        self.parent_building_name = parent_name  # or parent location/object?
        self.model_name = element.attrib["ModelName"]  # "r1_woman"
        self.model_cfg = element.attrib.get("cfg")  # 44
        self.model_skin = element.attrib.get("skin")  # 2 ???
        self.type = element.attrib.get("NpcType")  # "BARMAN"
        self.spoken_count = element.attrib["SpokenCount"]  # 0
        hello_reply_names = element.attrib.get("helloReplyNames")  # 'Buyer_hellodlg0 Buyer_hellodlg1'
        self.hello_reply_names = []
        if hello_reply_names is not None:
            for line in hello_reply_names.split():
                if dialogs_global_dict.get(line) is not None:
                    self.hello_reply_names.append([line, dialogs_global_dict[line]["text"]])
                else:
                    self.hello_reply_names.append([line, "MISSING_LINE"])


class SoldPartClass(object):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        self.pos_xy = [element.attrib["PosX"], element.attrib["PosY"]]  # [0, 0]
        self.flags = element.attrib["Flags"]  # 16
        self.prototype = element.attrib["Prototype"]  # "bugCargo02"
        self.prototype_name = model_names_dict[self.prototype]['value']
        if element.attrib.get("Name") is not None:
            self.name = element.attrib["Name"]
        else:
            self.name = None


class VehiclePartClass(object):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        self.present = element.attrib["present"]  # 1
        self.flags = element.attrib["Flags"]  # 16
        self.prototype = element.attrib["Prototype"]  # "bugCargo01"
        prototype_name = model_names_dict.get(self.prototype)
        self.prototype_name = prototype_name.get("value") if (prototype_name is not None) else None


class VehicleClass(SoldPartClass):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        SoldPartClass.__init__(self, element, model_names_dict)
        self.position = element.attrib["Pos"]  # "0.000 369.722 0.000"
        self.rotation = element.attrib.get("Rot")  # "-0.007 1.000 -0.010 0.021" or missing

        # {"present": 1,
        # "flags": 16,
        # "prototype": "bugCargo01"}
        if hasattr(element["Parts"], "BASKET"):
            self.basket = VehiclePartClass(element["Parts"]["BASKET"], model_names_dict)
            self.cabin = VehiclePartClass(element["Parts"]["CABIN"], model_names_dict)
            self.chassis = VehiclePartClass(element["Parts"]["CHASSIS"], model_names_dict)
        else:
            self.basket = None
            self.cabin = None
            self.chassis = None

        if element["Repository"].attrib:
            self.repository = [SoldPartClass(part_element, model_names_dict)
                               for part_element in element["Repository"]["Item"]]
        else:
            self.repository = None


class PlayerClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.money = element.attrib["Money"]
        self.vehicle = [element.iterchildren()][0]


class AutoGunClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.position = element.attrib["Pos"]  # "1219.141 304.220 2990.261"
        if element["Parts"].attrib:
            self.parts_cannon = AutoGunCannonClass(element["Parts"]["CANNON"])  # "staticAutoGun0444CANNON"
        else:
            self.parts_cannon = None


class AutoGunCannonClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.present = element.attrib["present"]  # 1


class GenericLocationClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.flags = element.attrib["Flags"]  # 21
        self.position = element.attrib["Pos"]  # "3351.445 369.913 3338.112"
        self.rotation = element.attrib.get("Rot")  # "0.000 -0.721 0.000 -0.693"
        self.radius = element.attrib["Radius"]  # "6.584"
        if hasattr(element, "LookingTimeOut"):
            self.looking_timeout = element.attrib["LookingTimeOut"]  # "20.000"
        else:
            self.looking_timeout = None


if __name__ == "__main__":
    sys.exit(main())
