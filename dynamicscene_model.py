import os
import sys
from lxml import etree
from lxml import objectify

DYNAMIC_SCENE_XML = os.path.join(os.path.dirname(__file__), "dummy_files", "dynamicscene.xml")
DYNAMIC_SCENE_CHANGED = os.path.join(os.path.dirname(__file__), "dummy_files", "dynamicscenemod.xml")


def main():
    dynamic_scene_tree = parse_file_to_tree(DYNAMIC_SCENE_XML)
    save_to_file(dynamic_scene_tree, DYNAMIC_SCENE_CHANGED)


def parse_file_to_tree(path):
    with open(path, "r") as f:
        objectify.enable_recursive_str()
        objfy = objectify.parse(f)
    objectify_tree = objfy.getroot()

    return objectify_tree


def save_to_file(objectify_tree: objectify.ObjectifiedElement, path):
    xml_string = etree.tostring(objectify_tree,
                                pretty_print=True,
                                xml_declaration=True,
                                encoding='windows-1251',
                                standalone=True)
    with open(path, "wb") as writer:
        writer.write(xml_attributes_to_new_line(xml_string))


def xml_attributes_to_new_line(xml_string):
    string = b""
    for i, line in enumerate(xml_string.splitlines()):
        line_stripped = line.lstrip()
        line_indent = (len(line) - len(line_stripped)) // 2
        line = split_tag_on_attributes(line_stripped, line_indent)
        string += line_indent * b"\t" + line + b"\n"
        # print(line_indent * b"\t" + line + b"\n")
    return string


def split_tag_on_attributes(xml_line: str, line_indent: int):
    white_space_index = xml_line.find(b" ")
    quotmark_index = xml_line.find(b'"')
    if white_space_index == -1 and quotmark_index == -1 and xml_line != b">" and xml_line.find(b"<") == -1:
        return xml_line + b"\n"
    elif white_space_index == -1 or quotmark_index == -1:
        return xml_line
    elif white_space_index < quotmark_index:
        return xml_line[:white_space_index] + b"\n" + b"\t" * (line_indent + 1) + split_tag_on_attributes(xml_line[white_space_index + 1:], line_indent)
    else:
        second_quotmark_index = xml_line.find(b'"', quotmark_index + 1) + 1
        return xml_line[:second_quotmark_index] + split_tag_on_attributes(xml_line[second_quotmark_index:], line_indent)


if __name__ == "__main__":
    sys.exit(main())
