import os
import sys
import fnmatch
import socket
import getpass
import platform
from pygccxml.parser import load_xml_generator_configuration

this_module_dir_path = os.path.abspath ( os.path.dirname( sys.modules[__name__].__file__) )

xml_generator_config = load_xml_generator_configuration(os.path.join(this_module_dir_path, 'gccxml.cfg'))

class indexing_suite:
    include = os.path.join( this_module_dir_path, 'indexing_suite_v2' )

class boost:
    libdir = '/usr/lib'
    lib = 'boost_python'
    include = '/usr/include'

class python:
    version = 'python%d.%d' % (sys.version_info[0],sys.version_info[1])
    libdir = os.path.join(sys.prefix, 'lib')
    lib = version
    include = os.path.join(sys.prefix, os.path.join('include', version))

class scons:
    suffix = '.so'
    cmd_build = 'scons'
    cmd_clean = 'scons --clean'
    ccflags = []

# attemp to set correct boost and python paths
if 'BOOST_ROOT' in os.environ:
    boost.libdir = os.path.join(os.environ['BOOST_ROOT'], 'lib')
    boost.include = os.path.join(os.environ['BOOST_ROOT'], 'include')
elif not os.path.exists(os.path.join(boost.include, 'boost')):
    # make another guess at where boost is installed
    boost.libdir = '/opt/local/lib'
    boost.include = '/opt/local/include'
    if not os.path.exists(os.path.join(boost.include, 'boost')):
        raise Exception('Cannot find Boost. Use the environment variable BOOST_ROOT')
pysuffixes = [ 'mu', 'm', 'u', 'd', '']
for suffix in pysuffixes:
    path = python.include + suffix
    if os.path.exists(path):
        python.include = path
        break
else:
    raise Exception('Cannot find Python include directory')

libs = os.listdir(python.libdir)
for suffix in pysuffixes:
    if len(fnmatch.filter(libs, '*' + python.lib + suffix + '*')):
        python.lib = python.lib + suffix
        break
else:
    raise Exception('Cannot find Python library')


_my_path = None
try:
    import environment_path_helper
    environment_path_helper.raise_error()
except Exception as error:
    _my_path = os.path.abspath( os.path.split( sys.exc_info()[2].tb_frame.f_code.co_filename )[0])
    if not os.path.exists( os.path.join( _my_path, 'environment.py' ) ):
        #try another guess
        if sys.modules.has_key('environment'):
            _my_path = os.path.split( sys.modules['environment'].__file__ )[0]


sys.path.insert(0, os.path.join( _my_path, '../pygccxml' ))
sys.path.insert(0, os.path.join( _my_path ))
import pygccxml
import pyplusplus
