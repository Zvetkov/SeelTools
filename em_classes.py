import os
from lxml import objectify


class GameObject(object):
    def __init__(self, element: objectify.ObjectifiedElement):
        self.name = element.attrib.get("Name")
        if self.name is None:
            self.name = "GAMEOBJ_MISSING_NAME"
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
        full_name_dict_value = object_names_dict.get(self.name)
        if full_name_dict_value is not None:
            self.full_name = full_name_dict_value["FullName"]  # "Южный"  # r1m1/object_names.xml map with name
        else:
            self.full_name = f"{self.name}_MISSING_FULL_NAME"
        self.on_map = os.path.dirname(element.base).split("/")[-1]  # "r1m1"  # dir of dynamicscene
        self.clan = clan_tree.get(self.belong)  # map with clans on belong ??? wtf is 1080 belong
        self.position = element.attrib["Pos"]  # "1263.873 308.000 2962.220"
        self.rotation = element.attrib.get("Rot")  # "0.000 -0.721 0.000 -0.693"
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
        # "TheTown_Shop"
        self.shop = ShopClass(element["Obj_shop"], model_names_dict) if hasattr(element, "Obj_shop") else None
        # "TheTown_Workshop"
        self.workshop = WorkshopClass(element["Obj_workshop"], model_names_dict) if hasattr(element, "Obj_workshop") else None

        # initialising
        self.town_enter = None
        self.town_defend = None
        self.town_deploy = None
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
                self.generic_locs.append(GenericLocationClass(generic_loc, dialogs_global_dict))

        if hasattr(element, "Parts"):
            if hasattr(element["Parts"], "AttackTeam"):
                self.parts = {"AttackTeam": {"present": element["Parts"]["AttackTeam"].attrib.get("present")}}
        else:
            self.parts = None

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

        description = object_desc_dict.get(f"{self.on_map}_{self.name}_diz")
        if description is not None:
            self.description = description
        else:
            self.description = f"{self.name}_MISSING_DESCRIPTION"

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
        if hasattr(element, "Obj_NPC"):
            self.npcs = [NpcCLass(npc_element, self.name, dialogs_global_dict) for npc_element in element["Obj_NPC"]]
        else:
            self.npcs = None

        if element.tag == "Obj_bar":
            self.withoutbarmen = False
            if self.npcs is not None:
                self.barman = [npc.name for npc in self.npcs if npc.type == "BARMAN"][0]
            else:
                self.barman = "MISSING_BARMAN"
        else:
            self.withoutbarment = True
            self.barman = None


class WorkshopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.parent_town_name = element.attrib["Name"].replace("_Workshop", "")

        if hasattr(element, "CabinsAndBaskets"):
            if hasattr(element["CabinsAndBaskets"], "Item"):
                self.cabins_and_baskets = [SoldPartClass(part_element, model_names_dict)
                                           for part_element in element["CabinsAndBaskets"]["Item"]]
        else:
            self.cabins_and_baskets = None

        if hasattr(element, "Vehicles"):
            if hasattr(element["Vehicles"], "Item"):
                self.vehicles = [VehicleSoldClass(vehicle_element, model_names_dict)
                                 for vehicle_element in element["Vehicles"]["Item"]]
        else:
            self.vehicles = None


class ShopClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.parent_town_name = element.attrib["Name"].replace("_Shop", "")
        self.guns_and_gadgets = []
        if hasattr(element, "GunsAndGadgets"):
            if hasattr(element["GunsAndGadgets"], "Item"):
                self.guns_and_gadgets.append(
                    {"Combined": [SoldPartClass(part, model_names_dict)
                     for part in element["GunsAndGadgets"]["Item"]]})
            else:
                self.guns_and_gadgets = []
        elif hasattr(element, "Guns") or hasattr(element, "Gadgets"):
            if hasattr(element, "Guns"):
                self.guns_and_gadgets.append(
                    {"Guns": [SoldPartClass(gun, model_names_dict)
                     for gun in element["Guns"]["Item"]]})
            else:
                self.guns_and_gadgets.append({"Guns": []})
            if hasattr(element, "Gadgets"):
                self.guns_and_gadgets.append(
                    {"Gadgets": [SoldPartClass(gun, model_names_dict)
                     for gun in element["Gadgets"]["Item"]]})
            else:
                self.guns_and_gadgets.append({"Gadgets": []})
        else:
            self.guns_and_gadgets = "MISSING_GUNS_AND_GADGETS"


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
        self.flags = element.attrib.get("Flags")  # 16 # ??? is this class really working if missing? example: zoo.ssl
        self.prototype = element.attrib["Prototype"]  # "bugCargo02"
        self.prototype_name = model_names_dict[self.prototype]['value']

        # zoo attribs unused in main game
        self.durability = element.attrib.get("Durability")  # ??? check that it works as exoected, only available on zoo
        self.max_durability = element.attrib.get("MaxDurability")  # ??? same as durability
        self.price = element.attrib.get("Price")  # ??? same as durability
        self.damage = element.attrib.get("Damage")  # ??? same as durability
        self.firing_rate = element.attrib.get("FiringRate")  # ??? same as durability
        self.firing_range = element.attrib.get("FiringRange")  # ??? same as durability


class VehiclePartClass(object):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        self.present = element.attrib["present"]  # 1
        self.flags = element.attrib.get("Flags")  # 16
        self.prototype = element.attrib["Prototype"]  # "bugCargo01"
        prototype_name = model_names_dict.get(self.prototype)
        self.prototype_name = prototype_name.get("value") if (prototype_name is not None) else None


class VehicleClass(object):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):

        self.position = element.attrib.get("Pos")  # "0.000 369.722 0.000"

        # {"present": 1,
        # "flags": 16,
        # "prototype": "bugCargo01"}
        if hasattr(element["Parts"], "BASKET"):
            self.basket = VehiclePartClass(element["Parts"]["BASKET"], model_names_dict)
            self.cabin = VehiclePartClass(element["Parts"]["CABIN"], model_names_dict)
        else:
            self.basket = None
            self.cabin = None

        if hasattr(element["Parts"], "CHASSIS"):
            self.chassis = VehiclePartClass(element["Parts"]["CHASSIS"], model_names_dict)
        else:
            self.chassis = None

        if element["Repository"].attrib:
            self.repository = [SoldPartClass(part_element, model_names_dict)
                               for part_element in element["Repository"]["Item"]]
        else:
            self.repository = None


class VehicleSoldClass(VehicleClass, SoldPartClass):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        SoldPartClass.__init__(self, element, model_names_dict)
        VehicleClass.__init__(self, element, model_names_dict)


class VehicleSpawnableClass(VehicleClass, GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.rotation = element.attrib.get("Rot")  # "-0.007 1.000 -0.010 0.021" or missing
        VehicleClass.__init__(self, element, model_names_dict)


class PlayerClass(GameObject):
    def __init__(self, element: objectify.ObjectifiedElement,
                 vehicles_proto: dict,
                 model_names_dict: dict):
        GameObject.__init__(self, element)
        self.money = element.attrib.get("Money")
        if len(element.getchildren()) == 1:
            self.vehicle = VehicleSpawnableClass(element.getchildren()[0], model_names_dict)
        else:
            self.vehicle = None  # r3m1 player prototype as example


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
    def __init__(self, element: objectify.ObjectifiedElement,
                 dialogs_global_dict: dict = {}):
        GameObject.__init__(self, element)
        self.flags = element.attrib.get("Flags")  # 21
        self.position = element.attrib["Pos"]  # "3351.445 369.913 3338.112"
        self.rotation = element.attrib.get("Rot")  # "0.000 -0.721 0.000 -0.693"
        self.radius = element.attrib["Radius"]  # "6.584"
        self.looking_timeout = element.attrib.get("LookingTimeOut")  # "20.000"
        if hasattr(element, "Obj_NPC"):
            self.npcs = [NpcCLass(npc, self.name, dialogs_global_dict) for npc in element["Obj_NPC"]]
        else:
            self.npcs = None
        self.exit_location = element.attrib.get("ExitLocation")
        self.passage_active = element.attrib.get("PassageActive")
        self.passage_address = element.attrib.get("PassageAddress")
