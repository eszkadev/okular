import re

class Parser:
    def __init__(self, input):
        # clear console commands
        self.raw_input = input
        self.fails = []

    def clean_text(self, text):
        return re.sub(r'\[\d+m', '', text)

    def parse(self):
        cypress_fail_prefix = 'Cypress test failed: '
        unittest_fail_prefix = 'Test failed on '
        write_error_prefix = 'write error: Resource temporarily unavailable'
        cypress_fail_summary_prefix = '[31mâ[39m'

        input = self.clean_text(self.raw_input)
        for line in input.split('\n'):
            if line.find(cypress_fail_prefix) != -1:
                test_name = line[len(cypress_fail_prefix):]
                self.fails.append(test_name)
            if line.find(unittest_fail_prefix) != -1:
                test_name = line[len(unittest_fail_prefix):].split(' ')[0]
                self.fails.append(test_name)
            if line.find(write_error_prefix) != -1:
                self.fails.append('write error: Resource temporarily unavailable')

        for line in self.raw_input.split('\n'):
            if line.find(cypress_fail_summary_prefix) != -1:
                test_name = self.clean_text(line.split(' ')[5])
                self.fails.append(test_name)

    def get_fails(self):
        return self.fails