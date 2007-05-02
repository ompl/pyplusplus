import sys
import unittest
# Python 2.5
from xml.etree.ElementTree import ElementTree

if ".." not in sys.path:
    sys.path.append("..")

from model.etree_extension import XmlAttribFinder, AttribNotFound
prj_template_file = "../model/ProjectTemplate.xml"


class TestAttribFinder(unittest.TestCase):

    def setUp(self):
        ''' Executed before each test '''
        self._root_el_prj_file = ElementTree(file=prj_template_file).getroot()
    
    def test_find(self):
        '''Test get_val methode with project template'''
        af_obj = XmlAttribFinder(self._root_el_prj_file)
        
        header_path = af_obj.get_val('gccXmlSettings.headerPath')
        self.assertEqual(header_path, "")
        
        inc_path_list = af_obj.get_val('gccXmlSettings.includePathList')
        self.assertEqual(eval(inc_path_list), [])
        
        inc_path_list_obj = af_obj.get_obj('gccXmlSettings.includePathList')

        self.assertTrue(inc_path_list_obj[1], [])
        
        self.assertRaises(AttribNotFound, af_obj.get_val, 
                          ('gccXmlSettings.xxx'))
        
    def tearDown(self):
        ''' Executed after each test '''       
        del self._root_el_prj_file

if __name__ == "__main__":
    unittest.main()
