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
                               "modelicons.xml")  # if/ico/modelicons.xml map with name
BELONG_LOGO_XML = os.path.join(GAME_FOLDER, "data", "models",
                               "belongstologos.xml")  # "data\models\belongstologos.xml"
LOGOS_GAM = os.path.join(GAME_FOLDER, "data", "models", "logos",
                         "logos.gam")  # "data\models\logos\logos.gam"
RADIO_SOUNDS_XML = os.path.join(GAME_FOLDER, "data", "sounds", "radio",
                                "radiosounds.xml")  # "data\sounds\radio\radiosounds.xml"

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
    clan_desc_dict = parse_file_to_dict(CLANDIZ_XML)
    relationship_dict = parse_file_to_dict(RELATIONSHIP_XML)
    belong_logo_dict = parse_file_to_dict(BELONG_LOGO_XML)
    belong_faction_dict = parse_belong_faction_to_dict(RADIO_SOUNDS_XML)

    # radio_sound_dict["farmers"]["Neutral"]["first_see_other"]["samples"]
    radio_sound_dict = parse_file_to_dict(RADIO_SOUNDS_XML)

    # gam manipulation
    logos_list = parse_logos_gam(LOGOS_GAM)

    # global properties
    global_prop_tree = parse_file_to_objectify(GLOBAL_PROP_XML)

    # creating native class object tree for dynamicscene
    clan_tree = parse_clans_to_native(global_prop_tree, clan_desc_dict,
                                      relationship_dict, model_icons_dict,
                                      belong_logo_dict, logos_list,
                                      belong_faction_dict)

    # creating dynamicscene objectify trees
    dynamic_scene_tree = parse_file_to_objectify(DYNAMIC_SCENE_XML)

    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)

    object_tree = parse_objectify_to_native(dynamic_scene_tree, object_names_dict, object_desc_dict, clan_tree)
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
    elif element.tag == "Group":
        return element.attrib['name'], \
               dict(map(objectify_to_dict, element)) or element.attrib
    elif element.tag == "Sound":
        return element.attrib['id'], \
               dict(map(objectify_to_dict, element)) or {"samples": element.attrib["samples"],
                                                         "probability": element.attrib["probability"]}
    elif element.tag == "Item":
        return element.attrib['id'], \
               dict(map(objectify_to_dict, element)) or {"file": element.attrib["file"],
                                                         "file1": element.attrib["file1"]}
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


def parse_file_to_objectify(path=DYNAMIC_SCENE_XML):
    from_codec = get_encoding_type(path)
    with open(path, "r", encoding=from_codec) as f:
        objectify.enable_recursive_str()
        objfy = objectify.parse(f)
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


def tag_object_dynamicscene(obj: objectify.ObjectifiedElement):
    if obj.countchildren() > 0:
        for obj_ch in obj.iterchildren():
            tag_object_dynamicscene(obj_ch)
    if obj.tag == 'Object':
        obj.tag = f'Obj_{obj.attrib["Prototype"]}'


def parse_objectify_to_native(objfy_tree: objectify.ObjectifiedElement,
                              object_names_dict: dict,
                              object_desc_dict: dict,
                              clan_tree: dict):
    ''' Returns dictionary of objects grouped by class
    '''
    tree = {}
    if hasattr(objfy_tree, "Obj_TownSouth"):
        tree["towns"] = [TownClass(objfy_tree["Obj_TownSouth"],
                                   object_names_dict,
                                   object_desc_dict,
                                   clan_tree)]
        tree["towns"].append(TownClass(objfy_tree["Obj_r1m1_GloohoeVillage"],
                                       object_names_dict,
                                       object_desc_dict,
                                       clan_tree))

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
        self.description = clan_desc[f"{self.name}_diz"]  # ("Фермеры работают с землей, как их предки когда-то."
                                                          #  " Так как еда нужна всем и всегда, а больше брать с"
                                                          #  " них нечего – спокойно существуют в полном"
                                                          #  " опасностей мире.")  # same as name
        self.logo_id = belong_logo_dict[belong]  # 10 - farmers_union, models/belongstologos.xml
        self.logo = f"data\\if\\models\\logos\\{logos_list[int(self.logo_id)]}.dds"  # models/logos/farmers_union.dds" - models/logos/logos.gam, id from 0 to 25 in order of listing
        self.radio_group_name = belong_faction_dict.get(belong)  # "farmers" - sounds/radio/radiosounds.xml


class TownClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 object_names_dict: dict,
                 object_desc_dict: dict,
                 clan_tree: dict):
        GameObject.__init__(self, element)
        self.full_name = object_names_dict[self.name]["FullName"]  # "Южный"  # r1m1/object_names.xml map with name
        self.on_map = os.path.dirname(element.base).split("/")[-1]  # "r1m1"  # dir of dynamicscene
        self.clan = clan_tree[self.belong]  # map with clans on belong
        self.position = element.attrib["Pos"]  # "1263.873 308.000 2962.220"
        self.rotation = element.attrib["Rot"]  # "0.000 -0.721 0.000 -0.693"
        self.pov_in_interface = element.attrib["PointOfViewInInterface"]  # "-35.000 60.000 35.000"
        self.caravans_dest = element.attrib["CaravansDest"]  # "" wtf ???
        # ??? need to check what buildings are always required and which can be ommited
        self.bar = BarClass(element["Obj_bar"]) if hasattr(element, "Obj_bar") else BarClass(element["Obj_barWithoutBarman"])  # "TheTown_Bar"
        self.shop = ShopClass(element["Obj_shop"])  # "TheTown_Shop"
        self.workshop = WorkshopClass(element["Obj_workshop"])  # "TheTown_Workshop"
        self.town_enter = GenericLocationClass(element["Obj_genericLocation"])  # "TheTown_enter"
        self.town_defend = GenericLocationClass(element["Obj_genericLocation"])  # "TheTown_defend"
        self.town_deploy = GenericLocationClass(element["Obj_genericLocation"])  # "TheTown_deploy"
        self.parts = None  # wtf is this and what it is doing here?
        self.auto_guns = None
        if hasattr(element, "Obj_staticAutoGun04"):
            self.auto_guns = [AutoGunClass(element["Obj_staticAutoGun04"])]  # ["staticAutoGun045"]
        self.entry_path = {"Points": ["1220.000 2970.000",  # {"Points": ["1220.000 2970.000",
                                      "1260.000 2966.500"],  #            "1260.000 2966.500"],
                           "CameraPoints": ["-95.811 24.235 8.577",  #   "CameraPoints": ["-95.811 24.235 8.577",
                                            "-35.000 60.000 35.000"]}  #                  "-35.000 60.000 35.000"]}
        self.exit_path = {"Points": ["1260.000 2966.500",
                                     "1220.000 2970.000"],
                          "CameraPoints": ["-35.000 60.000 35.000",
                                           "-95.811 24.235 8.577"]}

        self.town_icon = "icn_town.dds"  # if/ico/modelicons.xml
        self.description = object_desc_dict[f"{self.on_map}_{self.name}_diz"]  # ("Крохотный город, существующий лишь торговлей"
                                                                          # " с заезжими северными купцами.")  # "data\if\strings\objectdiz.xml"
        self.role_in_quest = ["Buyer_Quest1",  # maybe too ambitious and unnecessary, if\diz\questinfoglobal.xml
                              "d_FindBenInSouth_Quest",  # map on tag <Map targetObjName="self.name"/>
                              "d_FindFelix_Quest"]  # or from gamedata/quests.xml


class BarClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town_name = "TheTown"
        self.withoutbarment = False
        self.npcs = []


class WorkshopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town_name = "TheTown"
        self.cabins_and_baskets = []
        self.vehicles = []


class ShopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town_name = "TheTown"
        self.guns_and_gadgets = []


class NpcCLass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_building_name = "TheTown_Bar"  # or parent location/object?
        self.model_name = "r1_woman"
        self.model_skin = 2
        self.model_cfg = 44
        self.type = "BARMAN"
        self.spoken_count = 0
        self.dialogue_lines = []


class VehicleClass(object):
    def __init__(self, element: objectify.ObjectifiedElement):
        self.pos_xy = ["x", "y"]
        self.flags = 16
        self.pos = "0.000 369.722 0.000"
        self.basket = {"present": 1,
                       "flags": 16,
                       "prototype": "bugCargo01"}
        self.cabin = {"present": 1,
                      "flags": 16,
                      "prototype": "bugCab01"}
        self.chassis = {"present": 1,
                        "flags": 16,
                        "prototype": "bugChassis"}
        self.repository = ""


class SoldPartClass(object):
    def __init__(self, element: objectify.ObjectifiedElement):
        self.pos_xy = [0, 0]
        self.flags = 16
        self.prototype = "bugCargo02"


class AutoGunClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.pos = "1219.141 304.220 2990.261"
        self.parts_cannon = "staticAutoGun0444CANNON"


class AutoGunCannonClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.present = 1


class GenericLocationClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.flags = 21
        self.pos = "3351.445 369.913 3338.112"
        self.radius = "6.584"
        self.looking_timeout = "20.000"


if __name__ == "__main__":
    sys.exit(main())
