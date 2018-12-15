import utils
import collections

from lxml import etree as ET


def XMLSerialize(listOfData):
    rootDict = collections.OrderedDict(
        {
            'ts' : "1493453326772",
            'uri': "http://fxldemo.tornado.no/",
            'launch': "no.tornado.FxlDemo"
        }
    )
    root = ET.Element('Application', collections.OrderedDict())
    for data in listOfData:
        root.append(ET.Element('lib', data.getObjDetails()))
    
    tree = ET.ElementTree(root)
    tree.write(utils.get_xml_file(), pretty_print=True, xml_declaration=True, encoding="utf-8", standalone="yes")




# root.append(ET.Element('lib', collections.OrderedDict([
#     ('ts', '1493453326772'),
#     ('uri', "http://fxldemo.tornado.no/"),
#     ('launch',"no.tornado.FxlDemo")])
#     ))
# # main = ET.SubElement(level1, 'Text')
# # main.text = 'Thanks for contributing an answer to Stack Overflow!'
# # second = ET.SubElement(level1, 'Tokens')
# # level2 = ET.SubElement(second, 'Token', word=u"low")


# # level3 = ET.SubElement(level2, 'Morph')
# # second1 = ET.SubElement(level3, 'Lemma')
# # second1.text = 'sdfs'
# # second1 = ET.SubElement(level3, 'info')
# # second1.text = 'qw'

# # level4 = ET.SubElement(level3, 'Aff')
# # second1 = ET.SubElement(level4, 'Type')
# # second1.text = 'sdfs'
# # second1 = ET.SubElement(level4, 'Suf')
# # second1.text = 'qw'


