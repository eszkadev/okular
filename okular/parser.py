import re

class Parser:
    def __init__(self, input):
        # clear console commands
        self.input = re.sub(r'\[\d+m', '', input)
        self.fails = []

    def parse(self):
        cypress_fail_prefix = 'Cypress test failed: '
        for line in self.input.split('\n'):
            if line.find(cypress_fail_prefix) != -1:
                test_name = line[len(cypress_fail_prefix):]
                self.fails.append(test_name)

    def get_fails(self):
        return self.fails