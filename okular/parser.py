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
        kill_wrapper_prefix = 'Information about the killed process group'
        tsc_error_prefix = 'error TS'
        git_fetch_error_prefix = 'ERROR: Error fetching remote repo'
        fork_error_prefix = 'Failed to fork'
        build_timeout_prefix = 'Build timed out (after'
        cpp_compile_error_prefix = 'error:'
        workspace_cleanup_error_prefix = 'ERROR: Failed to clean the workspace'

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
            if line.find(kill_wrapper_prefix) != -1:
                self.fails.append('kill_wrapper')
            if line.find(tsc_error_prefix) != -1:
                self.fails.append('tsc_error')
            if line.find(git_fetch_error_prefix) != -1:
                self.fails.append('git_fetch_error')
            if line.find(fork_error_prefix) != -1:
                self.fails.append('fork_error')
            if line.find(build_timeout_prefix) != -1:
                self.fails.append('build_timeout')
            if line.find(cpp_compile_error_prefix) != -1:
                if 'cpp_compile_error' not in self.fails:
                    self.fails.append('cpp_compile_error')
            if line.find(workspace_cleanup_error_prefix) != -1:
                self.fails.append('workspace_cleanup_error')

        for line in self.raw_input.split('\n'):
            if line.find(cypress_fail_summary_prefix) != -1:
                test_name = self.clean_text(line.split(' ')[5])
                self.fails.append(test_name)

    def get_fails(self):
        return self.fails
