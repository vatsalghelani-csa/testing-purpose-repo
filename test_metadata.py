import os
import unittest
from os import path
import tempfile
from typing import List

from metadata import Metadata, MetadataReader  # Assumed to be existing modules
from test_runner import TestRunner  # Assumed to be existing modules


class TestMetadataReader(unittest.TestCase):

    test_file_content = ''' 
    # test-runner-runs: run1 
    # test-runner-run/run1/app: ${ALL_CLUSTERS_APP}
    # test-runner-run/run1/app-args: --discriminator 1234 --trace-to json:${TRACE_APP}.json
    # test-runner-run/run1/script-args: --commissioning-method on-network --trace-to json:${TRACE_TEST_JSON}.json --trace-to perfetto:${TRACE_TEST_PERFETTO}.perfetto
    # test-runner-run/run1/factoryreset: True
    '''

    env_file_content = '''
    ALL_CLUSTERS_APP: out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app
    CHIP_LOCK_APP: out/linux-x64-lock-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-lock-app
    ENERGY_MANAGEMENT_APP: out/linux-x64-energy-management-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-energy-management-app
    TRACE_APP: out/trace_data/app-{SCRIPT_BASE_NAME}
    TRACE_TEST_JSON: out/trace_data/test-{SCRIPT_BASE_NAME}
    TRACE_TEST_PERFETTO: out/trace_data/test-{SCRIPT_BASE_NAME}
    '''

    def generate_temp_file(self, directory: str, file_content: str) -> str:
        fd, temp_file_path = tempfile.mkstemp(dir=directory)
        with os.fdopen(fd, 'w') as fp:
            fp.write(file_content)
        return temp_file_path

    def test_run_arg_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = self.generate_temp_file(temp_dir, self.test_file_content)
            env_file = self.generate_temp_file(temp_dir, self.env_file_content)
            
            reader = MetadataReader(env_file)
            runner = TestRunner(env_file)
            self.maxDiff = None
            
            test_file_expected_arg_string = (
                "scripts/run_in_python_env.sh out/venv './scripts/tests/run_python_test.py "
                "--app out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app "
                "--factoryreset --app-args \"--discriminator 1234 --trace-to json:out/trace_data/app-{SCRIPT_BASE_NAME}.json\" "
                "--script \"" + temp_file + "\" --script-args \"--commissioning-method on-network "
                "--trace-to json:out/trace_data/test-{SCRIPT_BASE_NAME}.json --trace-to perfetto:out/trace_data/test-{SCRIPT_BASE_NAME}.perfetto\"'"
            )

            actual = runner.generate_run_commands(temp_file)[0]
            self.assertEqual(test_file_expected_arg_string, actual)


if __name__ == "__main__":
    unittest.main()
