import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import yaml


@dataclass
class Metadata:
    py_script_path: Optional[str] = None
    run: Optional[str] = None
    app: Optional[str] = None
    app_args: Optional[str] = None
    script_args: Optional[str] = None
    factory_reset: [bool] = False


    def copy_from_dict(self, attr_dict: Dict[str, str]) -> None:
        """
        Sets the value of the attributes from a dictionary.

        Attributes:

        attr_dict:
          Dictionary that stores attributes value that should
          be transferred to this class.
        """

        if "app" in attr_dict:
            self.app = attr_dict["app"]

        if "run" in attr_dict:
            self.run = attr_dict["run"]

        if "app-args" in attr_dict:
            self.app_args = attr_dict["app-args"]

        if "script-args" in attr_dict:
            self.script_args = attr_dict["script-args"]

        if "py_script_path" in attr_dict:
            self.py_script_path = attr_dict["py_script_path"]

        if "factoryreset" in attr_dict:
            self.factory_reset = bool(attr_dict["factoryreset"])



class MetadataReader:
    """
    A class to parse run arguments from the test scripts and 
    resolve them to environment specific values.
    """

    def __init__(self, env_yaml_file_path: str):
        """
        Reads the YAML file and Constructs the environment object

        Parameters:

        env_yaml_file_path:
          Path to the environment file that contains the YAML configuration.
        """
        with open(env_yaml_file_path) as stream:
            self.env = yaml.safe_load(stream)

    def __resolve_env_vals__(self, metadata_dict: Dict[str, str]) -> None:
        """
        Resolves the argument defined in the test script to environment values.
        For example, if a test script defines "all_clusters" as the value for app
        name, we will check the environment configuration to see what raw value is
        assocaited with the "all_cluster" variable and set the value for "app" option
        to this raw value.

        Parameter:

        metadata_dict:
          Dictionary where each key represent a particular argument and its value represent
          the value for that argument defined in the test script.
        """

        # detect ${VARIABLE} pattern which is used to
        #
        
        placeholder_ptrn = r"(?<=\${).*?(?=})"
        for arg, arg_val in metadata_dict.items():
            variables = re.findall(placeholder_ptrn, arg_val)
            for variable in variables:

                if variable not in self.env:
                    continue
                
                arg_val = arg_val.replace(f'${{{variable}}}', self.env[variable])

            metadata_dict[arg] = arg_val
                  
            

    def __read_args__(self, run_args_lines: List[str]) -> Dict[str, str]:
        """
        Parses a list of lines and extracts argument
        values from it.

        Parameters:

        run_args_lines:
          Line in test script header that contains run argument definition.
          Each line will contain a list of run arguments separated by a space.
          Line below is one example of what the run argument line will look like:
          "app/all-clusters discriminator KVS storage-path"

          In this case the line defines that app, discriminator, KVS, and storage-path
          are the arguments that should be used with this run.

          An argument can be defined multiple times in the same line or in different lines.
          The last definition will override any previous definition. For example,
          "KVS/kvs1 KVS/kvs2 KVS/kvs3" line will lead to KVS value of kvs3.
        """
        metadata_dict = {}

        for run_line in run_args_lines:
            for run_arg_word in run_line.strip().split():
                '''
                We expect the run arg to be defined in one of the 
                following two formats:
                1. run_arg
                2. run_arg/run_arg_val

                Examples: "discriminator" and "app/all_clusters"

                '''
                run_arg = run_arg_word.split('/', 1)[0]
                metadata_dict[run_arg] = run_arg_word

        return metadata_dict

    def parse_script(self, py_script_path: str) -> List[Metadata]:
        """
        Parses a script and returns a list of metadata object where
        each element of that list representing run arguments associated
        with a particular run.

        Parameter:

        py_script_path:
          path to the python test script

        Return:

        List[Metadata]
          List of Metadata object where each Metadata element represents
          the run arguments associated with a particular run defined in
          the script file.
        """

        runs_def_ptrn = re.compile(r'^\s*#\s*test-runner-runs:\s*(.*)$')
        arg_def_ptrn = re.compile(r'^\s*#\s*test-runner-run/([a-zA-Z0-9_]+)/([a-zA-Z0-9_\-]+):\s*(.*)$')

        runs_arg_lines: Dict[str, List[str]] = {}
        runs_metadata = []

        with open(py_script_path, 'r', encoding='utf8') as py_script:
            for line in py_script.readlines():

                runs_match = runs_def_ptrn.match(line.strip())
                args_match = arg_def_ptrn.match(line.strip())

                if runs_match:
                    for run in runs_match.group(1).strip().split():
                        runs_arg_lines[run] = {}
                        runs_arg_lines[run]['run'] = run
                        runs_arg_lines[run]['py_script_path'] = py_script_path

                elif args_match:
                    runs_arg_lines[args_match.group(1)][args_match.group(2)] = args_match.group(3)


        for run, attr in runs_arg_lines.items():
            self.__resolve_env_vals__(attr)
            
            metadata = Metadata()

            metadata.copy_from_dict(attr)
            runs_metadata.append(metadata)

        return runs_metadata
