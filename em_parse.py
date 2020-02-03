from lxml import etree, objectify
from em_classes import ClanClass

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


def xml_to_objfy(path: str):
    with open(path, 'r', encoding=ENCODING) as f:
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
