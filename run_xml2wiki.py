from flask import Flask
from shutil import copyfile
import xml.etree.ElementTree as ET
from enum import Enum


class MainParseMode(Enum):
    MainTags = 1
    UnitClassTags = 2
    UnitModifierTags = 3


class HEDXml2Wiki():
    def __init__(self):
        self.parent_map = None
        self.current_tag_string = ""
        self.current_tag_extra = ""
        self.parse_mode = MainParseMode.MainTags

    def count_parent_nodes(self, node, tags_to_check=None):
        if tags_to_check is None:
            tags_to_check = ["node"]
        nodes_in_parent = 0
        parent_elem = node
        while parent_elem in self.parent_map:
            if parent_elem.tag in tags_to_check:
                nodes_in_parent += 1
            parent_elem = self.parent_map[parent_elem]

        return nodes_in_parent

    def flush_current_tag(self):
        if self.current_tag_string or self.current_tag_extra:
            if self.current_tag_extra:
                print(f"{self.current_tag_string} <nowiki>{self.current_tag_extra}</nowiki>")
            else:
                print(self.current_tag_string)
            self.current_tag_string = ""
            self.current_tag_extra = ""

    def add_blank_line(self):
        print("")

    def process_tree(self, hed_tree):
        # Create a map so we can go from child to parent easily.
        self.parent_map = {c: p for p in hed_tree.iter() for c in p}
        self.current_tag_string = ""
        self.current_tag_extra = ""

        parse_mode = MainParseMode.MainTags
        for elem in hed_tree.iter():
            if elem.tag == "HED":
                self.current_tag_string = f"HED version: {elem.attrib['version']}"
                self.flush_current_tag()
                self.add_blank_line()
                self.current_tag_string = "!# start hed"
                self.flush_current_tag()
                continue
            elif elem.tag == "unitClasses":
                self.flush_current_tag()
                parse_mode = MainParseMode.UnitClassTags

                section_text_name = "Unit classes"
                self.current_tag_string += "\n"
                self.current_tag_string += f"'''{section_text_name}'''"
                self.add_blank_line()
            elif elem.tag == "unitModifiers":
                self.flush_current_tag()
                parse_mode = MainParseMode.UnitModifierTags

                section_text_name = "Unit modifiers"
                self.current_tag_string += "\n"
                self.current_tag_string += f"'''{section_text_name}'''"
                # self.add_blank_line()

            if self.current_tag_string == "*** Letter":
                breakHEre = 3
            nodes_in_parent = None
            if parse_mode == MainParseMode.MainTags:
                nodes_in_parent = self.count_parent_nodes(elem) - 1
                if elem.tag == "node":
                    self.flush_current_tag()
            elif parse_mode == MainParseMode.UnitClassTags:
                nodes_in_parent = self.count_parent_nodes(elem,
                                                     tags_to_check=["unitClasses", "units"])
                if elem.tag == "unit" or elem.tag == "unitClass":
                    self.flush_current_tag()
            elif parse_mode == MainParseMode.UnitModifierTags:
                nodes_in_parent = self.count_parent_nodes(elem, tags_to_check=["unitModifiers"])
                if elem.tag == "unitModifier":
                    self.flush_current_tag()

            # stuff that applies to all modes
            if elem.tag == "name" or elem.tag == "unit":
                # handle special case where text is just "#"
                if elem.text and "#" in elem.text:
                    if elem.text != "#":
                        breakHEre = 3
                    prefix = "*" * nodes_in_parent
                    self.current_tag_string += f"{prefix}"
                    self.current_tag_extra = f"{elem.text} {self.current_tag_extra}"
                else:
                    if nodes_in_parent == 0:
                        self.current_tag_string += f"'''{elem.text}'''"
                        self.add_blank_line()
                    elif nodes_in_parent > 0:
                        prefix = "*" * nodes_in_parent
                        self.current_tag_string += f"{prefix} {elem.text}"
                    elif nodes_in_parent == -1:
                        self.current_tag_string += elem.tag

            if elem.tag == "description":
                if self.current_tag_extra:
                    self.current_tag_extra += " "
                self.current_tag_extra += f"[{elem.text}]"

            if len(elem.attrib) > 0:
                self.current_tag_extra += "{"
                is_first = True
                sorted_keys = []
                # This is purely optional, but makes comparing easier when it's identical
                expected_key_order = ["takesValue", "isNumeric", "requireChild", "required", "unique",
                                      "predicateType", "position", "unitClass", "default"]
                for expected_key in expected_key_order:
                    if expected_key in elem.attrib:
                        sorted_keys.append(expected_key)
                for attrib_name in elem.attrib:
                    if attrib_name not in sorted_keys:
                        sorted_keys.append(attrib_name)

                for attrib_name in sorted_keys:
                    attrib_val = elem.attrib[attrib_name]
                    if attrib_name == "unitClass":
                        unit_classes = attrib_val.split(",")
                        for unit_class in unit_classes:
                            if not is_first:
                                self.current_tag_extra += ", "
                            is_first = False
                            self.current_tag_extra += f"{attrib_name}={unit_class}"
                    else:
                        if not is_first:
                            self.current_tag_extra += ", "
                        is_first = False
                        if attrib_val == "true":
                            self.current_tag_extra += attrib_name
                        elif attrib_val.isdigit():
                            self.current_tag_extra += f"{attrib_name}={attrib_val}"
                        else:
                            self.current_tag_extra += f"{attrib_name}={attrib_val}"
                self.current_tag_extra += "}"

        self.flush_current_tag()
        self.current_tag_string = "!# end hed"
        self.flush_current_tag()


hed_tree = ET.parse("HED7.1.1.xml")
hed_tree = hed_tree.getroot()
xml2wiki = HEDXml2Wiki()
xml2wiki.process_tree(hed_tree)
