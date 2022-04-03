from lxml import objectify, etree
from html import unescape
import winreg
from urllib.parse import unquote
import logging


ENCODING = 'windows-1251'




WORKING_DIRECTORY = r"S:\SteamLibrary\steamapps\common\Ex Machina Community Remaster"

logging.info(f"'{WORKING_DIRECTORY}': choosen as game working directory")

def machina_xml_beautify(xml_string: str):
    ''' Format and beautify xml string in the style very similar to
    original Ex Machina dynamicscene.xml files.'''
    beautified_string = b""
    previous_line_indent = -1

    # As first line of xml file is XML Declaration, we want to exclude it
    # from Beautifier to get rid of checks for every line down the line
    xml_string_first_line = xml_string[:xml_string.find(b"\n<")]

    for i, line in enumerate(xml_string[xml_string.find(b"\n<")
                             + 1:].splitlines()):
        line_stripped = line.lstrip()
        # calculating indent level of parent line to indent attributes
        # lxml use spaces for indents, game use tabs, so indents maps 2:1
        line_indent = (len(line) - len(line_stripped)) // 2

        line = _split_tag_on_attributes(line_stripped, line_indent)
        # manually tabulating lines according to saved indent level
        line = line_indent * b"\t" + line + b"\n"

        # in EM xmls every first and only first tag of its tree level is
        # separated by a new line
        if line_indent == previous_line_indent:
            line = b"\n" + line

        # we need to know indentation of previous tag to decide if tag is
        # first for its tree level, as described above
        previous_line_indent = line_indent

        beautified_string += line
    return beautified_string


def _split_tag_on_attributes(xml_line: str, line_indent: int):
    white_space_index = xml_line.find(b" ")
    quotmark_index = xml_line.find(b'"')

    # true when no tag attribute contained in string
    if white_space_index == -1 or quotmark_index == -1:
        return xml_line

    elif white_space_index < quotmark_index:
        # next tag attribute found, now indent found attribute and
        # recursively start work on a next line part
        return (xml_line[:white_space_index] + b"\n" + b"\t" * (line_indent + 1)
                + _split_tag_on_attributes(xml_line[white_space_index + 1:],
                                           line_indent))
    else:
        # searching where attribute values ends and new attribute starts
        second_quotmark_index = xml_line.find(b'"', quotmark_index + 1) + 1
        return (xml_line[:second_quotmark_index]
                + _split_tag_on_attributes(xml_line[second_quotmark_index:],
                                           line_indent))

def xml_to_objfy(full_path: str):
    with open(full_path, 'r', encoding=ENCODING) as f:
        parser_recovery = objectify.makeparser(recover=True, encoding=ENCODING, collect_ids=False)
        objectify.enable_recursive_str()
        objfy = objectify.parse(f, parser_recovery)
    objectify_tree = objfy.getroot()
    return objectify_tree

def is_xml_node_contains(xml_node: objectify.ObjectifiedElement, attrib_name: str):
    attribs = xml_node.attrib
    if attribs:
        return attribs.get(attrib_name) is not None
    else:
        logging.warning(f"Asking for attributes of node without attributes: {xml_node.base}")

def save_to_file(objectify_tree: objectify.ObjectifiedElement, path,
                 machina_beautify: bool = True):
    ''' Saves ObjectifiedElement tree to file at path, will format and
    beautify file in the style very similar to original Ex Machina
    dynamicscene.xml files by default. Can skip beautifier and save raw
    lxml formated file.
    '''
    xml_string = etree.tostring(objectify_tree,
                                pretty_print=True,
                                doctype='<?xml version="1.0" encoding="windows-1251" standalone="yes" ?>',
                                encoding="windows-1251")
    with open(path, "wb") as writer:
        if machina_beautify:
            writer.write(machina_xml_beautify(xml_string))
        else:
            writer.write(xml_string)

def read_from_xml_node(xml_node: objectify.ObjectifiedElement, attrib_name: str, do_not_warn: bool = False):
    attribs = xml_node.attrib
    if attribs:
        prot = attribs.get(attrib_name)
        if prot is not None:
            return prot
        else:
            if not do_not_warn:
                logging.warning(f"There is no attrib with the name: {attrib_name} "
                               f"in a tag {xml_node.tag} of {xml_node.base}")
            return None

    else:
        logging.warning(f"Node {xml_node.tag} of {xml_node.base} is empty!")
        if xml_node.tag == "comment":
            log_comment(xml_node, xml_node.getparent())
        return None


def is_xml_node_contains(xml_node: objectify.ObjectifiedElement, attrib_name: str):
    attribs = xml_node.attrib
    if attribs:
        return attribs.get(attrib_name) is not None
    else:
        logging.warning(f"Asking for attributes of node without attributes: {xml_node.base}")


def child_from_xml_node(xml_node: objectify.ObjectifiedElement, child_name: str, do_not_warn: bool = False):
    '''Get child from ObjectifiedElement by name'''
    try:
        return xml_node[child_name]
    except AttributeError:
        if not do_not_warn:
            logging.warning(f"There is no child with name {child_name} for xml node {xml_node.tag} in {xml_node.base}")
        return None


def check_mono_xml_node(xml_node: objectify.ObjectifiedElement, expected_child_name: str,
                        ignore_comments: bool = False):
    children = xml_node.getchildren()
    if len(children) > 0:
        for child in children:
            if child.tag != expected_child_name:
                if child.tag == "comment" and ignore_comments:
                    return
                elif child.tag == "comment":
                    comment = unescape(str(etree.tostring(child))).strip("b'<!-- ").strip(" -->'")
                    path = unquote(xml_node.base).replace(f'file:/{WORKING_DIRECTORY}', '')
                    logging.debug(f"Comment '{comment}' "
                                 f"in tag: '{xml_node.tag}'' "
                                 f"in file: '{path}'.")
                else:
                    logging.warning(f"Unexpected node with a name '{child.tag}' found "
                                   f"in xml node: '{xml_node.tag}' in '{xml_node.base}'!")
    else:
        logging.error(f"Empty node with a name '{xml_node.tag}' when expecting to find child "
                     f"nodes with a name '{expected_child_name}' in '{xml_node.base}'")


def log_comment(comment_node: objectify.ObjectifiedElement, parent_node: objectify.ObjectifiedElement):
    comment = unescape(str(etree.tostring(comment_node))).strip("b'<!-- ").strip(" -->'")
    path = unquote(parent_node.base).replace(f'file:/{WORKING_DIRECTORY}', '')
    logging.debug(f"Comment '{comment}' "
                 f"in tag: '{parent_node.tag}'' "
                 f"in file: {path}.")

