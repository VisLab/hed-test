from flask import Flask
from shutil import copyfile


def depth_iterator(parent, tag=None):
    stack = []
    stack.append(iter([parent]))
    while stack:
        e = next(stack[-1], None)
        if e is None:
            stack.pop()
        else:
            stack.append(iter(e))
            if tag == None or e.tag == tag:
                yield (e, len(stack) - 1)


app = Flask(__name__)
with app.app_context():
    from hed.converter import wiki2xml
    from hed.emailer import constants
    app.config.from_object('config.Config')

    hed_wiki_url = app.config[constants.CONFIG_HED_WIKI_URL_KEY]
    result_dict = wiki2xml.convert_hed_wiki_2_xml(hed_wiki_url)
    hed_tree = result_dict['hed_xml_tree']

    # Create a map so we can go from child to parent easily.
    parent_map = {c: p for p in hed_tree.iter() for c in p}

    current_tag_string = ""
    current_tag_extra = ""
    # tree = ET.parse('test.xml')
    for elem, depth in depth_iterator(hed_tree):
        if elem.tag == "unitClasses":
            break
        #print(f"{depth} - {elem.tag} {elem.text} - {elem}")
        nodes_in_parent = 0
        parent_elem = elem
        while parent_elem in parent_map:
            if parent_elem.tag is "node":
                nodes_in_parent += 1
            parent_elem = parent_map[parent_elem]

        if elem.tag == "node":
            if current_tag_string or current_tag_extra:
                if current_tag_extra:
                    print(f"{current_tag_string} <nowiki>{current_tag_extra}</nowiki>")
                else:
                    print(current_tag_string)
                current_tag_string = ""
                current_tag_extra = ""

        if elem.tag == "name" or elem.tag == "HED":
            node_count = nodes_in_parent - 1
            # handle special case
            if elem.text and "#" in elem.text:
                if elem.text != "#":
                    breakHEre = 3
                prefix = "*" * node_count
                current_tag_string += f"{prefix}"
                current_tag_extra = f"{elem.text} {current_tag_extra}"
            else:
                if node_count == 0:
                    current_tag_string += f"'''{elem.text}'''"
                    #print(f"'''{elem.text}'''")
                elif node_count > 0:
                    prefix = "*" * node_count
                    current_tag_string += f"{prefix} {elem.text}"
                    #print(f"{prefix} {elem.text}")
                elif node_count == -1:
                    current_tag_string += "HED"

        if elem.tag == "description":
            if current_tag_extra:
                current_tag_extra += " "
            current_tag_extra += f"[{elem.text}]"
        if len(elem.attrib) > 0:
            current_tag_extra += "{"
            is_first = True
            for attrib_name, attrib_val in elem.attrib.items():
                if not is_first:
                    current_tag_extra += ", "
                is_first = False
                if attrib_val == "true":
                    current_tag_extra += attrib_name
                elif attrib_val.isdigit():
                    current_tag_extra += f"{attrib_name}={attrib_val}"
                else:
                    current_tag_extra += f"{attrib_name}={attrib_val}"
            current_tag_extra += "}"

        #print(f"Nodes in parent tree: {nodes_in_parent - 1}")

    if current_tag_string:
        print(current_tag_string + current_tag_extra)
        current_tag_string = ""
        current_tag_extra = ""

    # for elem in hed_tree.iter():
    #     print(elem)



    xml_location = result_dict[constants.HED_XML_LOCATION_KEY]
    copyfile(xml_location, "result_xml.xml")
