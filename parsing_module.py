import sys

# from lxml import objectify

from logger import logger

# from constants import (GLOBAL_PROP_XML, DYNAMIC_SCENE_XML,
#                        OBJECT_NAMES_XML, OBJECT_DESCR_XML,
#                        MODEL_ICONS_XML, MODEL_NAMES_XML,
#                        CLANDIZ_XML, BELONG_LOGO_XML, LOGOS_GAM,
#                        DIALOGS_GLOBAL_XML, RADIO_SOUNDS_XML,
#                        TOWNS_XML, VEHICLE_PARTS_XML, VEHICLES_XML, GUNS_XML_DICT,
#                        PREFABS_XML, BREAKABLE_OBJ_XML, MISC_XML, BOSSES_XML,
#                        AFFIXES_STRINGS_XML, WORKING_DIRECTORY)

from global_properties import theServer


def get_server():
    server = theServer
    return server


# if __name__ == "__main__":
#     sys.exit(main())
