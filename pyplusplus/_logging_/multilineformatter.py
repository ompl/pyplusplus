# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# Initial version by Matthias Baas (baas@ira.uka.de).

import os, logging, textwrap

class multi_line_formatter_t(logging.Formatter):
    """Custom log formatter to split long message into several lines.

    This formatter is used for the default stream handler that outputs
    its messages to stdout.
    """

    def __init__(self, fmt=None, datefmt=None, width=70):
        """Constructor.

        See the Python standard library reference for a documentation
        of fmt and datefmt.
        width is the maximum width of the generated text blocks.
        """
        logging.Formatter.__init__(self, fmt, datefmt)
        self._width = width

    def format(self, record):
        """This method overwrites the original one.

        The first thing that is done in the original format() method
        is the creation of the record.message attribute:

          record.message = record.getMessage()

        Now this method temporarily replaces the getMessage() method of
        the record by a version that returns a pregenerated message that
        spans several lines. Then the original format() method is called
        which will invoke the 'fake' method.
        """
        # Get the original single-line message
        message = record.getMessage()
        # Distribute the message among several lines...
        message = self.formatMessage(message, width=self._width)
        # ...and temporarily replace the getMessage() method so that the
        # reformatted message is used
        mth = record.getMessage
        record.getMessage = lambda x=message: x
        # Invoke the inherited format() method
        res = logging.Formatter.format(self, record)
        # Restore the original method
        record.getMessage = mth
        return res

    @staticmethod
    def formatMessage(msgline, width=70):
        """Format a long single line message so that it is easier to read.

        msgline is a string containing a single message. It can either be
        a plain message string which is reformatted using the textwrap
        module or it can be of the form <decl>;<msg> where <decl> is the
        declaration string and <msg> an arbitrary message. Lines of this
        form will be separated so that the declaration and the message
        appear in individual text blocks separated by the string '->'.

        In any case the return string will be indented except for the first
        line.

        width is the maximum width of any text blocks (without indendation).
        """
        txts = msgline.split(";")
        # Ensure that there are no more than two items in txts
        if len(txts)>2:
            txts = [txts[0], ";".join(txts[1:])]

        # Insert a separator if there are two parts (=decl and msg)
        if len(txts)==2:
            txts.insert(1, "->")

        # Apply the text wrapper to shorten the maximum line length
        lines = []
        for txt in txts:
            txt = txt.strip().replace(os.linesep, " ")
            lines.extend(textwrap.wrap(txt, width))

        # Indent the text (except for the first line)
        lines[1:] = map(lambda s: (2*" ")+s, lines[1:])
        return os.linesep.join(lines)


