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

        for elem in hed_tree.iter():
            # stuff that applies to all modes
            if elem.tag == "name" or elem.tag == "unit":
                nodes_in_parent = self.count_parent_nodes(elem) - 1
                # handle special case where text is just "#"
                if elem.text and "#" in elem.text:
                    #prefix = "*" * nodes_in_parent
                    #self.add_tag(elem.text)
                    pass
                    #print(elem.text)
                    # self.current_tag_string += f"{prefix}"
                    # self.current_tag_extra = f"{elem.text} {self.current_tag_extra}"
                else:
                    if nodes_in_parent == 0:
                        self.add_tag(elem.text)

                        #self.current_tag_string += f"'''{elem.text}'''"
                        #self.add_blank_line()
                    elif nodes_in_parent > 0:
                        self.add_tag(elem.text)
                        #prefix = "*" * nodes_in_parent
                        #self.current_tag_string += f"{prefix} {elem.text}"
                    elif nodes_in_parent == -1:
                        self.add_tag(elem.text)
                        #self.current_tag_string += elem.tag

    def add_tag(self, new_tag):
        if new_tag not in self.tag_dict:
            self.tag_dict[new_tag] = [new_tag]
        else:
            self.tag_dict[new_tag].append(new_tag)
            print(f"Duplicate tag found {new_tag}: {len(self.tag_dict[new_tag])}")


hed_tree = ET.parse("HED7.1.1.xml")
hed_tree = hed_tree.getroot()
xml2wiki = TagCompare()
xml2wiki.process_tree(hed_tree)
