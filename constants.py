import os

GAME_FOLDER = "D:/Steam/steamapps/common/Hard Truck Apocalypse"

MAP_NAME = "r1m2"

# gamedata folder
GLOBAL_PROP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                               "globalproperties.xml")  # data\gamedata\globalproperties.xml"
RELATIONSHIP_XML = os.path.join(GAME_FOLDER, "data", "gamedata",
                                "relationship.xml")  # data/gamedata/relationship.xml
# gamedata/gameobjects
GAME_OBJECTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                "gameobjects.xml")  # \data\gamedata\gameobjects\gameobjects.xml
TOWNS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                         "towns.xml")  # \data\gamedata\gameobjects\gameobjects.xml
VEHICLES_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                            "vehicles.xml")  # data\gamedata\gameobjects\vehicles.xml
VEHICLE_PARTS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                 "vehicleparts.xml")  # data\gamedata\gameobjects\vehicleparts.xml
PREFABS_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                           "prefabs.xml")  # data\gamedata\gameobjects\prefabs.xml
BREAKABLE_OBJ_XML = os.path.join(GAME_FOLDER, "data", "gamedata", "gameobjects",
                                 "breakableobjects.xml")  # data\gamedata\gameobjects\breakableobjects.xml
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
                                 "dynamicscene.xml")
OBJECT_NAMES_XML = os.path.join(GAME_FOLDER, "data", "maps", MAP_NAME,
                                "object_names.xml")  # data/maps/r1m1/object_names.xml

# models folder
BELONG_LOGO_XML = os.path.join(GAME_FOLDER, "data", "models",
                               "belongstologos.xml")  # "data\models\belongstologos.xml"
LOGOS_GAM = os.path.join(GAME_FOLDER, "data", "models", "logos",
                         "logos.gam")  # "data\models\logos\logos.gam"

# sounds folder
RADIO_SOUNDS_XML = os.path.join(GAME_FOLDER, "data", "sounds", "radio",
                                "radiosounds.xml")  # "data\sounds\radio\radiosounds.xml"
DIALOGS_GLOBAL_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                                  "dialogsglobal.xml")  # data\if\diz\dialogsglobal.xml

# if/strings folder
OBJECT_DESCR_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                                "objectdiz.xml")  # "data\if\strings\objectdiz.xml"
CLANDIZ_XML = os.path.join(GAME_FOLDER, "data", "if", "strings",
                           "clansdiz.xml")  # data/if/strings/clansdiz.xml

# if/ico folder
MODEL_ICONS_XML = os.path.join(GAME_FOLDER, "data", "if", "ico",
                               "modelicons.xml")  # data/if/ico/modelicons.xml map with name

# if/diz folder
MODEL_NAMES_XML = os.path.join(GAME_FOLDER, "data", "if", "diz",
                               "model_names.xml")  # data\if\diz\model_names.xml
