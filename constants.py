import os

GAME_FOLDER = "D:/Steam/steamapps/common/Hard Truck Apocalypse"

MAP_NAME = "r1m3"

# gamedata folder
GLOBAL_PROP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                               "globalproperties.xml")  # data\gamedata\globalproperties.xml
RESOURCE_TYPES_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                                  "resourcetypes.xml")  # data\gamedata\resourcetypes.xml
VEHICLE_PART_TYPES_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                                      "vehicleparttypes.xml")  # data\gamedata\vehicleparttypes.xml
RELATIONSHIP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                                "relationship.xml")  # data/gamedata/relationship.xml
AFFIXES_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                           "affixes.xml")  # data/gamedata/affixes.xml
QUESTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                          "quests.xml")  # data/gamedata/quests.xml

# gamedata/gameobjects
GAME_OBJECTS_PATH = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects")
GAME_OBJECTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                "gameobjects.xml")  # \data\gamedata\gameobjects\gameobjects.xml
TACTICS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                           "tactics.xml")  # \data\gamedata\gameobjects\tactics.xml
INFECTION_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                             "infection.xml")  # \data\gamedata\gameobjects\infection.xml
CARAVAN_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                           "caravan.xml")  # \data\gamedata\gameobjects\caravan.xml
MISC_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                        "miscellaneous.xml")  # data\gamedata\gameobjects\miscellaneous.xml
BOSSES_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                          "bosses.xml")  # data\gamedata\gameobjects\bosses.xml
GADGETS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                           "gadgets.xml")  # data\gamedata\gameobjects\gadgets.xml
WARES_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                         "wares.xml")  # data\gamedata\gameobjects\wares.xml
QUEST_ITEMS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                               "questitems.xml")  # data\gamedata\gameobjects\questitems.xml
BREAKABLE_OBJ_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                 "breakableobjects.xml")  # data\gamedata\gameobjects\breakableobjects.xml
TOWNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                         "towns.xml")  # \data\gamedata\gameobjects\gameobjects.xml
VEHICLES_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                            "vehicles.xml")  # data\gamedata\gameobjects\vehicles.xml
VEHICLE_PARTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                 "vehicleparts.xml")  # data\gamedata\gameobjects\vehicleparts.xml
PREFABS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                           "prefabs.xml")  # data\gamedata\gameobjects\prefabs.xml
# guns - listed as folder in gameobjects.xml
SMALL_GUNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                              "smallguns.xml")  # data\gamedata\gameobjects\smallguns.xml
BIG_GUNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                            "bigguns.xml")  # data\gamedata\gameobjects\bigguns.xml
GIANT_GUNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                              "giantguns.xml")  # data\gamedata\gameobjects\giantguns.xml
SIDE_GUNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                             "sideguns.xml")  # data\gamedata\gameobjects\sideguns.xml
GUNS_XML_DICT = {"small_guns": SMALL_GUNS_XML, "big_guns": BIG_GUNS_XML,
                 "giant_guns": GIANT_GUNS_XML, "side_guns": SIDE_GUNS_XML}

# maps folder
DYNAMIC_SCENE_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                                 "dynamicscene.xml")  # data/maps/r1m1/dynamicscene.xml
OBJECT_NAMES_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                                "object_names.xml")  # data/maps/r1m1/object_names.xml
TOWN_BACKGROUND_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                                   "icons.xml")  # data/maps/r1m1/icons.xml
TRIGGERS_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                            "triggers.xml")  # data/maps/r1m1/triggers.xml
CINEMA_TRIGGERS_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                                   "cinematriggers.xml")  # data/maps/r1m1/cinematriggers.xml

# models folder
BELONG_LOGO_XML = os.path.join(GAME_FOLDER, "data", "models",
                               "belongstologos.xml")  # "data\models\belongstologos.xml
LOGOS_GAM = os.path.join(GAME_FOLDER, "data", "models", "logos",
                         "logos.gam")  # "data\models\logos\logos.gam"

# sounds folder
RADIO_SOUNDS_XML = os.path.join(GAME_FOLDER, "data", "sounds", "radio",
                                "radiosounds.xml")  # "data\sounds\radio\radiosounds.xml
DIALOGS_GLOBAL_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                                  "dialogsglobal.xml")  # data\if\diz\dialogsglobal.xml

# if/strings folder
OBJECT_DESCR_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                                "objectdiz.xml")  # "data\if\strings\objectdiz.xml
CLANDIZ_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                           "clansdiz.xml")  # data/if/strings/clansdiz.xml

# if/ico folder
MODEL_ICONS_XML = os.path.join(GAME_FOLDER, "data", "if", "ico",
                               "modelicons.xml")  # data/if/ico/modelicons.xml map with name

# if/diz folder
MODEL_NAMES_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                               "model_names.xml")  # data\if\diz\model_names.xml
QUEST_INFO_GLOB_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                                   "questinfoglobal.xml")  # data\if\diz\questinfoglobal.xml
