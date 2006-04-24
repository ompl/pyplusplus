import os
import sys
import getpass

class boost:
    libs = ''
    include = ''

class python:
    libs = ''
    include = ''

class gccxml:
    executable = ''

class scons:
    suffix = ''
    cmd_build = ''
    cmd_clean = ''
    ccflags = []
    
if 'roman' in getpass.getuser():
    
    scons.cmd_build = 'scons --file=%s'
    scons.cmd_clean = 'scons --clean --file=%s'

    if sys.platform == 'win32':
        scons.suffix = '.dll'
        scons.ccflags = ['/MD', '/EHsc', '/GR' ]
        boost.libs = 'd:/boost_cvs/bin'
        boost.include = 'd:/boost_cvs'
        python.libs = 'c:/python/libs'
        python.include = 'c:/python/include'
    else:
        scons.suffix = '.so'
        boost.libs = '/home/roman/boost_cvs/bin'
        boost.include = '/home/roman/boost_cvs'
        python.include = '/usr/include/python2.4'

