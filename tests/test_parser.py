import re
from okular.parser import Parser

def test_no_console_commands():
    text = '[22mCypress test failed: Hello[1m World\nThis is second line\n'
    parser = Parser(text)
    parser.parse()
    assert len(parser.get_fails()) == 1
    assert parser.get_fails()[0] == 'Hello World'


def test_cpp_compile_error():
    text = '''../src/Module.hpp:550:25: error: cannot convert 'MyClass**' to 'OtherClass**'
../src/Module.cpp:127:30: error: invalid conversion from 'StructA*' to 'StructB*'
make: *** [Makefile:42: Module.o] Error 1
'''
    parser = Parser(text)
    parser.parse()
    assert 'cpp_compile_error' in parser.get_fails()
    # Should only appear once even with multiple error lines
    assert parser.get_fails().count('cpp_compile_error') == 1