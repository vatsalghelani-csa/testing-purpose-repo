import os
import unittest
from os import path
import tempfile
from typing import List

from metadata import Metadata, MetadataReader
from test_runner import TestRunner


class TestMetadataReader(unittest.TestCase):
   
    test_file_content = ''' 
    # test-runner-runs: run1 
    # test-runner-run/run1/app: ${ALL_CLUSTERS_APP}
    # test-runner-run/run1/app-args: --discriminator 1234 --trace-to json:${TRACE_BASE}.json
    # test-runner-run/run1/script-args: --commissioning-method on-network --trace-to perfetto:${TRACE_BASE}.json
    # test-runner-run/run1/factoryreset: True
    '''

    env_file_content ='''
    TRACE_BASE: out/trace_data/test-{SCRIPT_BASE_NAME}
    ALL_CLUSTERS_APP: out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app
    '''


    def setUp(self):
        # build the reader object
        self.temp_file = self.generateTempFile(self.test_file_content)
        self.env_yaml_file = self.generateTempFile(self.env_file_content)
        self.reader = MetadataReader(path.join(path.dirname(__file__), self.env_yaml_file))
        self.runner = TestRunner(path.join(path.dirname(__file__), self.env_yaml_file))
        self.maxDiff = None
        self.test_file_expected_arg_string = "scripts/run_in_python_env.sh out/venv './scripts/tests/run_python_test.py "\
        "--app out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app "\
        "--factoryreset --app-args \"--discriminator 1234 --trace-to json:out/trace_data/test-{SCRIPT_BASE_NAME}.json\" "\
        "--script \""+self.temp_file+"\" --script-args \"--commissioning-method on-network "\
        "--trace-to perfetto:out/trace_data/test-{SCRIPT_BASE_NAME}.json\"'"
    
        

    def generateTempFile(self, file_content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
            fp.write(file_content)
            fp.close()
            return fp.name

 
    def test_run_arg_generation(self):
        
        actual = self.runner.generate_run_commands(self.temp_file)[0]
        self.assertEqual(self.test_file_expected_arg_string,actual)


if __name__ == "__main__":
    unittest.main()
