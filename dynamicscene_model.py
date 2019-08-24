import os
import sys
from lxml import etree
from lxml import objectify

DYNAMIC_SCENE_XML = os.path.join(os.path.dirname(__file__), "dummy_files", "dynamicscene.xml")
DYNAMIC_SCENE_CHANGED = os.path.join(os.path.dirname(__file__), "dummy_files", "dynamicscenemod.xml")
DYNAMIC_SCENE_RAW = os.path.join(os.path.dirname(__file__), "dummy_files", "dynamicsceneraw.xml")


def main():
    dynamic_scene_tree = parse_file_to_tree(DYNAMIC_SCENE_XML)
    save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)
    save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_RAW, False)


def parse_file_to_tree(path):
    with open(path, "r") as f:
        objectify.enable_recursive_str()
        objfy = objectify.parse(f)
    objectify_tree = objfy.getroot()

    return objectify_tree


def save_to_file(objectify_tree: objectify.ObjectifiedElement, path, machina_beautify: bool = True):
    '''
    Saves ObjectifiedElement tree to file at path, will format and beautify file
    in the style very similar to original Ex Machina dynamicscene.xml files by
    default. Can skip beautifier and save raw lxml formated file.
    '''
    xml_string = etree.tostring(objectify_tree,
                                pretty_print=True,
                                xml_declaration=True,
                                encoding='windows-1251',
                                standalone=True)
    with open(path, "wb") as writer:
        if machina_beautify:
            writer.write(machina_xml_beautify(xml_string))
        else:
            writer.write(xml_string)


def machina_xml_beautify(xml_string: str):
    ''' Format and beautify xml string in the style very similar to original
    Ex Machina dynamicscene.xml files.'''
    beautified_string = b""
    previous_line_indent = -1

    # As first line of xml file is XML Declaration, we want to exclude it from
    # Beautifier to get rid of checks for every line that it's not a Declaration
    xml_string_first_line = xml_string[:xml_string.find(b"\n<")]

    for i, line in enumerate(xml_string[xml_string.find(b"\n<") + 1:].splitlines()):
        line_stripped = line.lstrip()
        # calculating indentation level of parent line to indent its attributes.
        # lxml use spaces for indents but EM files use tabs, so indents maps 2:1
        line_indent = (len(line) - len(line_stripped)) // 2

        line = _split_tag_on_attributes(line_stripped, line_indent, previous_line_indent)
        # manually tabulating lines according to saved indent level
        line = line_indent * b"\t" + line + b"\n"

        # in EM xmls every first and only first tag of its tree level is
        # separated by a new line
        if line_indent == previous_line_indent:
            line = b"\n" + line

        # we need to know indentation of previous tag to decide if tag is first
        # for its tree level, as described above
        previous_line_indent = line_indent

        beautified_string += line
    return xml_string_first_line + b"\n" + beautified_string


def _split_tag_on_attributes(xml_line: str, line_indent: int,
                             previous_line_indent: int):
    white_space_index = xml_line.find(b" ")
    quotmark_index = xml_line.find(b'"')

    # true when no tag attribute contained in string
    if white_space_index == -1 or quotmark_index == -1:
        return xml_line

    # next tag attribute found
    elif white_space_index < quotmark_index:
        # indent found attribute and recursively start work on next line part
        return (xml_line[:white_space_index] + b"\n" + b"\t" * (line_indent + 1)
                + _split_tag_on_attributes(xml_line[white_space_index + 1:],
                                           line_indent, previous_line_indent))
    # searching where attribute values ends and new attribute starts
    else:
        second_quotmark_index = xml_line.find(b'"', quotmark_index + 1) + 1
        return (xml_line[:second_quotmark_index]
                + _split_tag_on_attributes(xml_line[second_quotmark_index:],
                                           line_indent, previous_line_indent))


if __name__ == "__main__":
    sys.exit(main())
