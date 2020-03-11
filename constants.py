import os

WORKING_DIRECTORY = "D:/Steam/steamapps/common/Hard Truck Apocalypse"

MAP_NAME = "r1m3"

# gamedata folder

# CONFIG_PATH = os.path.join("data", "config.cfg")

LOCALIZED_FORMS_QUANTITY = 2

STATUS_SUCCESS = 1

# CONFIG = parse_config(CONFIG_PATH)
# CONFIG = {"pathToAffixes": "data/gamedata/Affixes.xml",
#           "pathToDialogs": "data/if/diz/DialogsGlobal.xml",
#           "pathToDynamicDialogs": "data/if/diz/DynamicDialogsGlobal.xml",
#           "pathToLevelInfo": "data/if/diz/LevelInfo.xml",
#           "pathToQuestInfo": "data/if/diz/QuestInfoGlobal.xml",
#           "pathToResourceTypes": "data/gamedata/ResourceTypes.xml",
#           "pathToSoilProps": "data/tiles/TilesProps.xml",
#           "pathToUiIcons": "data/if/ico/UiIcons.xml",
#           "pathToUiStrings": "data/if/strings/UiStrings.xml",
#           "pathToUiWindows": "data/if/dialogs/UiWindows.xml",
#           "pathToVehiclePartTypes": "data/gamedata/VehiclePartTypes.xml"}

GLOBAL_PROP_XML = os.path.join("data", "gamedata",
                               "globalproperties.xml")  # data\gamedata\globalproperties.xml
# RESOURCE_TYPES_XML = os.path.join("data", "gamedata",
#                                   "resourcetypes.xml")  # data\gamedata\resourcetypes.xml
# VEHICLE_PART_TYPES_XML = os.path.join("data", "gamedata",
#                                       "vehicleparttypes.xml")  # data\gamedata\vehicleparttypes.xml
# RELATIONSHIP_XML = os.path.join("data", "gamedata",
#                                 "relationship.xml")  # data/gamedata/relationship.xml
# AFFIXES_XML = os.path.join("data", "gamedata",
#                            "affixes.xml")  # data/gamedata/affixes.xml
# QUESTS_XML = os.path.join("data", "gamedata",
#                           "quests.xml")  # data/gamedata/quests.xml

# gamedata/gameobjects
GAME_OBJ_DEFS_XML = os.path.join("data", "gamedata", "gameobjdefs.xml")
GAME_OBJECTS_PATH = os.path.join("data", "gamedata", "gameobjects")
# GAME_OBJECTS_XML = os.path.join("data", "gamedata", "gameobjects",
#                                 "gameobjects.xml")  # \data\gamedata\gameobjects\gameobjects.xml
TACTICS_XML = os.path.join("data", "gamedata", "gameobjects",
                           "tactics.xml")  # \data\gamedata\gameobjects\tactics.xml
INFECTION_XML = os.path.join("data", "gamedata", "gameobjects",
                             "infection.xml")  # \data\gamedata\gameobjects\infection.xml
CARAVAN_XML = os.path.join("data", "gamedata", "gameobjects",
                           "caravan.xml")  # \data\gamedata\gameobjects\caravan.xml
MISC_XML = os.path.join("data", "gamedata", "gameobjects",
                        "miscellaneous.xml")  # data\gamedata\gameobjects\miscellaneous.xml
BOSSES_XML = os.path.join("data", "gamedata", "gameobjects",
                          "bosses.xml")  # data\gamedata\gameobjects\bosses.xml
GADGETS_XML = os.path.join("data", "gamedata", "gameobjects",
                           "gadgets.xml")  # data\gamedata\gameobjects\gadgets.xml
WARES_XML = os.path.join("data", "gamedata", "gameobjects",
                         "wares.xml")  # data\gamedata\gameobjects\wares.xml
QUEST_ITEMS_XML = os.path.join("data", "gamedata", "gameobjects",
                               "questitems.xml")  # data\gamedata\gameobjects\questitems.xml
BREAKABLE_OBJ_XML = os.path.join("data", "gamedata", "gameobjects",
                                 "breakableobjects.xml")  # data\gamedata\gameobjects\breakableobjects.xml
TOWNS_XML = os.path.join("data", "gamedata", "gameobjects",
                         "towns.xml")  # \data\gamedata\gameobjects\gameobjects.xml
VEHICLES_XML = os.path.join("data", "gamedata", "gameobjects",
                            "vehicles.xml")  # data\gamedata\gameobjects\vehicles.xml
VEHICLE_PARTS_XML = os.path.join("data", "gamedata", "gameobjects",
                                 "vehicleparts.xml")  # data\gamedata\gameobjects\vehicleparts.xml
PREFABS_XML = os.path.join("data", "gamedata", "gameobjects",
                           "prefabs.xml")  # data\gamedata\gameobjects\prefabs.xml
# guns - listed as folder in gameobjects.xml
SMALL_GUNS_XML = os.path.join("data", "gamedata", "gameobjects",
                              "smallguns.xml")  # data\gamedata\gameobjects\smallguns.xml
BIG_GUNS_XML = os.path.join("data", "gamedata", "gameobjects",
                            "bigguns.xml")  # data\gamedata\gameobjects\bigguns.xml
GIANT_GUNS_XML = os.path.join("data", "gamedata", "gameobjects",
                              "giantguns.xml")  # data\gamedata\gameobjects\giantguns.xml
SIDE_GUNS_XML = os.path.join("data", "gamedata", "gameobjects",
                             "sideguns.xml")  # data\gamedata\gameobjects\sideguns.xml
GUNS_XML_DICT = {"small_guns": SMALL_GUNS_XML, "big_guns": BIG_GUNS_XML,
                 "giant_guns": GIANT_GUNS_XML, "side_guns": SIDE_GUNS_XML}

# maps folder
DYNAMIC_SCENE_XML = os.path.join("data", "maps", MAP_NAME,
                                 "dynamicscene.xml")  # data/maps/r1m1/dynamicscene.xml
OBJECT_NAMES_XML = os.path.join("data", "maps", MAP_NAME,
                                "object_names.xml")  # data/maps/r1m1/object_names.xml
TOWN_BACKGROUND_XML = os.path.join("data", "maps", MAP_NAME,
                                   "icons.xml")  # data/maps/r1m1/icons.xml
TRIGGERS_XML = os.path.join("data", "maps", MAP_NAME,
                            "triggers.xml")  # data/maps/r1m1/triggers.xml
CINEMA_TRIGGERS_XML = os.path.join("data", "maps", MAP_NAME,
                                   "cinematriggers.xml")  # data/maps/r1m1/cinematriggers.xml

# models folder
BELONG_LOGO_XML = os.path.join("data", "models",
                               "belongstologos.xml")  # "data\models\belongstologos.xml
LOGOS_GAM = os.path.join("data", "models", "logos",
                         "logos.gam")  # "data\models\logos\logos.gam"

# sounds folder
RADIO_SOUNDS_XML = os.path.join("data", "sounds", "radio",
                                "radiosounds.xml")  # "data\sounds\radio\radiosounds.xml
DIALOGS_GLOBAL_XML = os.path.join("data", "if", "diz",
                                  "dialogsglobal.xml")  # data\if\diz\dialogsglobal.xml

# if/strings folder
OBJECT_DESCR_XML = os.path.join("data", "if", "strings",
                                "objectdiz.xml")  # "data\if\strings\objectdiz.xml
CLANDIZ_XML = os.path.join("data", "if", "strings",
                           "clansdiz.xml")  # data/if/strings/clansdiz.xml
UI_EDIT_STRINGS_XML = os.path.join("data", "if", "strings",
                                   "uieditstrings.xml")  # data/if/strings/uieditstrings.xml
AFFIXES_STRINGS_XML = os.path.join("data", "if", "strings",
                                   "affixesdiz.xml")  # "data\if\strings\affixesdiz.xml


# if/ico folder
MODEL_ICONS_XML = os.path.join("data", "if", "ico",
                               "modelicons.xml")  # data/if/ico/modelicons.xml map with name

# if/diz folder
MODEL_NAMES_XML = os.path.join("data", "if", "diz",
                               "model_names.xml")  # data\if\diz\model_names.xml
QUEST_INFO_GLOB_XML = os.path.join("data", "if", "diz",
                                   "questinfoglobal.xml")  # data\if\diz\questinfoglobal.xml


GOBJ_PROPERTIES = {"BELONG": 0x0,
                   "PROTOTYPE_NAME": 0x1,
                   "PROTOTYPE_ID": 0x2,
                   "NAME": 0x3,
                   "POSITION": 0x4,
                   "ROTATION": 0x5,
                   "MASS": 0x6,
                   "NODE_SCALE": 0x7,
                   "AICONTROLLED": 0x8,
                   "FUEL": 0x9,
                   "MAX_FUEL": 0xA,
                   "MONEY": 0xB,
                   "DRIFT_COEFF": 0xC,
                   "GADGET_ANTI_MISSILE_RADIUS": 0xD,
                   "REMOVE_WHEN_CHILDREN_DEAD": 0xE,
                   "TEAMTACTIC_PROTOTYPE": 0xF,
                   "TEAMTACTIC_SHOULD_BE_ASSIGNED": 0x10,
                   "PART_TYPE": 0x11,
                   "ARMOR": 0x12,
                   "DURABILITY": 0x13,
                   "MAX_DURABILITY": 0x14,
                   "PRICE": 0x15,
                   "MAX_TORQUE": 0x16,
                   "MAX_SPEED": 0x17,
                   "FUEL_CONSUMPTION": 0x18,
                   "CONTROL": 0x19,
                   "HEALTH": 0x1A,
                   "MAX_HEALTH": 0x1B,
                   "DAMAGE": 0x1C,
                   "FIRING_RATE": 0x1D,
                   "FIRING_RANGE": 0x1E,
                   "ACCURACY": 0x1F,
                   "WITH_CHARGING": 0x20,
                   "WITH_CHARGE_LIMIT": 0x21,
                   "CHARGE_SIZE": 0x22,
                   "RECHARGING_TIME": 0x23,
                   "SHELLS_IN_POOL": 0x24,
                   "CHARGES": 0x25,
                   "CHARGE_STATE": 0x26,
                   "CURRENT_CHARGE_TIME": 0x27,
                   "ITEMS_IN_CURRENT_CHARGE": 0x28,
                   "SLOT_NUM": 0x29,
                   "GIVING_QUESTS": 0x2A,
                   "DISCUSSING_QUESTS": 0x2B,
                   "MODEL_NAME": 0x2C,
                   "MODEL_SKIN": 0x2D,
                   "MODEL_CONFIGURATION": 0x2E,
                   "HELLO_REPLIES": 0x2F,
                   "NPC_TYPE": 0x30,
                   "RADIUS": 0x31,
                   "TARGET_CLASSES": 0x32,
                   "TOLERANCE": 0x33,
                   "LOOKINGTIMEOUT": 0x34,
                   "ACTIVE": 0x35,
                   "PASSAGE_ADDRESS": 0x36,
                   "CORRESPONDING_PASSAGE_LOCATION_NAME": 0x37,
                   "PASSAGE_ACTIVE": 0x38,
                   "TARGET_NAME": 0x39,
                   "HIRER_NAME": 0x3A,
                   "QUEST_STATUS": 0x3B,
                   "REWARD": 0x3C,
                   "HUNT_FRAGS_AT_START": 0x3D,
                   "HUNT_START_TIME": 0x3E,
                   "MAX_ITEMS": 0x3F,
                   "MAX_DEFENDERS": 0x40,
                   "OPEN_GATE_TO_PLAYER": 0x41,
                   "MAX_ATTACKERS": 0x42,
                   "PROBABILITY": 0x43,
                   "WAVE_FORCE_INTENSITY": 0x44,
                   "WAVE_DAMAGE_INTENSITY": 0x45,
                   "MIN_DIST_TO_PLAYER": 0x46,
                   "CRITICAL_TEAM_DIST": 0x47,
                   "CRITICAL_TEAM_TIME": 0x48,
                   "INFECTION_TEAM_PROTOTYPE_NAME": 0x49,
                   "DROPOUT_TIMEOUT": 0x4A,
                   "PLACE_POSITION": 0x4B,
                   "PORT_POSITION": 0x4C,
                   "PATHS_NAMES": 0x4D,
                   "CLASS_NAME": 0x4E}

TEXTURE_TYPE = {"DIFFUSE": 0x0,
                "BUMP": 0x1,
                "LIGHTMAP": 0x2,
                "CUBEMAP": 0x3,
                "DETAIL": 0x4}

MESH_TYPE = {"SKINED_MESH": 0x2,
             "TRI_MESH": 0x1,
             "LOAD_POINT": 0x3,
             "STATIC_MESH": 0x4}

TOLLERANCE = {"RS_ENEMY": 0x1,
              "RS_NEUTRAL": 0x2,
              "RS_ALLY": 0x3,
              "RS_OWN": 0x4,
              "RS_MAX": 0x5}

BUILDING_TYPE = {"ADMINISTRATION": 0x0,
                 "BAR": 0x1,
                 "SHOP": 0x2,
                 "WORKSHOP": 0x3,
                 "GARAGE": 0x4,
                 "NUM_BUILDINGTYPES": 0x5,
                 "INVALID_BUILDINGTYPE": 0x5}

ITEM_TYPE = {"GADGET": 0x0,
             "VEHICLE_PART_CABIN": 0x1,
             "VEHICLE_PART_BASKET": 0x2,
             "REPOSITORY_ITEM": 0x3,
             "MAIN_ITEM": 0x4,
             "INVALID": 0x5}

GEOM_TYPE = {"NONE": 0x0,
             "BOX": 0x1,
             "SPHERE": 0x2,
             "CYLINDER": 0x3,
             "RAY": 0x4,
             "TRIMESH": 0x5,
             "FROM_MODEL": 0x6}

GEOM_REPOSITORY_ITEM_TYPE = {"RESOURCE": 0x0,
                             "OBJECT": 0x1}

WORKSHOP_REPOSITORY_TYPE = {"GOODS": 0x0,
                            "CABINS_AND_BASKETS": 0x1,
                            "VEHICLES": 0x2,
                            "GUNS_AND_GADGETS": 0x3,
                            "NUM_TYPES": 0x4}

FIRING_TYPES = {"MACHINE_GUN": 0x0,
                "CANNON": 0x1,
                "SHOT_GUN": 0x2,
                "LASER": 0x3,
                "PLASMA": 0x4,
                "ROCKET": 0x5,
                "ARTILLERY": 0x6,
                "THUNDERBOLT": 0x7,
                "MINE": 0x8,
                "NAIL": 0x9,
                "TURBO": 0xA,
                "OIL": 0xB,
                "SMOKE": 0xC,
                "NUM_FIRING_TYPES": 0xD}

LOCATION_TYPE = {"GENERIC": 0x0,
                 "ENTER": 0x1,
                 "DEFEND": 0x2,
                 "DEPLOY": 0x3,
                 "CARAVAN_ARRIVE": 0x4,
                 "ATTACK": 0x5,
                 "PASSAGE": 0x6}

NPC_TYPE = {"NPC_BARMAN": 0x0,
            "NPC_CLIENT": 0x1}
