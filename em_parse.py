import os
from warnings import warn
from lxml import etree, objectify

from em_classes import ClanClass
from constants import WORKING_DIRECTORY

ENCODING = 'windows-1251'


def parse_logos_gam(path: str):
    logo_list = []
    with open(path, 'rb') as f:
        str_from_file = f.read()
    logo_list_raw = str_from_file.split(b'.dds')
    for byte_str in logo_list_raw:
        logo_list.append(byte_str[byte_str.rindex(b'\x00') + 1:].decode('latin-1'))
    return logo_list


def objfy_to_dict(element: objectify.ObjectifiedElement):
    if element.tag == 'Object':
        return element.attrib['Name'], \
            dict(map(objfy_to_dict, element)) or element.attrib
    elif element.tag == 'string':
        return element.attrib['id'], \
            dict(map(objfy_to_dict, element)) or element.attrib['value']
    elif element.tag == 'Belong':
        return element.attrib['id'], \
            dict(map(objfy_to_dict, element)) or element.attrib['logo']
    elif element.tag == 'set':
        return f'{element.attrib["forwhom"]}_{element.attrib["tolerance"]}', \
            dict(map(objfy_to_dict, element)) or element.attrib
    elif element.tag == 'Group' or element.tag == 'Reply':
        return element.attrib['name'], \
            dict(map(objfy_to_dict, element)) or element.attrib
    elif (element.tag == 'Sound' or element.tag == 'Item'):
        return element.attrib['id'], \
            dict(map(objfy_to_dict, element)) or element.attrib
    else:
        return element.tag, \
            dict(map(objfy_to_dict, element)) or element.attrib


def xml_to_dict(path: str):
    dictionary = ()
    try:
        with open(path, 'r', encoding=ENCODING) as f:
            str_from_file = f.read().encode(ENCODING)
            parser = etree.ETCompatXMLParser(encoding=ENCODING)
            objectify.enable_recursive_str()
        objfy = objectify.fromstring(str_from_file, parser)
        dictionary = objfy_to_dict(objfy)
    except FileNotFoundError:
        print(f"xml {path} is missing!")
        dictionary = ['', {}]
    return dictionary[1]


def parse_belong_faction_to_dict(path: str):
    dictionary = ()
    with open(path, 'r', encoding=ENCODING) as f:
        str_from_file = f.read().encode(ENCODING)
        parser = etree.ETCompatXMLParser(encoding=ENCODING)
        objectify.enable_recursive_str()
    objfy = objectify.fromstring(str_from_file, parser)
    dictionary = {}
    for child in objfy.iterchildren():
        for belong in child.attrib['belongs'].split():
            dictionary[belong] = child.attrib['name']
    return dictionary


def xml_to_objfy(path_to_file: str):
    full_path = os.path.join(WORKING_DIRECTORY, path_to_file)
    with open(full_path, 'r', encoding=ENCODING) as f:
        parser_recovery = objectify.makeparser(recover=True)
        objectify.enable_recursive_str()
        objfy = objectify.parse(f, parser_recovery)
    objectify_tree = objfy.getroot()

    for obj in objectify_tree.iterchildren():
        tag_object_tree(obj, objectify_tree.tag)
    return objectify_tree


def parse_clans_to_native(structs: dict, dicts: dict):
    tree = {}
    belongs = structs['global_prop']['Belongs'].attrib['Values'].split()
    for belong in belongs:
        tree[belong] = ClanClass(belong, dicts)
    return tree


def obj_to_simple_dict(obj: objectify.ObjectifiedElement, key: str, value: str):
    proto_dict = {}
    for prot in obj.iterchildren():
        if prot.tag == 'comment':
            print('ignoring comment')
        else:
            proto_dict[prot.attrib[key]] = prot.attrib[value]
            # log(f"key[{key}]: {prot.attrib.get(key)}, value[{value}]: {prot.attrib.get(value)}")
    return proto_dict


def tag_object_tree(obj: objectify.ObjectifiedElement, parent: str = ''):
    if obj.countchildren() > 0:
        for obj_ch in obj.iterchildren():
            tag_object_tree(obj_ch, obj.tag)
    # towns.xml uses scheme similar but not exactly matching dynamicscene.xml
    # This solution is a bit shit and it's shit because I don't yet know what the hell in
    # this spagetti of xmls will be needed and what info is relevant for tool's functions.
    # I defenitely will not forget to replace this with more elegant parser /s
    if obj.tag == 'Object' and parent != 'Prototype':
        obj.tag = f'{obj.attrib["Prototype"]}'
    elif obj.tag == 'Folder':
        obj.tag = f'Dir_{obj.attrib["Name"]}'
    elif obj.tag == 'Prototype' and parent == 'Prototypes':
        obj.tag = f'Prot_{obj.attrib["Class"]}'
    # elif obj.tag == 'Type' and parent == 'ResourceTypes':
    #     obj.tag = f'Type_{obj.attrib["Name"]}'


def parse_config(xml_file):
    config = {}
    tree = xml_to_objfy(xml_file)
    if tree.tag == 'config':
        config_entries = tree.attrib
        for entry_name in config_entries:
            if config.get(entry_name) is None:
                config[entry_name] = config_entries[entry_name]
            else:
                warn(f"There is a duplicate config value with name: {entry_name}, "
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
                warn(f"There is no attrib with the name: {attrib_name} "
                     f"in a tag {xml_node.tag} of {xml_node.base}")
            return None

    else:
        warn(f"Node {xml_node.tag} of {xml_node.base} is empty!")
        return None


def is_xml_node_contains(xml_node: objectify.ObjectifiedElement, attrib_name: str):
    attribs = xml_node.attrib
    if attribs:
        return attribs.get(attrib_name) is not None
    else:
        warn(f"Asking for attributes of node without attributes: {xml_node.base}")


def child_from_xml_node(xml_node: objectify.ObjectifiedElement, child_name: str, do_not_warn: bool = False):
    try:
        return xml_node[child_name]
    except AttributeError:
        if not do_not_warn:
            warn(f"There is no child with name {child_name} for xml node {xml_node.tag} in {xml_node.base}")
        return None


def check_mono_xml_node(xml_node: objectify.ObjectifiedElement, expected_child_name: str):
    children = xml_node.getchildren()
    if len(children) > 0:
        for child in children:
            if child.tag != expected_child_name:
                warn(f"Unexpected node with a name {child.tag} found in xml node: {xml_node.tag} in {xml_node.base}!")
    else:
        raise(f"Empty node with a name {child.tag} when expecting to find child nodes with a name {expected_child_name} "
              f"in {xml_node.base}")


def parse_str_to_bool(string: str):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        raise ValueError(f"Invalid str to parse: {string}")
