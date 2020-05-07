import os
from lxml import etree, objectify
from html import unescape
from urllib.parse import unquote

from seeltools.utilities.game_path import WORKING_DIRECTORY
from seeltools.utilities.log import logger

ENCODING = 'windows-1251'


def parse_logos_gam(path: str):
    logo_list = []
    with open(path, 'rb') as f:
        str_from_file = f.read()
    logo_list_raw = str_from_file.split(b'.dds')
    for byte_str in logo_list_raw:
        logo_list.append(byte_str[byte_str.rindex(b'\x00') + 1:].decode('latin-1'))
    return logo_list


def xml_to_objfy(path_to_file: str):
    full_path = os.path.join(WORKING_DIRECTORY, path_to_file)
    with open(full_path, 'r', encoding=ENCODING) as f:
        parser_recovery = objectify.makeparser(recover=True, encoding=ENCODING, collect_ids=False)
        objectify.enable_recursive_str()
        objfy = objectify.parse(f, parser_recovery)
    objectify_tree = objfy.getroot()

    # for obj in objectify_tree.iterchildren():
    #     tag_object_tree(obj, objectify_tree.tag)
    return objectify_tree


def parse_config(xml_file):
    config = {}
    tree = xml_to_objfy(xml_file)
    if tree.tag == 'config':
        config_entries = tree.attrib
        for entry_name in config_entries:
            if config.get(entry_name) is None:
                config[entry_name] = config_entries[entry_name]
            else:
                logger.warning(f"There is a duplicate config value with name: {entry_name}, "
                               f"will be using last available value for the name.")
            config[entry_name] = config_entries[entry_name]
        return config
    else:
        raise NameError("Config should contain config tag with config entries as attributes!")


def read_from_xml_node(xml_node: objectify.ObjectifiedElement, attrib_name: str, do_not_warn: bool = False):
    attribs = xml_node.attrib
    if attribs:
        prot = attribs.get(attrib_name)
        if prot is not None:
            return prot
        else:
            if not do_not_warn:
                logger.warning(f"There is no attrib with the name: {attrib_name} "
                               f"in a tag {xml_node.tag} of {xml_node.base}")
            return None

    else:
        logger.warning(f"Node {xml_node.tag} of {xml_node.base} is empty!")
        if xml_node.tag == "comment":
            log_comment(xml_node, xml_node.getparent())
        return None


def is_xml_node_contains(xml_node: objectify.ObjectifiedElement, attrib_name: str):
    attribs = xml_node.attrib
    if attribs:
        return attribs.get(attrib_name) is not None
    else:
        logger.warning(f"Asking for attributes of node without attributes: {xml_node.base}")


def child_from_xml_node(xml_node: objectify.ObjectifiedElement, child_name: str, do_not_warn: bool = False):
    try:
        return xml_node[child_name]
    except AttributeError:
        if not do_not_warn:
            logger.warning(f"There is no child with name {child_name} for xml node {xml_node.tag} in {xml_node.base}")
        return None


def check_mono_xml_node(xml_node: objectify.ObjectifiedElement, expected_child_name: str,
                        ignore_comments: bool = False):
    children = xml_node.getchildren()
    if len(children) > 0:
        for child in children:
            if child.tag != expected_child_name:
                if child.tag == "comment" and not ignore_comments:
                    comment = unescape(str(etree.tostring(child))).strip("b'<!-- ").strip(" -->'")
                    path = unquote(xml_node.base).replace(f'file:/{WORKING_DIRECTORY}', '')
                    logger.debug(f"Comment '{comment}' "
                                 f"in tag: '{xml_node.tag}'' "
                                 f"in file: {path}.")
                else:
                    logger.warning(f"Unexpected node with a name {child.tag} found "
                                   f"in xml node: {xml_node.tag} in {xml_node.base}!")
    else:
        logger.error(f"Empty node with a name {xml_node.tag} when expecting to find child "
                     f"nodes with a name {expected_child_name} in {xml_node.base}")


def log_comment(comment_node: objectify.ObjectifiedElement, parent_node: objectify.ObjectifiedElement):
    comment = unescape(str(etree.tostring(comment_node))).strip("b'<!-- ").strip(" -->'")
    path = unquote(parent_node.base).replace(f'file:/{WORKING_DIRECTORY}', '')
    logger.debug(f"Comment '{comment}' "
                 f"in tag: '{parent_node.tag}'' "
                 f"in file: {path}.")


def parse_str_to_bool(string: str):
    if string is None:
        return False
    if string.lower() == "true" or string == "1":
        return True
    elif string.lower() == "false" or string == "0":
        return False
    else:
        logger.warning(f"Invalid str passed to parse to bool: '{string}'")
        return False


def parse_str_to_vector(string: str):
    if string is not None:
        split_str = string.split()
    else:
        split_str = []
    # default in case string is not valid
    dictionary = {"x": 0.0,
                  "y": 0.0,
                  "z": 0.0}
    if len(split_str) == 3:
        dictionary = {"x": float(split_str[0]),
                      "y": float(split_str[1]),
                      "z": float(split_str[2])}
    elif split_str:
        logger.warn(f"Expected 3 vector attributes: {string} were given")

    return dictionary


def parse_str_to_quaternion(string: str):
    if string is not None:
        split_str = string.split()
    else:
        split_str = []
    # default in case string is not valid
    dictionary = {"x": 0.0,
                  "y": 0.0,
                  "z": 0.0,
                  "w": 1.0}
    if len(split_str) == 4:
        dictionary = {"x": float(split_str[0]),
                      "y": float(split_str[1]),
                      "z": float(split_str[2]),
                      "w": float(split_str[3])}
    elif split_str:
        logger.warn(f"Expected 4 quaternion attributes: {string} were given")
    return dictionary


def safe_check_and_set(property_default_value, xmlNode, name_to_check, convert_type=None, do_not_warn=True):
    value_from_xml = read_from_xml_node(xmlNode, name_to_check, do_not_warn)
    if value_from_xml is not None:
        if convert_type is None:
            return value_from_xml
        elif convert_type == "float":
            return float(value_from_xml)
        elif convert_type == "int":
            return int(value_from_xml)
    else:
        return property_default_value
