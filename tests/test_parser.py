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


def test_workspace_cleanup_error():
    text = '''Started by upstream project "MyProject" build number 1234
Building remotely on BuildAgent (windows) in workspace C:\\jenkins\\workspace\\my_job
Cloning the remote Git repository
Cloning repository https://git.example.com/repo
ERROR: Failed to clean the workspace
jenkins.util.io.CompositeIOException: Unable to delete 'C:\\jenkins\\workspace\\my_job'.
    at jenkins.util.io.PathRemover.forceRemoveDirectoryContents(PathRemover.java:86)
ERROR: Error cloning remote repo 'abc123'
Finished: FAILURE
'''
    parser = Parser(text)
    parser.parse()
    assert 'workspace_cleanup_error' in parser.get_fails()