from lxml import etree, objectify


def save_to_file(objectify_tree: objectify.ObjectifiedElement, path,
                 machina_beautify: bool = True):
    ''' Saves ObjectifiedElement tree to file at path, will format and
    beautify file in the style very similar to original Ex Machina
    dynamicscene.xml files by default. Can skip beautifier and save raw
    lxml formated file.
    '''
    xml_string = etree.tostring(objectify_tree,
                                pretty_print=True,
                                doctype='<?xml version="1.0" encoding="windows-1251" standalone="yes" ?>')
    with open(path, "wb") as writer:
        if machina_beautify:
            writer.write(machina_xml_beautify(xml_string))
        else:
            writer.write(xml_string)


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
    return xml_string_first_line + b"\n" + beautified_string


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
