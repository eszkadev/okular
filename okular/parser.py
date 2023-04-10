import re

class Parser:
    def __init__(self, input):
        # clear console commands
        self.input = re.sub(r'\[\d+m', '', input)
        self.fails = []

    def parse(self):
        cypress_fail_prefix = 'Cypress test failed: '
        unittest_fail_prefix = 'Test failed on '
        write_error_prefix = 'write error: Resource temporarily unavailable'
        for line in self.input.split('\n'):
            if line.find(cypress_fail_prefix) != -1:
                test_name = line[len(cypress_fail_prefix):]
                self.fails.append(test_name)
            if line.find(unittest_fail_prefix) != -1:
                test_name = line[len(unittest_fail_prefix):].split(' ')[0]
                self.fails.append(test_name)
            if line.find(write_error_prefix) != -1:
                self.fails.append('write error: Resource temporarily unavailable')

    def get_fails(self):
        return self.fails