# coding: utf-8
"""
Module **demohelloworld** provides a very simple example of usage of the Pysbs, without using argument file.
"""
from __future__ import unicode_literals
import logging
import time

log = logging.getLogger(__name__)
import os
import sys
import json5
from PIL import Image

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs import python_helpers
from pysbs import context
from pysbs import sbsenum

from pysbs import sbsgenerator
from pysbs.api_decorators import doc_source_code



def createDirectory(directory):
    '''
    创建路径，如果文件夹不存在，就创建
    :param directory (str): 创建文件夹
    :return:
    '''
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


# bridge_data={}
sbs_path = r'D:\bridge\sbs'
sbsar_dir = os.path.join(os.environ['USERPROFILE'],r'Documents\Adobe\Adobe Substance 3D Painter\assets\materials\bridge')
icon_path =os.path.join(os.environ['USERPROFILE'],'.SAT')

createDirectory(sbsar_dir)
createDirectory(icon_path)

class CreateSbsar:
    def __init__(self, bridge):
        self.size = [3,3]
        self.categories = bridge['categories']
        self.name = bridge['folderNamingConvention'].replace(' ', '_')
        self.sbs_path = os.path.join(sbs_path, f'{self.name}.sbs')
        self.previewImage = bridge['previewImage']
        self.mapNameOverride = bridge['mapNameOverride']

        self.components = {}
        for i in bridge['components']:
            self.components[i['type']] = i['path']

        self.aContext = context.Context()
        self.sbsDoc = sbsgenerator.createSBSDocument(self.aContext,
                                                     aFileAbsPath=os.path.join(sbs_path, f'{self.name}.sbs'),
                                                     aGraphIdentifier=self.name)

        self.aGraph = self.sbsDoc.getSBSGraph(aGraphIdentifier=self.name)
        # self.aGraph.setDefaultParentSize(11,11)

        self.textures_type = {'albedo': [{21: 1, 1: self.size}, {1: {0: 0}}, 'BaseColor', 'baseColor', ''],
                              "ao": [{21: 0, 1: self.size}, {5: {0: 0}}, 'Ambient Occlusion', 'ambientOcclusion', ''],
                              "displacement": [{21: 0, 1: self.size, 0: 1}, {9: {0: 0}}, 'Height', 'height', ''],
                              "metalness": [{21: 0, 1: self.size}, {28: {0: 0}}, 'Metallic', 'metallic', ''],
                              "opacity": [{21: 0, 1: self.size}, {2: {0: 0}}, 'Opacity', 'opacity',
                                          'IsChannelsAlpha=true'],
                              "roughness": [{21: 0, 1: self.size}, {15: {0: 0}}, 'Roughness', 'roughness', ''],
                              "normal": [{21: 1, 1: self.size}, {7: {0: 0,1:3}}, 'Normal', 'normal', '']}

        self.textures_resource = []

        self.icon = createDirectory(self.previewImage)




    def is_texture_exist(self, texture):
        if texture in self.components:
            return True
        else:
            return False

    def create_sbs(self):

        for texture_type in self.textures_type:
            print(texture_type)
            if self.is_texture_exist(texture_type):
                texture_resource = self.sbsDoc.createImportedResource(aResourcePath=self.components[texture_type],
                                                                      aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
                texture_resource_path = texture_resource.getPkgResourcePath()
                resource_node = self.aGraph.createBitmapNode(aSBSDocument=self.sbsDoc,
                                                             aResourcePath=texture_resource_path,
                                                             aParameters=self.textures_type[texture_type][0],
                                                             aInheritance={0:0})

                out_node = self.aGraph.createOutputNode(aIdentifier=self.textures_type[texture_type][3],
                                                        aUsages=self.textures_type[texture_type][1])
                self.aGraph.connectNodes(aLeftNode=resource_node, aRightNode=out_node)
                self.aGraph.setUserData(out_node, self.textures_type[texture_type][4])
        self.aGraph.setIcon(self.icon)
        self.sbsDoc.writeDoc()

    def create_sbsar(self):
        if os.path.exists(self.sbs_path):
            os.system(f'sbscooker --inputs {self.sbs_path} --output-path "{sbsar_dir}" --enable-icons')
            if os.path.exists(os.path.join(sbsar_dir,f'{self.name}.sbsar')):
                return True
        else:
            self.create_sbs()
            time.sleep(0.5)
            self.create_sbsar()

    def create_icon(self):
        image = Image.open(self.previewImage)
        r_image = image.resize((128,128))
        r_image_path = os.path.join(icon_path,f'{self.name}.png')
        r_image.save(r_image_path)
        return r_image_path


def run(bridge_data):
    csb = CreateSbsar(bridge_data)
    a = csb.create_sbsar()
    return a