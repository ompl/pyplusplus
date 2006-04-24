# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

__doc__ = """

This module provides a simplified high-level API for using
pygccxml and pyplusplus.  It is currently under heavy construction.

Quickstart Usage
================

 1. Create an instance of the L{ModuleBuilder} class that serves as main
    entry point for controlling pygccxml and pyplusplus. Parameters for
    configuring pygccxml/pyplusplus can be passed in the constructor::

      from pypp_api import *
   
      mb = ModuleBuilder(...)

 2. Parse the header files using L{parse()<ModuleBuilder.parse>} and
    customize your bindings::

      toplevel_namespace = mb.parse()

      MyClass = toplevel_namespace.Class("MyClass")
      MyClass.expose()

      MyClass.Method("foo").setPolicy(return_internal_reference())
      ...

 3. Write the C++ source files using
    L{writeModule()<ModuleBuilder.writeModule>}::

      mb.writeModule()


Detailed Usage
==============

Add detailed usage here.

@todo: Add quickstart and detailed documentation for API.
@author: Allen Bierbaum
@author: Matthias Baas
@license: Boost Software License, Version 1.0 (see http://www.boost.org/LICENSE_1_0.txt)
@copyright: 2006 Allen Bierbaum, Matthias Baas
"""

import os, os.path, re, time, types

# Bring in everything I need from pyplusplus and pygccxml
from pygccxml import parser
from pygccxml import declarations
from pygccxml.declarations import ACCESS_TYPES
import pygccxml.utils

from pyplusplus import code_creators
from pyplusplus import module_creator
from pyplusplus import file_writers
from pyplusplus import decl_wrappers

# Bring in call policies to use
from pyplusplus.decl_wrappers import return_self
from pyplusplus.decl_wrappers import return_internal_reference
from pyplusplus.decl_wrappers import with_custodian_and_ward
from pyplusplus.decl_wrappers import copy_const_reference
from pyplusplus.decl_wrappers import copy_non_const_reference
from pyplusplus.decl_wrappers import manage_new_object
from pyplusplus.decl_wrappers import reference_existing_object
from pyplusplus.decl_wrappers import return_by_value
from pyplusplus.decl_wrappers import return_opaque_pointer
from pyplusplus.decl_wrappers import return_value_policy

import declwrapper

PUBLIC = ACCESS_TYPES.PUBLIC
PROTECTED = ACCESS_TYPES.PROTECTED
PRIVATE = ACCESS_TYPES.PRIVATE

QUERY = "query"
DECORATION = "decoration"

def cleanTemplateName(templateName):
   """ Build a clean template name. """
   clean_re = re.compile('[:<>\s,]')
   return clean_re.sub('_', templateName)

class ModuleBuilder:
   """Wrapper for a module (or part of a module).
   
   Captures handling of parsing and writing out bindings.
   Note: The public namespace '::' is the root decl for the Module.
   By default all declarations are ignored.

   @group Control methods: parse, buildCreators, writeModule
   @group Customizing output: addInclude, setLicense, Template, addStartText, addEndText, addBodyTailText
   """
   def __init__(self,
                headerFiles = [],
                workingDir = None,
                includePaths = [],
                gccxmlPath = '', 
                defines = [],
                undefines = [],
                cacheFile = None,
                cacheDir = None,
                moduleName = None,
                output = "bindings",
                multiFile = False,
                useScope = False,
                queryLog = None,
                decorationLog = None,
                verbose = True):
      """Initialize module.

      @param headerFiles: The header files to parse
      @type headerFiles: str or list of str
      @param workingDir: directory to start processing.  (default: current working dir)
      @type workingDir: str
      @param includePaths: List of paths to tell gccxml to search for header files.
      @type includePaths: list of str
      @param gccxmlPath: path to gccxml.  If not set then attempt to find it in system path.
      @type gccxmlPath: str
      @param defines: set of symbols to add as defined when compiling.
      @type defines: list of str
      @param undefines: set of symbols to add as undefined when compiling.
      @type undefines: list of str
      @param cacheFile: name of file to use for caching parse data for this module using the file cache.
      @type cacheFile: str
      @param cacheDir: The name of the directory to use for caching parse data using the directory cache.
      @type cacheDir: str
      @param moduleName: The name of the Python module to generate
      @type moduleName: str
      @param output: The output file name or directory
      @type output: str
      @param multiFile: Determines whether the output will be written in one single file or in several files
      @type multiFile: bool
      @param useScope: If true the creators all use scope in their code.
      @type useScope: bool
      @param queryLog: Query log file (file name or file-like object)
      @type queryLog: str or file
      @param decorationLog: Decoration log file (file name or file-like object)
      @type decorationLog: str or file
      @param verbose: if true output status and command information as building the module.
      @type verbose: bool
      """
      if not isinstance(headerFiles, list):
         headerFiles = [headerFiles]
      self.mHeaderFiles = headerFiles
      self.mWorkingDir = workingDir
      if not self.mWorkingDir:
         self.mWorkingDir = os.getcwd()
      self.mIncludePaths = includePaths   # Paths to use for extra includes with gccxml
      self.mGccXmlPath   = gccxmlPath     # Path to gccxml executable
      self.mDefines      = defines        # Defines for gccxml
      self.mUndefines    = undefines
      self.mCacheFile    = cacheFile      # File to use for caching gccxml output
      self.mCacheDir     = cacheDir       # Directory to use for caching
      self.mModuleName = moduleName       # Name of the Python extension module
      self.mOutput = output               # Output file or directory name
      self.mMultiFile = multiFile         # Multi file flag
      self.mUseScope = useScope           # Use scope 
      self.mVerbose      = verbose        # Should there be verbose output during processing
      self.mDeclRoot     = None           # Root of the parsed decls (as declaration_t object)
      self.mDeclRootWrapper = None        # The wrapper around mDeclRoot
      self.mFinalDecls   = None           # Final list of decls to export
      self.mTemplates    = []             # List of (templateType, typedefName) to instantiate
      self.mTypeDefMap   = {}             # Map from typedef name to expanded type
      self.mBodyTailCreators = []         # List of creators to add at body tail
      self.mStartCreators = []            # List of creators to put at beginning of file
      self.mEndCreators = []              # List of custom creators to add on
      self.mExtraIncludes = []            # List of extra includes to add
      self.mLicense       = None          # License to use
      self.mExtModule     = None          # Extension model being built (code creator tree)
      self.mStartTime = None              # Begin of the parsing step
      self.mParseEndTime = None           # The time when parsing was finished

      if queryLog:
         self.log(QUERY, queryLog)
      if decorationLog:
         self.log(DECORATION, decorationLog)
      
      print "Initialized module."

   def log(self, type, logfile):
      """Enable specific logging functionality.

      @param type: Identifies a log stream (QUERY or DECORATION)
      @type type: str
      @param logfile: The output file name or a file-like object
      @type logfile: str or file
      """
      if isinstance(logfile, types.StringTypes):
         logfile = file(logfile, "wt")         
      
      if type==QUERY:
         declwrapper.query_log = logfile
      elif type==DECORATION:
         declwrapper.decoration_log = logfile
      else:
         raise ValueError, "Invalid log stream: %s"%type
      

   def parse(self):
      """ Parse the header files and setup the known declarations.
          Currently this method can only be called once.
          This method can be called anytime after initialization and all Template() calls
          have been made.

          @returns: Returns the root of the declaration tree
          @postcondition: This class can act as a wrapper for namespace("::") and all declarations are set to be ignored.
      """
      if self.mHeaderFiles==[]:
         raise ValueError, "No header files specified"
      
      if self.mVerbose:
         print "Parsing headers: ", self.mHeaderFiles

      # Record the time when parsing started...
      self.mStartTime = time.time()

      # Create and initialize the config object
      parser_cfg = parser.config_t(self.mGccXmlPath,
                                   self.mWorkingDir,
                                   self.mIncludePaths,
                                   define_symbols=self.mDefines,
                                   undefine_symbols=self.mUndefines,
                                   start_with_declarations=None,
                                   verbose=self.mVerbose)

      full_header_list = self.mHeaderFiles[:]
      
      # Handle template instantiation as needed      
      temp_file, temp_filename = (None,None)
      template_instantiation_text = self.buildTemplateFileContents()
      if None != template_instantiation_text:
         temp_filename = pygccxml.utils.create_temp_file_name(suffix=".h")
         temp_file = file(temp_filename, 'w')
         temp_file.write(template_instantiation_text)
         temp_file.close()
         if self.mVerbose:
            print "   creating template instantiation file: ", temp_filename
         full_header_list.append(temp_filename)      

      # Create the cache object...
      if self.mCacheDir!=None:
         if self.mVerbose:
            print "Using directory cache in '%s'"%self.mCacheDir
         cache = parser.directory_cache_t(self.mCacheDir)
      elif self.mCacheFile!=None:
         if self.mVerbose:
            print "Using file cache '%s'"%self.mCacheFile
         cache = parser.file_cache_t(self.mCacheFile)         
      else:
         if self.mVerbose:
            print "No cache in use"
         cache = None

      # Create the parser object...
      the_parser = parser.project_reader_t(config=parser_cfg, 
                                           cache=cache,
                                           decl_factory=decl_wrappers.dwfactory_t())
      # ...and parse the headers
      parsed_decls = the_parser.read_files(full_header_list, 
                                           parser.project_reader.COMPILATION_MODE.FILE_BY_FILE)
      
      assert len(parsed_decls) == 1    # assume that we get root of full tree
      self.mDeclRoot = parsed_decls[0]
      
      # Parse the files and add to decl root
      # - then traverse tree setting everything to ignore
      self.mDeclRootWrapper = DeclWrapper(self.mDeclRoot)      
      self.mDeclRootWrapper.ignore()
      
      # Cleanup
      if temp_filename:
         pygccxml.utils.remove_file_no_raise( temp_filename )
      
      typedef_decls = declarations.make_flatten(parsed_decls)
      typedef_decls = decls = filter( lambda x: (isinstance( x, declarations.typedef_t ) and 
                                                 not x.name.startswith('__') and 
                                                 x.location.file_name != "<internal>")
                                      , typedef_decls )

      self.mTypeDefMap = {}
      for d in typedef_decls:
         type_def_name = d.name
         full_name = declarations.full_name(d)
         if full_name.startswith("::"):    # Remove the base namespace
            full_name = full_name[2:]
         real_type_name = d.type.decl_string
         if real_type_name.startswith("::"):    # Remove base namespace
            real_type_name = real_type_name[2:]   
         self.mTypeDefMap[full_name] = real_type_name

      self.mParseEndTime = time.time()
      if self.mVerbose:
         print "Completed parsing in %s."%self._time2str(self.mParseEndTime-self.mStartTime)

      return self.mDeclRootWrapper


   def buildCreators(self, moduleName=None, filename=None, useScope=None):
      """ Build creator tree and module from the current declarations.
          See writeModule for parameter documentation.
          In normal usage the user will not call this directly.
          Return the base of the creator tree.

          @rtype: module_t
      """
      if None == self.mDeclRoot:
         self.parse()

      if self.mVerbose:
         print "Decoration time:",self._time2str(time.time()-self.mParseEndTime)
      startTime = time.time()

      if moduleName==None:
         moduleName = self.mModuleName
      if moduleName==None:
         raise ValueError, "No output module name given"
      if useScope==None:
         useScope = self.mUseScope

      # Lock the decoration interface (an attempt to decorate after this
      # call will lead to an error)
      declwrapper.decl_lock = True
      
      if self.mVerbose:
         print "Creating module code creator tree...."
         
      # Filter the exposed decl list to create a final decl list.      
#      def filter(decl):
#         expose = getattr(decl, "_expose_flag", False)
#         return expose
      
#      if self.mVerbose:
#         print "Filtering module..."
         
#      self.mFinalDecls = declarations.filtering.user_defined( self.mDeclRoot, filter)

      # The above filtering is already done in pyplusplus as it stores
      # the "ignore" flag itself. [mbaas]
         
      # Create creator.module_t for the module
      # - override the header files in create since we already know what files we used.
      maker = module_creator.creator_t(self.mDeclRoot, module_name=moduleName)      
#      maker = module_creator.creator_t(self.mFinalDecls, module_name=moduleName)      
      extmodule = maker.create(decl_headers=self.mHeaderFiles)

      # Handle the extra creators that need added
      mod_body = extmodule.body
      for c in self.mBodyTailCreators:
         mod_body.adopt_creator(c)
      
      for c in self.mEndCreators:
         extmodule.adopt_creator(c)
         
      self.mStartCreators.reverse()
      for c in self.mStartCreators:
         extmodule.adopt_creator(c, extmodule.last_include_index()+1)
         
      for h in self.mExtraIncludes:
         extmodule.adopt_include(code_creators.include_t(h))
         
      if useScope:
         class_creators = filter( lambda c: isinstance( c, code_creators.class_t )
                                 , code_creators.make_flatten( extmodule.body.creators ) )
         for c in class_creators:
            c.always_expose_using_scope = True #better error reporting from compiler   
      
      if self.mLicense:
         extmodule._set_license(self.mLicense)

      if self.mVerbose:
         print "Code creator tree built in %s"%self._time2str(time.time()-startTime)
         
      self.mExtModule = extmodule
      return self.mExtModule
     
      
   def writeModule(self, moduleName=None, filename=None, useScope=None, 
                    multiFile=None, multiCreateMain=True):
      """ Create the module and write it out.
          Automatically calls createCreators() and filterExposed() if needed.
          
          @param moduleName: The name of the module being created.
          @param filename:   The file or directory to create the code.
          @param useScope:   If true the creators all use scope in their code.
          @param multiFile:  If true use the multifile writer.
          @param multiCreateMain: If true and using multifile then create main reg method.
      """
      if not self.mExtModule:
         self.buildCreators(moduleName, filename, useScope)
      extmodule = self.mExtModule
      assert extmodule

      startTime = time.time()

      if filename==None:
         filename = self.mOutput
      if multiFile==None:
         multiFile = self.mMultiFile

      # Check for missing policies...
      if self.mVerbose:
         print "Sanity check..."
      creators = code_creators.make_flatten(self.mExtModule)
      fmfunctions = filter(lambda creator: isinstance(creator, code_creators.function_t), creators)
      missing_flag = False
      sanity_failed = []
      for creator in fmfunctions:
         if not creator.call_policies:
            print "Missing policy:", declarations.full_name(creator.declaration)
            missing_flag = True
         if not self._declSanityCheck(creator.declaration):
            sanity_failed.append(creator.declaration)
      if len(sanity_failed)>0:
         print "***Warning*** The following %d declarations may produce code that compiles, but"%len(sanity_failed)
         print "that does not have the desired effect in Python:"
         for decl in sanity_failed:
            print " ",decl
      if missing_flag:
         print "*** Aborting because of missing policies!"
         return
      
      if self.mVerbose:
         print "Writing out files (%s)..."%filename
      
      # Write out the file(s)
      if not multiFile:
         file_writers.write_file(extmodule, filename)
      else:
         mfs = file_writers.multiple_files_t(extmodule, filename)
         mfs.write(write_main=multiCreateMain)         
         self.split_header_names = mfs.split_header_names
         self.split_method_names = mfs.split_method_names
         
      if self.mVerbose:
         print "Module written in %s"%self._time2str(time.time()-startTime)
         print "Module generation complete."
         print "Total time: %s"%self._time2str(time.time()-self.mStartTime)
         
         
   # ------------- Creator methods -------------- #      
   def Template(self, templateType, typedefName=None):
      """Add a template to instantiate.
      
      @param templateType: Fully instantiated name.  (ex: TemplateClass<float> )
      @param typedefName:  Name of type def to define to this template type.
          This name can then be used later to look up the real fully
          expanded template type from the typedef map. (see self.mTypeDefMap)
      """
      if not typedefName:
         typedefName = cleanTemplateName(templateType)
      self.mTemplates.append( (templateType, typedefName) )
   
   def addInclude(self, headers):
      """Add additional include file(s).
      
      These are not parsed but are just added to the generated code.
      Takes either a single header or a list of headers.

      @param headers: Header name(s)
      @type headers: str or list of str
      """
      if not isinstance(headers, list):
         headers = [headers]
      self.mExtraIncludes.extend(headers)
      
   def __getattr__(self, name):
      """ Pass through all unfound attributes to the decl wrapper.
      This allows us to act like a decl wrapper on root.
      
      Ex: mod.ignore()
      """
      if hasattr(self.mDeclRootWrapper, name):
         return getattr(self.mDeclRootWrapper, name)
      else:
         raise AttributeError, name  
   
   # --- Advanced methods of adding creators --- #
   # This set of methods needs further refinement based upon user needs
   def addBodyTailText(self, text):
      """Add C++ source code to the module initialization function.

      @param text: A string containing valid C++ source code.
      @type text: str      
      """
      self.addBodyTailCreator(code_creators.custom_text_t(text) )

   def addStartText(self, text):
      """Add C++ source code to the beginning of the main source file.

      @param text: A string containing valid C++ source code.
      @type text: str
      """
      self.addStartCreator(code_creators.custom_text_t(text) )

   def addEndText(self, text):
      """Add C++ source code to the end of the main source file.

      @param text: A string containing valid C++ source code.
      @type text: str
      """
      self.addEndCreator(code_creators.custom_text_t(text) )

   def setLicense(self, licenseText):
      """ Set the license header to use. """
      self.mLicense = licenseText

   def addStartCreator(self, creator):
      self.mStartCreators.append(creator)

   def addBodyTailCreator(self, creator):
      self.mBodyTailCreators.append(creator)

   def addEndCreator(self, creator):
      self.mEndCreators.append(creator)
     
   # ---------- Internal helpers ----------- #
   def buildTemplateFileContents(self):
      """ Build up the contents of a file to instantiate the needed templates.
          headerFiles - List of header files for this module.
      """
      if len(self.mTemplates) == 0:
         return None
      
      content = "/** Autogenerated temporary file for template instantiation. */\n"
      for h in self.mHeaderFiles:
         content += '#include<%s>\n'%h
      
      for t in self.mTemplates:
         template_type = t[0]
         typedef_name = t[1]
         content += """
            typedef %(template_type)s %(typedef_name)s;
            void __instantiate_%(typedef_name)s()
            { sizeof(%(typedef_name)s); }
         """ % vars()
         
      return content

   # _declSanityCheck
   def _declSanityCheck(self, decl):
      """Check if a declaration will produce code that won't work in Python.
      """
      # Check if there's a pointer or reference to a fundamental type among the args...
      args = getattr(decl, "arguments")
      for arg in args:
         t = arg.type
         if isinstance(t, declarations.pointer_t) or isinstance(t, declarations.array_t) or isinstance(t, declarations.reference_t):
            if isinstance(t.base, declarations.fundamental_t) and not (isinstance(t.base, declarations.char_t) or isinstance(t.base, declarations.unsigned_char_t)):
               return False
            
      return True
      

   # _time2str
   def _time2str(self, t):
      """Helper method to convert a time value to a readable string.
      
      @param t: Time value in seconds
      @type t: float
      @returns: The time as a string
      @rtype: str
      """
      if t<60:
         return "%1.0fs"%t
      else:
         min = int(t/60)
         sec = int(t%60)
         if min<60:
            return "%dmin %ds"%(min,sec)
         else:
            h = int(min/60)
            min = int(min%60)
            return "%dh %dmin %ds"%(h,min,sec)


class DeclWrapper:
   """ Class to wrap a single declaration.
       This is the core class for all API exposing.
       Instances of this class are normally created by calling
       one of the creation methods (Namespace, Class, Method, Var, Enum)
       on an existing wrapper or on a module.
      
       @todo: Rewrite methods to use new wrappers.
   """
   def __init__(self, decl):
      """ Construct declaration wrapper for decl. """
      self.mDecl = decl       # The declaration we are wrapping
      
   def Namespace(self, name, expose=False):
      """ Return wrapper for namespace.
          name: full name or regex to match name.
      """
      res = self.findContained(name, declarations.namespace_t)
      if res==None:
         raise RuntimeError, "Namespace '%s' not found"%name
      if expose:
         res.expose()      
      return res   
   
   def Class(self, name, expose=True):
      """ Returns wrapper for class named name. 
          name: full name or regex to match name.
      """
      res = self.findContained(name, declarations.class_t)
      if res==None:
         raise RuntimeError, "Class '%s' not found"%name
      if expose:
         res.expose()
      return res
   
   def Method(self, name, retval=None, args=None, expose=True):
      """ Returns wrapper for method.
          name: full name or regex to match name.
          retval: string rep of return value. None=ignore
          args: list of string rep of arg types. None=ignore
      """
      res = self.findContainedMethod(name, retval, args)
      if res==None:
         raise RuntimeError, "Method '%s' {sig: %s } not found"%(name, [retval,args])
      if expose:
         res.expose()      
      return res
   
   def Var(self, name, expose=True):
      """ Returns wrapper around a varibale.
          name: full name or regex to match the name.
      """
      res = self.findContained(name, declarations.variable_t)
      if res == None:
         raise RuntimeError, "Variable '%s' not found"%name
      if expose:
         res.expose()
      return res
   
   def Enum(self, name, expose=True):
      """ Returns wrapper around an Enum.
          name: full name or regex to match the name.
      """
      res = self.findContained(name, declarations.enumeration_t)
      if res == None:
         raise RuntimeError, "Enum '%s' not found"%name
      if expose:
         res.expose()
      return res

   def ignore(self):
      """ Ignore this declaration.  
          Ignore always acts recursively hidding all declarations under this one.
      """
      for d in iterdecls(self.mDecl, True):
         d.exclude()
      return self
   
   def expose(self, recursive=True):
      """ Expose this declaration.  
          recursive - If True, then expose all under this decl. 
      """
      for d in iterdecls(self.mDecl, recursive):
         d.include()
      return self
         
   def rename(self, newName):
      """ Rename declaration to newName. """
      self.mDecl.rename(newName)
      return self
   
   def setHeldType(self, heldType):
      """ Explicitly set the held type.
          Ex: setHeldType("boost::shared_ptr<Class>")
      """
      self.mDecl.held_type = heldType
      return self
      
   def setCallPolicy(self, callPolicy):
      """ Set the callpolicy of the contained method.
      
          @param callPolicy: Callpolicy object to use (must be of type decl_wrappers.call_policy_t)
      """
      assert isinstance(callPolicy, decl_wrappers.call_policy_t)
      self.mDecl.call_policies = callPolicy
      return self
   
   def finalize(self):
      """ Ask this system to attempt to finalize this declaration. """
      #self.mDecl.declDecorator.finalize = True
      print "XXX: Can't implement yet."
      return self
   
   def addMethod(self, methodName, methodRef):
      """ Manually add a method (can be used for wrappers as well).
          Ex: addMethod("method", "&Class::method")
      """
      self.addCustomText('def("%s", %s)'%(methodName, methodRef))
      return self
   
   def wrapMethod(self, methodName, wrapperRef):
      """ Manually wrap method.
          Example: setWrapper("method", "ns::new_method")
          :postcondition: ignores any old methods of methodName and defines new method
      """
      self.Method(methodName).ignore()
      self.addMethod(methodName, wrapperRef)
      
   def addCustomText(self, text):
      """ Add custom text to the declarations creator. """
      self.addCreator(code_creators.custom_text_t(text) )
      return self
      
   def addCreator(self, creator):
      """ Add a creator that will be automatically added to the creator
          used to build the code for the wrapped declaration.
      """
      #self.mDecl.declDecorator.customCreators.append(creator)
      print "XXX: Can't implement yet."
      return self

   def printTree(self, detailed=True, recursive=True):
      """ Print decl tree rooted at this node. """
      printDeclTree(self.mDecl, detailed, recursive)      
   
   def getName(self):
      return self.mDecl.name
   
   def getFullname(self):
      return self.mDecl.decl_string
   
   def getSignature(self):
      """ Returns function signature: [retval, [arg1, ..., argN]]. """
      return getMethodSignature(self.mDecl)
   
   def __getitem__(self, name):
      """ Allow simple name lookup using []'s.
          Semantically this has nearly the same effect as the creator methods
          except it does not allow restricting the decl lookup based on type.
          Ex: class["method"].expose()
      """
      res = self.findContained(name)
      if res==None:
         raise RuntimeError, "Declaration '%s' not found"%name
      res.expose()      
      return res

   def count(self, name, declType=None):
      """ Return the number of contained decls with given name and type. """
      return len(self.findContainedDecls(name, declType))
   
   def getDeclChildren(self):
      """ Return a list of all the children of the wrapped decl. """
      children = getattr(self.mDecl, "declarations", None)
      return children
   
   # --------- Internal helpers --------- #
   def findContainedDecls(self, name=None, declType=None):
      """Search contained declarations for ones of specific type and or name.
      
      @param name: regex to use for matching.  (can just be full name)
      @param declType: a single type or a list of decl types to look for.
      @return: None if not found.  Returns 1 or a list if found.
      @note: To make name lookup more predictable matching we automatically add
             a '$' to the end of the regex to match the end of the name.
             This helps to prevent names with similar prefix's from matching.
             If you need this ability you can still get it by adding '.*'                
      """
      found = []
      children = self.getDeclChildren()
      if None != name:
         if not name.endswith('$'):
            name = name + '$'
         name_re = re.compile(name)
      for c in children:
         if ((None == name or name_re.match(c.name)) and  
             (None == declType or isinstance(c, declType))):
            found.append(c)      
      return found
   
   def findContained(self, name=None, declType=None):
      """ Return a new DeclWrapper or MultiDeclWrapper for matching decls.
      
          @param name:     If set this regex is used.
          @param declType: If set restrict search to decls based on the given type.
      """
      found = self.findContainedDecls(name, declType)
      
      if len(found) == 0:
         return None
      elif len(found) == 1:
         return DeclWrapper(found[0])
      else:
         return MultiDeclWrapper([DeclWrapper(d) for d in found])
      
      

   def findContainedMethod(self, name, retval=None, args=None):
      """Search for a method with a particular name.
      name is the method name, retval the type of the return
      value and args a list of argument types. All types (retval and args)
      are given as strings treated as regex matches.
      ex:
      findContainedMethod("method", retval="bool &", args=["int", "float"])
      findContainedMethod(".*", retval="float", args=None)
      """
      found = []
      children = getattr(self.mDecl, "declarations", None)
      if not name.endswith('$'):
         name = name + '$'
      name_re = re.compile(name)
      for c in children:
         if not isinstance(c, declarations.calldef_t):
            continue
         if not name_re.match(c.name):
            continue
         if retval!=None:
            if not retval.endswith('$'):
               retval = retval + '$'
            retval_re = re.compile(retval)
            if c.return_type == None or not retval_re.match(c.return_type.decl_string):
               continue
         if args!=None:
            if len(args) != len(c.arguments):
               continue
            cont_flag = False
            for arg,argument in zip(args, c.arguments):
               if not arg.endswith('$'):
                  arg = arg + '$'
               arg_re = re.compile(arg)
               if not arg_re.match(argument.type.decl_string):
                  cont_flag = True
                  break
            if cont_flag:
               continue
         # Found one
         found.append(c)
      
      if len(found) == 0:
         return None
      elif len(found) == 1:
         return DeclWrapper(found[0])
      else:
         return MultiDeclWrapper([DeclWrapper(d) for d in found])
   
   
class MultiDeclWrapper:
   """ Wrapper for multiple decls at once.  
       Contains a limited subset of DeclWrapper interface. 
       The purpose of having a separate class is to restrict the allowable
       methods that can be called on a set of decl wrappers.  This helps to prevent
       user errors and minimizes the amount of error checking that is necessary.
   """
   def __init__(self, wrappers):
      self.mDeclWrappers = wrappers

   def __getitem__(self, key):
      """ Lookup a contained item.
          Ex: methods[3].rename("newMethod")
      """
      return self.mDeclWrappers[key]
   
   def __len__(self):
      """ Return the number of contained decl wrappers. """
      return len(self.mDeclWrappers)
   
   def ignore(self):
      """ Call ignore on all contained wrappers. """
      for d in self.mDeclWrappers:
         d.ignore()
      return self

   def expose(self, recursive=True):
      """ Call expose on all contained wrappers. """
      for d in self.mDeclWrappers:
         d.expose(recursive)
      return self
         
   def setCallPolicy(self, callPolicy):
      """ Set the call policy for all contained wrappers. """
      for d in self.mDeclWrappers:
         d.setCallPolicy(callPolicy)
      return self
   
   def finalize(self):
      """ Finalize all contained wrappers. """
      for d in self.mDeclWrappers:
         d.finalize()
      return self

# ------ Helper methods and classes --------- #
# Internal methods that are not part of the main interface.

# iterdecls
def iterdecls(rootdecl, recursive=True):
   """Depth first iteration over one or more declaration trees.
   rootdecl can be either a single declaration, a list of declarations
   or None. A declaration must be an object derived from the declaration_t
   class.
   """
   if rootdecl==None:
      return

   if type(rootdecl) is not list:
      rootdecl = [rootdecl]

   for root in rootdecl:
      yield root
      if recursive:
         children = getattr(root, "declarations", None)
         for node in iterdecls(children):
            yield node

def getMethodSignature(decl):
   """ Returns function signature: [retval, [arg1, ..., argN]]. """
   if not isinstance(decl, declarations.member_calldef_t):
      return None
   
   retval = decl.return_type.decl_string
   args = []
   for arg in decl.arguments:
      args.append(arg.type.decl_string)
   return [retval, args]
         
def printDeclTree(decls, detailed=True, recursive=True):
   """ Print decl tree rooted at each of the included nodes.
       decls - either a single decl or a list of decls.
   """
   prn = DeclPrinter(0, detailed, recursive)
   if type(decls) is not list:
      decls = [decls]
   for d in decls:
      prn.level = 0
      prn.instance = d
      declarations.apply_visitor(prn, d)

class DeclPrinter( declarations.decl_visitor_t ):
    """ Helper class for printing decl tree. """
    JUSTIFY = 20
    INDENT_SIZE = 4
    
    def __init__( self, level=0, printDetails=True, recursive=True ):
        declarations.decl_visitor_t.__init__(self)
        self.__inst = None
        self.__level = level
        self.__printDetails = printDetails
        self.__recursive = recursive

    def _get_level(self):
        return self.__level
    def _set_level(self, lvl):
        self.__level = lvl
    level = property( _get_level, _set_level )
    
    def _get_inst(self):
        return self.__inst
    def _set_inst(self, inst):
        self.__inst = inst
    instance = property( _get_inst, _set_inst )
    
    def __nice_decl_name( self, inst ):
        name = inst.__class__.__name__
        return name
        #if name.endswith( '_t' ):
        #    name = name[:-len('_t')]
        #return name.replace( '_', ' ' )

    def __print_decl_header(self):        
        header = self.__nice_decl_name( self.__inst ) + ": '%s'" % self.__inst.name
        print ' ' * self.level * self.INDENT_SIZE + header.ljust( self.JUSTIFY )
        if self.__printDetails:
            curr_level = self.level + 1 
            if self.__inst.location:
                location = 'location: [%s]:%s'%(self.__inst.location.file_name, self.__inst.location.line)
                print ' ' * curr_level * self.INDENT_SIZE + location
            expose = getattr(self.__inst, "_expose_flag", False)
            print ' ' * curr_level * self.INDENT_SIZE + "Expose: ", expose
            artificial = 'artificial: ' + "'%s'" % str(self.__inst.is_artificial)      
            print ' ' * curr_level * self.INDENT_SIZE + artificial.ljust( self.JUSTIFY )

    def visit_member_function( self ):
        self.__print_decl_header()
        print ' ' * (self.level+1) * self.INDENT_SIZE + "Signature: ", getMethodSignature(self.__inst)

    def visit_constructor( self ):
        self.__print_decl_header()

    def visit_destructor( self ):
        self.__print_decl_header()        

    def visit_member_operator( self ):
        self.__print_decl_header()        

    def visit_casting_operator( self ):
        self.__print_decl_header()        

    def visit_free_function( self ):
        self.__print_decl_header()

    def visit_free_operator( self ):
        self.__print_decl_header()

    def visit_class_declaration(self ):
        self.__print_decl_header()

    def visit_class(self ):
        self.__print_decl_header()
        curr_level = self.level + 1
        class_type = 'class type: ' + "'%s'" % str(self.__inst.class_type)        
        print ' ' * curr_level * self.INDENT_SIZE + class_type.ljust( self.JUSTIFY )
        
        def print_hierarchy(hierarchy_type, classes, curr_level):
            print ' ' * curr_level * self.INDENT_SIZE + hierarchy_type.ljust( self.JUSTIFY )
            curr_level += 1
            for class_ in classes:
                class_str = 'class: ' + "'%s'" % str(class_.related_class.decl_string)        
                print ' ' * curr_level * self.INDENT_SIZE + class_str.ljust( self.JUSTIFY )
                access = 'access: ' + "'%s'" % str(class_.access) 
                print ' ' * (curr_level + 1)* self.INDENT_SIZE + access.ljust( self.JUSTIFY )
        
        def print_members(members_type, members, curr_level):
            print ' ' * curr_level * self.INDENT_SIZE + members_type.ljust( self.JUSTIFY )
            if self.__recursive:
               curr_level += 1
               for member in members:
                  prn = DeclPrinter( curr_level + 1, self.__printDetails, self.__recursive )
                  prn.instance = member
                  declarations.apply_visitor( prn, member )
        
        if self.__inst.bases:
            print_hierarchy( 'base classes: ', self.__inst.bases, curr_level )
            
        if self.__inst.derived:
            print_hierarchy( 'derived classes: ', self.__inst.derived, curr_level )

        print_members( 'public: ', self.__inst.public_members, curr_level )
        print_members( 'protected: ', self.__inst.protected_members, curr_level )
        print_members( 'private: ', self.__inst.private_members, curr_level )
        
    def visit_enumeration(self):
        self.__print_decl_header()
        curr_level = self.level + 1
        print ' ' * curr_level * self.INDENT_SIZE + 'values: ['.ljust( self.JUSTIFY ),        
        for name, value in self.__inst.values.items():
            print "%s:%s, "% (name, value)

    def visit_namespace(self ):
        self.__print_decl_header()
        if self.__recursive:
           for decl in self.__inst.declarations:
              prn = DeclPrinter( self.level + 1, self.__printDetails, self.__recursive )
              prn.instance = decl
              declarations.apply_visitor( prn, decl )
            
    def visit_typedef(self ):
        self.__print_decl_header()
        curr_level = self.level + 1
        print ' ' * curr_level * self.INDENT_SIZE + 'alias to: ', self.__inst.type.decl_string

    def visit_variable(self ):
        self.__print_decl_header()
        curr_level = self.level + 1
        print ' ' * curr_level * self.INDENT_SIZE, 'type: %s  value: %s'%(self.__inst.type.decl_string, self.__inst.value)        
 
