from .. import extract 
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

    with pytest.raises(NameError) : extract.extract(example, 'something')
    with pytest.raises(ValueError) : extract.extract(example, 'something.a.a')

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

