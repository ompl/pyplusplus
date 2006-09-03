# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains the base class L{subst_t}.
"""

import re

# subst_t
class subst_t:
    """Perform text substitutions.

    This class performs text substitutions on a template string. The
    variables are simply stored as attributes inside the class and may
    be of any type that can be converted to a string. An empty string
    is used if a template string references a variable that does not
    exist.

    Example::

        sm = subst_t(blockvars=['BODY'])
        sm.RETURNTYPE = 'int'
        sm.FUNCNAME = 'foo'
        sm.ARGLIST = 'int n'
        sm.BODY = '''int res=0;
        for(int i=0; i<n; i++)
        {
          res += n;
        }
        return res;'''

        template = '''
        $RETURNTYPE $FUNCNAME($ARGLIST)
        {
          $BODY
        }
        '''

        print sm.substitute(template)

    The result of the substitution will be::

        int foo(int n)
        {
          int res=0;
          for(int i=0; i<n; i++)
          {
            res += n;
          }
          return res;
        }

    The variable BODY is a block variable which means it may contain
    an entire block of text where each line should be indented with
    the same depth as the variable in the template string. The value
    of BODY should not contain an already indented block.

    @author: Matthias Baas
    """

    def __init__(self, blockvars):
        """Constructor.

        The argument blockvars is used to declare the names of those
        variables that may contain a block of code (i.e. multiple lines).
        
        @param blockvars: A list of block variable names.
        @type blockvars: list of str
        """
        self._blockvars = dict(map(lambda x: (x,0), blockvars))

    def substitute(self, template):
        """Substitute the variables in template and return the result.

        All variables of the form "$<varname>" are replaced with the
        corresponding attribute <varname>. Block variables must appear
        in one single line. The indendation of the variable determines
        the indendation of the entire block.
        Unknown variables will be substituted with an empty string.

        @param template: The template string
        @type template: str
        @return: Returns the input string where all variables have been substituted.
        @rtype: str
        """

        lines = []
        # Replace the block variables...
        for line in template.split("\n"):
            s = line.lstrip()
            # Determine the indendation depth
            depth = len(line)-len(s)
            key = s.rstrip()
            if key!="" and key[0]=="$" and key[1:] in self._blockvars:
                block = getattr(self, key[1:], None)
                if block==None or block=="":
                    line = None
                else:
                    line = self._indent(depth, block)
            else:
                line = line.rstrip()
            if line!=None and (line!="" or (lines!=[] and lines[-1]!="")):
                lines.append(line)
        code = "\n".join(lines)

        # Replace the non-block variables...
        varexpr = re.compile("\$[a-zA-Z_]+")
        while 1:
            m = varexpr.search(code)
            if m==None:
                break
            s = m.start()
            e = m.end()
            key = code[s+1:e]
            code = "%s%s%s"%(code[:s], getattr(self, key, ""), code[e:])

        # Replace trailing blanks on each line...
        expr = re.compile("[ ]+$", re.MULTILINE)
        code = expr.sub("", code)

        # Replace two subsequent empty lines with one single line...
        expr = re.compile("^\n^\n", re.MULTILINE)
        n1 = len(code)
        while 1:
            code = expr.sub("\n", code)
            n2 = len(code)
            if n2==n1:
                break
            n1 = n2

        # Remove blank lines right after '{' or before '}'
        code = code.replace("{\n\n", "{\n")
        code = code.replace("\n\n}", "\n}")

        return code

    # _indent
    def _indent(self, n, code):
        """Indent source code.
        """
        if code=="":
            return ""
        return "\n".join(map(lambda s: ((n*" ")+s).rstrip(), code.split("\n")))


