import utils
import collections
from lxml import etree as ET


def XMLSerialize(listOfData, xmlfile=None):

    rootDict = collections.OrderedDict(
        {
            'ts' : "1493453326772",
            'uri': "http://fxldemo.tornado.no/",
            'launch': "no.tornado.FxlDemo"
        }
    )
    root = ET.Element('Application', rootDict)
    for data in listOfData:
        root.append(ET.Element('lib', data.getObjDetails()))
    
    updating = ET.SubElement(root, 'updateText')
    updating.text = "Updating ..."
    
    updateLabelStyle = ET.SubElement(root, 'updateLabelStyle')
    updateLabelStyle.text = "-fx-font-weight: bold;"

    progressBarStyle = ET.SubElement(root, 'progressBarStyle')
    progressBarStyle.text = "-fx-pref-width: 200;"

    wrapperStyle = ET.SubElement(root, 'wrapperStyle')
    wrapperStyle.text = "-fx-spacing: 10; -fx-padding: 25;"

    parameters = ET.SubElement(root, 'parameters')
    parameters.text = "--myOption=myValue --myOtherOption=myOtherValue"

    cacheDir = ET.SubElement(root, 'cacheDir')
    cacheDir.text = "USERLIB/FxlDemo"

    acceptDowngrade = ET.SubElement(root, 'acceptDowngrade')
    acceptDowngrade.text = "false"
    
    lingeringUpdateScreen = ET.SubElement(root, 'lingeringUpdateScreen')
    lingeringUpdateScreen.text = "false"
    
    if xmlfile:
        xmlfile_path = utils.get_xml_file(xmlfile)
    else:
        xmlfile_path = utils.get_xml_file()
    
    tree = ET.ElementTree(root)
    tree.write(xmlfile_path, pretty_print=True, xml_declaration=True, encoding="utf-8", standalone="yes")
    print "writing to XML file.."