import argparse
import os
import sys

from server import server_init
from utilities.log import logger

from machina_fileops import xml_to_objfy, child_from_xml_node, read_from_xml_node
common_servers_path = r""


def main(options):
    dyn_scene_path = os.path.join(options.map_dir, "dynamicscene.xml")
    servers_path = os.path.join(options.map_dir, "servers.xml")
    world_path = os.path.join(options.map_dir, "world.xml")

    dyn_scene = xml_to_objfy(dyn_scene_path)
    servers = xml_to_objfy(servers_path)
    world = xml_to_objfy(world_path)

    server = server_init.theServer
    prots = server.thePrototypeManager.prototypesMap

    prots_used = []
    prots_unused = []

    server_items = {}

    anim_models = child_from_xml_node(servers, "AnimatedModelsServer")
    for item in child_from_xml_node(anim_models, "Item"):
        name = read_from_xml_node(item, "id")
        if server_items.get(name) is None:
            server_items[name] = ''

    for node in world.iterchildren(tag="Node"):
        name = read_from_xml_node(node, "name", do_not_warn=True)
        model_id = read_from_xml_node(node, "id", do_not_warn=True)
        if model_id is not None:
            in_servers = server_items.get(model_id)
            if in_servers is None:
                logger.error(f"No model in servers for '{name}-{model_id}'")
            else:
                server_items[model_id] = f"{model_id}-{name}"
        else:
            for inner_node in node.iterchildren(tag="Node"):
                name = read_from_xml_node(inner_node, "name", do_not_warn=True)
                model_id = read_from_xml_node(inner_node, "id", do_not_warn=True)
                if model_id is not None:
                    in_servers = server_items.get(model_id)
                    if in_servers is None:
                        logger.error(f"No model in servers for '{name}-{model_id}'")
                    else:
                        server_items[model_id] = f"{model_id}-{name}"


    for obj in child_from_xml_node(dyn_scene, "Object"):
        name = read_from_xml_node(obj, "Name", do_not_warn=True)
        prot_name = read_from_xml_node(obj, "Prototype")
        if name is None and prot_name not in ["Cable", "Cable_1"]:
            logger.warning(f"No name for object of prot {prot_name}")

        prot = prots.get(prot_name)
        if prot is not None:
            has_model = hasattr(prot, "engineModelName")
            if has_model and prot.engineModelName.value is not None:
                in_servers = server_items.get(prot.engineModelName.value)
                if in_servers is None:
                    logger.error(f"WTF no engineModelName '{prot.engineModelName.value}'")
                else:
                    server_items[prot.engineModelName.value] = f"{prot_name}-{name}"

            has_broken_model = hasattr(prot, "brokenModelName")
            if has_broken_model and prot.brokenModelName.value is not None:
                in_servers = server_items.get(prot.brokenModelName.value)
                if in_servers is None and prot.brokenModelName.value != "brokenTest":
                    logger.error(f"WTF no brokenModelName '{prot.brokenModelName.value}'")
                else:
                    server_items[prot.brokenModelName.value] = f"{prot_name}-{name}"

            has_destroyed_model = hasattr(prot, "destroyedModelName")
            if has_destroyed_model and prot.destroyedModelName.value is not None:
                in_servers = server_items.get(prot.destroyedModelName.value)
                if in_servers is None:
                    logger.error(f"WTF no destroyedModelName '{prot.destroyedModelName.value}'")
                else:
                    server_items[prot.destroyedModelName.value] = f"{prot_name}-{name}"
        else:
            logger.warning(f"Cant find prot with a name {prot_name}")

    a = 1


def _init_input_parser():
    parser = argparse.ArgumentParser(description=u'check servers')
    parser.add_argument('-map_dir', help=u'path to map', required=True)

    return parser


if __name__ == '__main__':
    sys.exit(main(_init_input_parser().parse_args()))
