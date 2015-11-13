#! /usr/bin/python
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import subprocess

this_module_dir_path = os.path.abspath ( os.path.dirname( sys.modules[__name__].__file__) )

data_directory = os.path.join( this_module_dir_path, 'data' )
build_directory = os.path.join( this_module_dir_path, 'temp' )
build_dir = build_directory

if not os.path.exists( build_dir ):
    os.mkdir( build_dir )

sys.path.append( os.path.dirname( this_module_dir_path ) )

from environment import scons, boost, python, xml_generator_config, indexing_suite

import pygccxml

class scons_config:
    libs = [ python.lib ]
    libpath =  [ boost.libdir ] + [ python.libdir ]
    cpppath = [ boost.include, python.include, build_directory, data_directory ] #indexing_suite.include ]
    include_dirs = cpppath + [data_directory] + xml_generator_config.include_paths
    if xml_generator_config.compiler == 'msvc9':
        libpath.append( r'C:\Program Files\Microsoft Visual Studio 9.0\VC\lib' )
        libpath.append( r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Lib' )
        include_dirs.append( r'C:\Program Files\Microsoft Visual Studio 9.0\VC\include' )
        include_dirs.append( r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Include' )

    @staticmethod
    def create_sconstruct():
        msvc_compiler = ''
        if 'posix' != os.name:
            msvc_compiler = str( pygccxml.utils.native_compiler.get_version()[1] )
        else:
            scons_config.libs.append( boost.lib )
        code = [
               "import os"
            ,  "import sys"
            , "env = Environment()"
            , "if 'posix' != os.name:"
            , "    env['MSVS'] = {'VERSION': '%s'}" % msvc_compiler
            , "    env['MSVS_VERSION'] = '%s'" % msvc_compiler
            , "    Tool('msvc')(env)"
            , "t = env.SharedLibrary( target=r'%(target)s'"
            , "    , source=[ %(sources)s ]"
            , "    , LIBS=[ %s ]" % ','.join( [ 'r"%s"' % lib for lib in scons_config.libs ] )
            , "    , LIBPATH=[ %s ]" % ','.join( [ 'r"%s"' % path for path in scons_config.libpath ] )
            , "    , CPPPATH=[ %s ]" % ','.join( [ 'r"%s"' % path for path in scons_config.include_dirs] )
            , "    , CCFLAGS=[ %s ]" % ','.join( [ 'r"%s"' % flag for flag in scons.ccflags ] )
            , "    , SHLIBPREFIX=''"
            , "    , SHLIBSUFFIX='%s'" % scons.suffix #explicit better then implicit
            , ")" ]
            #~ , "if 'linux' not in sys.platform:"
            #~ , "    env.AddPostAction(t, 'mt.exe -nologo -manifest %(target)s.pyd.manifest -outputresource:%(target)s.pyd;2'  )" ]
        return os.linesep.join( code )

    @staticmethod
    def compile( cmd, cwd=build_directory ) :
        print('\n' + cmd)
        process = subprocess.Popen( args=cmd
                                    , shell=True
                                    , stdin=subprocess.PIPE
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT
                                    , cwd=cwd )
        process.stdin.close()

        while process.poll() is None:
            line = process.stdout.readline().decode('utf-8')
            if line.strip():
                print(line.rstrip())
        for line in process.stdout.readlines():
            if line.strip():
                print(line.rstrip())
        if process.returncode:
            raise RuntimeError( "unable to compile extension. See output for the errors." )


#I need this in order to allow Python to load just compiled modules
sys.path.append( build_dir )

os.chdir( build_dir )

if 'nt' == os.name:
    PATH = os.environ.get( 'PATH', '' )
    PATH=PATH + ';' + ';'.join( scons_config.libpath )
    os.environ['PATH'] = PATH
