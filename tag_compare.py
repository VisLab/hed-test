import xml.etree.ElementTree as ET

class TagCompare():
    def __init__(self):
        self.parent_map = None
        self.tag_dict = {}

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

    def process_tree(self, hed_tree):
        # Create a map so we can go from child to parent easily.
        self.parent_map = {c: p for p in hed_tree.iter() for c in p}

        self.tag_dict = {}
        current_depth_check = None
        name_stack = []
        for elem in hed_tree.iter():
            if elem.tag == "unitClasses":
                name_stack = []
                self.print_tag_dict()
                self.tag_dict = {}
                current_depth_check = ["unitClasses", "units"]
            elif elem.tag == "unitModifiers":
                name_stack = []
                self.print_tag_dict()
                self.tag_dict = {}
                current_depth_check = ["unitModifiers"]
            if elem.tag == "name" or elem.tag == "unit":
                # handle special case where text is just "#"
                if elem.text and "#" in elem.text:
                    pass
                else:
                    nodes_in_parent = self.count_parent_nodes(elem, current_depth_check)
                    while len(name_stack) >= nodes_in_parent and len(name_stack) > 0:
                        name_stack.pop()
                    name_stack.append(elem.text)
                    full_tag_name = "/".join(name_stack)
                    self.add_tag(elem.text, full_tag_name)

        self.print_tag_dict()

    def add_tag(self, new_tag, full_tag):
        if new_tag not in self.tag_dict:
            self.tag_dict[new_tag] = [full_tag]
        else:
            self.tag_dict[new_tag].append(full_tag)

    def print_tag_dict(self):
        for tag_name in self.tag_dict:
            if len(self.tag_dict[tag_name]) > 1:
                print(f"Duplicate tag found {tag_name}: {len(self.tag_dict[tag_name])}")
                for full_tag in self.tag_dict[tag_name]:
                    print(full_tag)


hed_tree = ET.parse("result_reduced.xml")
hed_tree = hed_tree.getroot()
xml2wiki = TagCompare()
xml2wiki.process_tree(hed_tree)
