from mydocstring import extract
import pytest


def test_get_names():
    extract.get_names('test') == ('', 'test', 'function')
    extract.get_names('Test') == ('Test', '', 'class')
    extract.get_names('Test.test') == ('Test', 'test', 'method')
    extract.get_names('') == ('', '', 'module')


def test_extract():
    example = 'fixtures/example.py'
    match = extract.extract(example, 'function_with_docstring')
    assert match['function'] == 'function_with_docstring'
    assert match['signature'] == '(arg1, arg2=True)'
    assert match['type'] == 'function'
    assert match['source'] == 'def function_with_docstring(arg1, arg2=True):\n    pass\n\n'
    assert match['docstring']

    match = extract.extract(example, 'ExampleOldClass')
    assert match['class'] == 'ExampleOldClass'
    assert match['type'] == 'class'

    match = extract.extract(example, 'ExampleNewClass')
    assert match['class'] == 'ExampleNewClass'
    assert match['signature'] == '(object)'
    assert match['type'] == 'class'

    match = extract.extract(example, 'ExampleOldClass.__init__')

    with pytest.raises(NameError):
        extract.extract(example, 'something')
    with pytest.raises(ValueError):
        extract.extract(example, 'something.a.a')


def test_pybind():
    docstring = \
        """
    add(arg0: int, arg1: int) -> int


           Add two numbers

           Some other explanation about the add function.
    """
    pybind = extract.PyBindExtract(docstring)
    match = pybind.extract('add')
    assert match['function'] == 'add'
    assert match['return_type'] == 'int'
    assert match['signature'] == '(arg0: int, arg1: int)'
    assert 'Add two numbers' in match['docstring']
    assert 'Some other' in match['docstring']


def test_pybind_parse_args():

    pybind = extract.PyBindExtract('')
    signature = '(arg0: int, arg1: int)'
    args = pybind.parse_signature(signature)
    assert 'arg0' in args and args['arg0'] == 'int'
    assert 'arg1' in args and args['arg1'] == 'int'


def test_pybind_parse_overloaded():
    docstring = \
        """
    add(*args, **kwargs)
    Overloaded function.

    1. add(arg0: int, arg1: int) -> int


        Adds two numbers

        Args:
            arg0 (int): The first parameter.
                Second line of description should be indented.
            arg1 (int): The second parameter.

        Returns:
            int: The sum arg0+arg1

            The return type is optional and may be specified at the beginning of
            the ``Returns`` section followed by a colon.


      2. add(arg0: int, arg1: int, arg2: int) -> int


          Adds three numbers

          Args:
              arg0 (int): The first parameter.
                  Second line of description should be indented.
              arg1 (int): The second parameter.
              arg2 (int): The third parameter.

          Returns:
              int: The sum arg0+arg1+arg2.

              The return type is optional and may be specified at the beginning of
              the ``Returns`` section followed by a colon.


    """
    pybind = extract.PyBindExtract(docstring)
    match = pybind.extract('add')
    assert isinstance(match["function"], list)
    assert match["function"][0] == 'add'
    assert match['return_type'][0] == 'int'
    assert match['signature'][0] == '(arg0: int, arg1: int)'
    assert match["function"][1] == 'add'
    assert match['return_type'][1] == 'int'
    assert match['signature'][1] == '(arg0: int, arg1: int, arg2: int)'


def test_pybind_class():
    docstring =\
        """
    class  Operations

    The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).
    """
    pybind = extract.PyBindExtract(docstring)
    match = pybind.extract('Operations')
    assert match["class"] == 'Operations'
