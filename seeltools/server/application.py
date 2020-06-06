import os
from urllib.parse import unquote
# from copy import deepcopy

from seeltools.server.wnd_station import theWndStation
from seeltools.utilities.log import logger
from seeltools.utilities.parse import (xml_to_objfy, check_mono_xml_node,
                                       safe_check_and_set)
from seeltools.utilities.game_path import WORKING_DIRECTORY
# from seeltools.utilities.constants import ZERO_VECTOR


class Application(object):
    def __init__(self):
        pass

    def LoadServers(self, file_name):
        anim_models_alias = "AnimatedModelsServer"
        # static_models_alias = "StaticModelsServer",
        # light_alias = "LightsServer"
        # sprite_alias = "SpritesServer"
        # particles_alias = "ParticlesServer"
        # sounds_alias = "SoundsServer"
        # music_alias = "MusicServer"
        # projectors_alias = "ProjectorsServer"
        # decals_alias = "DecalsServer"
        self.servers = {}  # 9 servers total
        animated_models_server = self.ServerContainer(
            AnimatedModelsServer(),
            anim_models_alias,
            theWndStation.GetStringByStringId(anim_models_alias, "0"))
        self.servers[anim_models_alias] = animated_models_server
        animated_models_server.server.AddAllItems(os.path.join(WORKING_DIRECTORY, "data/models/animmodels.xml"))
        logger.info(f"Loading Servers: {file_name}")

        xml_file_node = xml_to_objfy(file_name)
        if xml_file_node is not None:
            for server_node in xml_file_node.iterchildren():
                server_container = self.servers.get(server_node.tag)
                if server_container is not None:
                    logger.info(f"Loading server :{server_container.name}")
                    server_container.server.ReadFromXmlNode(xml_file_node, server_node)

                else:
                    logger.info(f"Skipping loading unsupported server: {server_node.tag}")
        else:
            logger.error("Load servers: cannot find Servers")

    def LoadAdditionalServers(self, file_name):
        xml_file_node = xml_to_objfy(file_name)
        if xml_file_node is not None:
            for server_node in xml_file_node.iterchildren():
                server_container = self.servers.get(server_node.tag)
                if server_container is not None:
                    logger.debug(f"Loading additional server :{server_container.name}")
                    server_container.server.ReadFromXmlNode(xml_file_node, server_node, warn_on_duplication=False)

                else:
                    logger.debug(f"Skipping loading unsupported server: {server_node.tag}")
        else:
            logger.error("Load servers: cannot find Servers")

    # not original class
    class ServerContainer(object):
        def __init__(self, server, name, description):
            self.server = server
            self.name = name
            self.diz = description


class DataServer(object):
    def __init__(self):
        self.models = []
        self.items_list = []
        self.items_map = {}
        self.valid = 0

    def ReadFromXmlNode(self, xmlFile, xmlNode, warn_on_duplication=True):
        if xmlNode is not None:
            check_mono_xml_node(xmlNode, "Item")
            for item_node in xmlNode.iterchildren(tag="Item"):
                item = self.ServerItem()
                item.id = safe_check_and_set(item.id, item_node, "id")
                item.params = safe_check_and_set(item.params, item_node, "params")
                item.filename = safe_check_and_set(item.filename, item_node, "file")
                if self.items_map.get(item.id) is None:
                    self.items_list.append(item)
                    self.items_map[item.id] = item
                elif warn_on_duplication:
                    path = unquote(xmlFile.base)
                    logger.warning(f"Duplicate server item with id: '{item.id}' encountered in '{path}'")

    def GetItemByName(self, engine_model_name, viaMap=True):
        model_id = self.models.get(engine_model_name)
        if model_id is not None:
            return model_id
        else:
            return -1

    class ServerItem(object):
        def __init__(self):
            self.id = ""
            self.filename = ""
            self.params = ""
            # self.fileWasRead = 0


class MeshMaterialManager(object):
    def __init__(self):
        self.mapBelongToLogo = []
        self.pLogos = 0


class AnimatedModelsServer(DataServer):
    def __init__(self):
        DataServer.__init__(self)
        self.meshMaterialManager = MeshMaterialManager()
        self.meshMaterialManager.pLogos = 0
        self.meshMaterialManager.mapBelongToLogo = {}
        self.tessellate = 1
        self.alreadyCached = 0
        self.models = {}
        self.shadowMan = 0
        self.numShadowingNodes = 0
        self.impostorPs = 0
        self.impostorVs = 0

    # unused original logic
    def AddItems(self, params, model_id):
        item = self.GetItemByName(model_id, False)
        if item == -1:
            proto = self.ParseProto(params)
            if proto == 1:
                xml_file_node = xml_to_objfy(params)
                if xml_file_node.tag == "AnimatedModels":
                    for model_node in xml_file_node.iterchildren(tag="model"):
                        anim_model = self.AnimatedModel()
                        anim_model.model_id = safe_check_and_set(item.id, model_node, "id")
                        # anim_model.params = safe_check_and_set(item.params, model_node, "params")
                        # anim_model.file_name = safe_check_and_set(anim_model.file_name, item.filename, model_node, "file")
                        # anim_model.shadowed = safe_check_and_set(item.filename, model_node, "shadow")
                        # anim_model.winded = safe_check_and_set(item.filename, model_node, "windwavy")
                        # anim_model.tessellate = safe_check_and_set(item.filename, model_node, "tessellate")
                        # anim_model.trackland = safe_check_and_set(item.filename, model_node, "trackland")
                        # anim_model.composite = safe_check_and_set(item.filename, model_node, "composite")
                        # anim_model.passable = safe_check_and_set(item.filename, model_node, "passable")
                        # anim_model.bBoxMin = safe_check_and_set(item.filename, model_node, "bBoxMin")
                        # anim_model.bBoxMax = safe_check_and_set(item.filename, model_node, "bBoxMax")

    def AddAllItems(self, filepath):
        '''Replacement to read all models from animmodels.xml'''
        xml_file_node = xml_to_objfy(filepath)
        if xml_file_node.tag == "AnimatedModels":
            for model_node in xml_file_node.iterchildren(tag="model"):
                anim_model = self.AnimatedModel()
                anim_model.model_id = safe_check_and_set(anim_model.model_id, model_node, "id")
                anim_model.file_name = safe_check_and_set(anim_model.file_name, model_node, "file")
                # ToDo: deprecate check on duplication if not needed
                if self.models.get(anim_model.model_id) is not None:
                    logger.warning(f"Duplicate model found in animmodels.xml with id: '{anim_model.model_id}'")
                self.models[anim_model.model_id] = anim_model

    def ParseProto(string_in: str, paramsPos):
        if len(string_in) < 3:
            logger.warning(f"No protocol found for '{string_in}'")
        paramsPos = string_in.find(":")
        if paramsPos == -1:
            logger.warning(f"No protocol found for '{string_in}'")
        elif string_in.find("new") == 0:
            return 2
        elif string_in.find("file") == 0:
            return 1

    class AnimatedModel(object):
        def __init__(self):
            self.model_id = ""
            self.file_name = ""
            # self.params
            # self.shadowed = 0
            # self.winded = 0
            # self.tessellate = 0
            # self.trackland = 0
            # self.bBoxMin = deepcopy(ZERO_VECTOR)
            # self.bBoxMax = deepcopy(ZERO_VECTOR)

        def GetLoadPointIdByName(xmlNode, strLoadPointForLoad):
            pass
