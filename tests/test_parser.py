import re
from okular.parser import Parser

def test_no_console_commands():
    text = '[22mCypress test failed: Hello[1m World\nThis is second line\n'
    parser = Parser(text)
    parser.parse()
    assert len(parser.get_fails()) == 1
    assert parser.get_fails()[0] == 'Hello World'