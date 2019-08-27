import os
import sys
from lxml import etree, objectify

DYNAMIC_SCENE_XML = os.path.join(os.path.dirname(__file__), "dummy_files",
                                 "dynamicscene.xml")
DYNAMIC_SCENE_SHORT = os.path.join(os.path.dirname(__file__), "dummy_files",
                                   "dynamicsceneshort.xml")
DYNAMIC_SCENE_CHANGED = os.path.join(os.path.dirname(__file__), "dummy_files",
                                     "dynamicscenemod.xml")
DYNAMIC_SCENE_RAW = os.path.join(os.path.dirname(__file__), "dummy_files",
                                 "dynamicsceneraw.xml")


def main():
    # dynamic_scene_tree = parse_file_to_tree(DYNAMIC_SCENE_XML)
    dynamic_scene_tree_short = parse_file_to_tree(DYNAMIC_SCENE_SHORT)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    # save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)
    print(dynamic_scene_tree_short)


def parse_file_to_tree(path=DYNAMIC_SCENE_XML):
    with open(path, "r") as f:
        objectify.enable_recursive_str()
        objfy = objectify.parse(f)
    objectify_tree = objfy.getroot()

    return objectify_tree


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
    def __init__(self, element: objectify.ObjectifiedElement):
        self.belong = "1008"
        self.name = "Belong_1008"  # if/strings/clandiz.xml, map with belong
        self.full_name = "Союз Фермеров"  # same as name
        self.member_name = "СФ"  # same as name
        self.relationship = {"ally": [1100],  # data/gamedata/relationship.xml
                             "neutral": [1003, 1009, 1010, 1011, 1051, 1052],
                             "enemy": []}

        # if/ico/modelicons.xml map with name
        self.icons = {"small": "data/if/ico/clans/farmers_union02.dds",
                      "big": "data/if/ico/clans/farmers_union03.dds"}
        self.description = ("Фермеры работают с землей, как их предки когда-то."
                            " Так как еда нужна всем и всегда, а больше брать с"
                            " них нечего – спокойно существуют в полном"
                            " опасностей мире.")  # same as name
        self.logo_id = 10  # farmers_union, models/belongstologos.xml
        self.logo = "farmers_union.dds"  # models/logos/logos.gam, id from 0 to 25 in order of listing
        self.radio_group_name = "farmers"  # sounds/radio/radiosounds.xml


class TownClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.full_name = "Южный"  # r1m1/object_names.xml map with name
        self.on_map = "r1m1"  # dir of dynamicscene
        self.clan = "1008 / Союз Фермеров"  # map with clans on belong
        self.position = "1263.873 308.000 2962.220"
        self.rotation = "0.000 -0.721 0.000 -0.693"
        self.pov_in_interface = "-35.000 60.000 35.000"
        self.caravans_dest = ""
        self.bar = "TheTown_Bar"
        self.shop = "TheTown_Shop"
        self.workshop = "TheTown_Workshop"
        self.town_enter = "TheTown_enter"
        self.town_defend = "TheTown_defend"
        self.town_deploy = "TheTown_deploy"
        self.parts = None  # wtf is this and what it is doing here?
        self.auto_guns = ["staticAutoGun045"]
        self.entry_path = {"Points": ["1220.000 2970.000",
                                      "1260.000 2966.500"],
                           "CameraPoints": ["-95.811 24.235 8.577",
                                            "-35.000 60.000 35.000"]}
        self.exit_path = {"Points": ["1260.000 2966.500",
                                     "1220.000 2970.000"],
                          "CameraPoints": ["-35.000 60.000 35.000",
                                           "-95.811 24.235 8.577"]}

        self.town_icon = "icn_town.dds"  # if/ico/modelicons.xml
        self.description = ("Крохотный город, существующий лишь торговлей"
                            " с заезжими северными купцами.")
        self.role_in_quest = ["Buyer_Quest1",  # maybe too ambitious and unnecessary, if\diz\questinfoglobal.xml
                              "d_FindBenInSouth_Quest",  # map on tag <Map targetObjName="self.name"/>
                              "d_FindFelix_Quest"]  # or from gamedata/quests.xml


class BarClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town = "TheTown"
        self.withoutbarment = False
        self.npcs = []


class WorkshopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town = "TheTown"
        self.cabins_and_baskets = []
        self.vehicles = []


class ShopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_town = "TheTown"
        self.guns_and_gadgets = []


class NpcCLass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement):
        GameObject.__init__(self, element)
        self.parent_building = "TheTown_Bar"  # or parent location/object?
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
