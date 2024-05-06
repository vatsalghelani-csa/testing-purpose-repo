#!/usr/bin/python3
# Copyright (c) 2024 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    # test-runner-run/run1: app/all-clusters discriminator passcode factoryreset KVS
    # test-runner-run/run1: trace_to_app_args trace_to_script_args_json trace_to_script_args_perfetto
    # test-runner-run/run1: storage_path commissioning_method
    '''

    env_file_content ='''
    discriminator: 1234
    passcode: 20202021
    KVS: kvs1
    storage_path: admin_storage.json
    trace_to_app_args: json:out/trace_data/app-{SCRIPT_BASE_NAME}.json
    trace_to_script_args_json: json:out/trace_data/test-{SCRIPT_BASE_NAME}.json
    trace_to_script_args_perfetto: perfetto:out/trace_data/test-{SCRIPT_BASE_NAME}.perfetto
    commissioning_method: on-network
    PICS: src/app/tests/suites/certification/ci-pics-values
    app:
     all-clusters: out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app
     lock: out/linux-x64-lock-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-lock-app
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
        "--factoryreset --app-args \" --discriminator 1234 --KVS kvs1 --trace-to json:out/trace_data/app-{SCRIPT_BASE_NAME}.json\" "\
        "--script \""+self.temp_file+"\" --script-args \" --storage-path admin_storage.json --commissioning-method "\
        "on-network --discriminator 1234 --passcode 20202021 --trace-to json:out/trace_data/test-{SCRIPT_BASE_NAME}.json "\
        "--trace-to perfetto:out/trace_data/test-{SCRIPT_BASE_NAME}.perfetto\"'"
    
        

    def generateTempFile(self, file_content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
            fp.write(file_content)
            fp.close()
            return fp.name


    def test_parse_single_run(self):
        
        expected_metadata = Metadata(app="out/linux-x64-all-clusters-ipv6only-no-ble-no-wifi-tsan-clang-test/chip-all-clusters-app",
                                     discriminator=1234, py_script_path=self.temp_file, run="run1", passcode=20202021, factoryreset=True, KVS="kvs1",
                                     trace_to_app_args="json:out/trace_data/app-{SCRIPT_BASE_NAME}.json",
                                     trace_to_script_args_json="json:out/trace_data/test-{SCRIPT_BASE_NAME}.json",
                                     trace_to_script_args_perfetto="perfetto:out/trace_data/test-{SCRIPT_BASE_NAME}.perfetto",
                                     storage_path="admin_storage.json",
                                     commissioning_method="on-network"
                                     )

        self.assertEqual(expected_metadata, self.reader.parse_script(self.temp_file)[0])
        pass


    def test_run_arg_generation(self):
        
        actual = self.runner.run_test(self.temp_file)[0]
        self.assertEqual(self.test_file_expected_arg_string,actual)


if __name__ == "__main__":
    unittest.main()
