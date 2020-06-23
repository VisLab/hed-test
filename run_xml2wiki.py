import xml.etree.ElementTree as ET
from xml2wiki import HEDXml2Wiki

hed_tree = ET.parse("HED7.1.1.xml")
hed_tree = hed_tree.getroot()
xml2wiki = HEDXml2Wiki()
xml2wiki.process_tree(hed_tree)
