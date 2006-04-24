# Generate documentation using epydocs
#
import os, os.path
pj = os.path.join

default_format = "epytext"

pypp_module_dirs = ["code_creators", 
                    "code_repository", 
                    "decl_wrappers", 
                    "experimental", 
                    "file_writers", 
                    "gui", 
                    "module_builder",
                    "module_creator",
                    "utils",
                    "__init__.py"]

pypp_dir = pj("..","..","..","pyplusplus")

module_params = [pj(pypp_dir,d) for d in pypp_module_dirs]

cmd_line = "epydoc -o html --docformat " + default_format + " "
cmd_line += " ".join(module_params)

print "Running: ", cmd_line
os.system(cmd_line)

