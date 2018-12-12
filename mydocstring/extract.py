"""
MIT License

Copyright (c) 2018 Ossian O'Reilly

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
"""
This module is used to extract a docstring from source.
"""
import re

class Extract(object):
    """
    Base class for extracting docstrings.

    Attributes:
        filename: A string that that specifies the file to extract docstrings
            from.
        txt : A string that contains the source code that has been read from
            `source`.
        query : The docstring to search for. The search is specified in the form
            of `Class.method`, or `function`, or `.` to search for the module
            docstring.
        classname : Holds the class name of the query.
        funcname : Holds the function or method name of the query.
        dtype : Holds the type of the query `module`, `class`, `method`, or
            `function`.

    """

    def __init__(self, filename):
        """
        Initializer for Extract.

        Arguments:
            filename: A string that that specifies the file to extract
                docstrings from. If this is not a valid file, then it will be
                treated as text.

        """
        try:
            self.txt = open(filename).read()
            self.filename = filename
        except:
            self.txt = filename
            self.filename = ''
        self.query = ''
        self.classname = ''
        self.funcname = ''
        self.dtype = ''
        # This dictionary contains the ids of the different attributes that can
        # be captured. The value specifies the order in which attribute is
        # captured.
        self.ids = {'class' : 0, 'function' : 1, 'signature' : 2,
                'indent' : 3, 'docstring' : 4, 'body' : 5, 'return_type' : 100}
        self.function_keyword = 'def '


    def extract(self, query):
        """
        Extracts the docstring.

        Arguments:
            query : The docstring to search for. The search is specified in the form
                of `Class.method`, or `function`, or `.` to search for the module
                docstring.

        Returns:
            A dictionary that matches the description given by `Extract.find`.

        """

        self.query = query
        self.classname, self.funcname, self.dtype = get_names(query)
        types = {'class' : self.extract_class,
                 'method' : self.extract_method,
                 'function' : self.extract_function,
                 'module' : self.extract_module}

        return types[self.dtype]()

    def extract_function(self):
        """
        Override this method to extract function docstrings for the specific
        language. The functions extracted are module functions. Lamba functions
        are not extracted.

        Returns:
            A dictionary that matches the description given by `Extract.find`.
        """
        pass
    def extract_class(self):
        """
        Override this method to extract class docstrings for the specific
        language.

        Returns:
            A dictionary that matches the description given by `Extract.find`.
        """
        pass

    def extract_method(self):
        """
        Override this method to extract method docstrings for the specific
        language.

        Returns:
            A dictionary that matches the description given by `Extract.find`.
        """
        pass

    def extract_module(self):
        """
        Override this method to extract module docstrings for the specific
        language. Module docstrings are defined at the start of a file and are
        not attached to any block of code.

        Returns:
            A dictionary that matches the description given by `Extract.find`.
        """
        pass

    def find(self, pattern, ids=None):
        """
        Performs a search for a docstring that matches a specific pattern.

        Returns:
            dict: The return type is a dictionary with the following keys:
                 * `class` :  The name of the class.
                 * `function` : The name of the function/method.
                 * `signature` : The signature of the function/method.
                 * `docstring` : The docstring itself.
                 * `type` : What type of construct the docstring is attached to.
                      This can be either `'module'`, `'class'`, `'method'`, or
                      `'function'`.
                 * `label` : The search query string.
                 * `filename` : The filename of source to extract docstrings from.
                 * `source` : The source code if the query is a function/method.

        Raises:
            NameError: This is exception is raised if the docstring cannot be
                extracted.
        """
        import textwrap
        matches = re.compile(pattern, re.M).findall(self.txt)
        if not matches:
            raise NameError(r'Unable to extract docstring for `%s`' % self.query)
        else:

            if not ids:
                ids = self.ids

            cls = get_match(matches[0], ids['class'])
            function = get_match(matches[0], ids['function'])
            signature = get_match(matches[0], ids['signature'])
            indent = len(get_match(matches[0], ids['indent']))
            return_type = get_match(matches[0], ids['return_type'])
            docstring = remove_indent(get_match(matches[0], ids['docstring']),
                                      indent)
            if self.dtype == 'function' or self.dtype == 'method': 
                source = textwrap.dedent(self.function_keyword + function +
                                         signature + ':' + return_type + '\n'
                                         +
                                         get_match(matches[0], ids['body'])) 
            else: 
                source = ''

            out = {}
            out['class'] = cls
            out['function'] = function
            out['signature'] = signature
            out['docstring'] = docstring
            out['return_type'] = return_type
            out['source'] = source
            out['type'] = self.dtype
            out['label'] = self.query
            out['filename'] = self.filename

            return out

class PyExtract(Extract):
    """
    Base class for extracting docstrings from python source code.
    """

    def extract_function(self):
        pattern = (r'^\s*()def\s(%s)(\((?!self).*\)):.*' % self.funcname
                   + r'\n*(\s+)"""([\w\W]*?)"""\n((\4.*\n+)+)?')
        return self.find(pattern)

    def extract_class(self):
        pattern = (r'^\s*class\s+(%s)()(\(\w*\))?:\n(\s+)"""([\w\W]*?)"""()' %
                   self.classname)
        return self.find(pattern)

    def extract_method(self):
        pattern = (r'class\s+(%s)\(?\w*\)?:[\n\s]+[\w\W]*?' % self.classname +
                   r'[\n\s]+def\s+(%s)(\(self.*\)):.*\n' % self.funcname +
                   r'(\s+)"""([\w\W]*?)"""\n((?:\4.*\n+)+)?')
        return self.find(pattern)

    def extract_module(self):
        pattern = r'()()()()^"""([\w\W]*?)"""'
        return self.find(pattern)

class PyBindExtract(PyExtract):
    """
    Extract function header, signature, and documentation from PyBind-generated
    docstrings.
    """

    def __init__(self, query):
        PyExtract.__init__(self, query)
        self.function_keyword = ""

    def extract_function(self):
        pattern = (r'^\s*(%s)(\((?!self).*\))' % self.funcname
                 +  r'\s*(?:-> (\w+))*\n+(\s+)\n*((?:\4.*\n+)+)')
        ids = {'class' : 100, 'function' : 0, 'signature' : 1,
                'return_type' : 2,
                'indent' : 3, 'docstring' : 4, 'body' : 5}
        return self.find(pattern, ids)

    def parse_signature(self, args):
        """
        Parse the signature e.g., `(int: a, int: b)` and put into a dict {'a' :
        'int', 'b' : int}
        """

        # Remove () 
        substr = args[1:-1]
        substr = substr.split(',')
        args_out = {}
        for si in substr:
            name, type_ = si.split(':')
            name = name.strip()
            args_out[name] = type_.strip()
        return args_out

    



def extract(filestr, query):
    """
    Extracts a docstring from source.

    Arguments:
        filestr: A string that specifies filename of the source code to extract
            from.
        query: A string that specifies what type of docstring to extract.

    """
    import os

    filename = os.path.splitext(filestr)
    ext = filename[1]

    options = {'.py' : PyExtract}

    if ext in options:
        extractor = options[ext](filestr)

    return extractor.extract(query)


def get_names(query):
    """
    Extracts the function and class name from a query string.
    The query string is in the format `Class.function`.
    Functions starts with a lower case letter and classes starts
    with an upper case letter.

    Arguments:
        query: The string to process.

    Returns:
        tuple: A tuple containing the class name, function name,
               and type. The class name or function name can be empty.

    """
    funcname = ''
    classname = ''
    dtype = ''

    members = query.split('.')
    if len(members) == 1:
        # If no class, or function is specified, then it is a module docstring
        if members[0] == '':
            dtype = 'module'
        # Identify class by checking if first letter is upper case
        elif members[0][0].isupper():
            classname = query
            dtype = 'class'
        else:
            funcname = query
            dtype = 'function'
    elif len(members) == 2:
        # Parse method
        classname = members[0]
        funcname = members[1]
        dtype = 'method'
    else:
        raise ValueError('Unable to parse: `%s`' % query)

    return (classname, funcname, dtype)

def remove_indent(txt, indent):
    """
    Dedents a string by a certain amount.
    """
    lines = txt.split('\n')
    if lines[0] != '\n':
        header = '\n' + lines[0]
    else:
        header = ''
    return '\n'.join([header] + [line[indent:] for line in lines[1:]])

def get_match(match, index, default=''):
    """
    Returns a value from match list for a given index. In the list is out of
    bounds `default` is returned.

    """
    if index >= len(match):
        return default
    else:
        return match[index]

