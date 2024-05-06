from metadata import Metadata, MetadataReader
from typing import List, Union, Optional
from os.path import relpath


class TestRunner:
    """
    A class to run a test script against an environment.
    """

    def __init__(self, env_yaml_file_path: str) -> None:
        self.metadata_reader = MetadataReader(env_yaml_file_path)

    
    def run_test(self, py_test_file: str) -> List[str]:
        """
        Runs a test script by first parsing it to extract run arguments. Then
        build an argument string from those run arguments and then passing
        that argument string to shell to run the test.

        Parameters:

        py_test_file:
         Path to the python test script that should be run
        """
        runs = self.metadata_reader.parse_script(py_test_file)
        run_arg_strings = []

        for run in runs:
            run_arg_strings.append(self.generate_run_arg_string(run))

        return run_arg_strings

    def __arg_values__(self, arg_type: str, arg_val: Union[str,bool,None,int]) -> List[str]:
        """
        Generates an argument string corresponding to the given `arg-type` and value.

        Generally generates a string of the form "--foo bar" for string-like values
        or "--foo" for boolean arguments.

        Returns:
           empty list if no argument is to be added
           ["key"] or ["key", "value"] when some arguments are required
        """

        if type(arg_val)==bool:
            if arg_val:
                return [arg_type] # boolean value
            # Argument is NOT set, do not return a value
            return []
            
            
        if not arg_val:
            # None or empty list
            return []

        # A key with a value here
        return [arg_type, str(arg_val)]

    
    def get_app_args(self, run: Metadata) -> str:
        """
        Gets the app arguments associated with the run. These arguments
        will be passed the --app-args option.

        Parameters:
        
        run
         Object that contains all the run arguments including app args
        """

        app_args = []
        app_args.extend(self.__arg_values__("--discriminator",run.discriminator))
        app_args.extend(self.__arg_values__("--KVS",run.KVS))
        app_args.extend(self.__arg_values__("--enable-key",run.enable_key))
        app_args.extend(self.__arg_values__("--trace-to", run.trace_to_app_args))

        return " ".join(app_args)

    
    
    def get_script_args(self, run: Metadata) -> str:
        """
        Gets the script arguments associated with the run. These arguments
        will be passed the --script-args option.

        Parameters:
        
        run
         Object that contains all the run arguments including script args
        """

        script_args= []

        script_args.extend(self.__arg_values__("--log-level", run.log_level))
        script_args.extend(self.__arg_values__("--t", run.t))
        script_args.extend(self.__arg_values__("--disable-test", run.disable_test))
        script_args.extend(self.__arg_values__("--storage-path", run.storage_path))
        script_args.extend(self.__arg_values__("--commissioning-method", run.commissioning_method))
        script_args.extend(self.__arg_values__("--discriminator", run.discriminator))
        script_args.extend(self.__arg_values__("--passcode", run.passcode))
        script_args.extend(self.__arg_values__("--PICS", run.PICS))
        script_args.extend(self.__arg_values__("--endpoint", run.endpoint))
        script_args.extend(self.__arg_values__("--int-arg", run.int_arg))
        script_args.extend(self.__arg_values__("--hex-arg", run.hex_arg))
        script_args.extend(self.__arg_values__("--manual-code", run.manual_code))
        script_args.extend(self.__arg_values__("--tests", run.tests))
        script_args.extend(self.__arg_values__("--bool-arg", run.bool_arg))
        script_args.extend(self.__arg_values__("--trace-to",run.trace_to_script_args_json))
        script_args.extend(self.__arg_values__("--trace-to", run.trace_to_script_args_perfetto))
               
        return " ".join(script_args)

    
    def generate_run_arg_string(self, run: Metadata) -> str:
        """
        Converts a run metadata object into a string format that
        can be passed to shell for executing a test script.

        Parameters:
        
        run
         Object that contains all the run arguments including app args
        """

        run_args = []
        run_args.extend(self.__arg_values__("--app",run.app))
        run_args.extend(self.__arg_values__("--factoryreset",run.factoryreset))
        
                        
        app_args = self.get_app_args(run)
        if app_args != "":
            run_args.extend(['--app-args', f'"{app_args}"'])

        if run.py_script_path != None:
            run_args.extend(['--script', f'"{str(run.py_script_path)}"'])

        script_args = self.get_script_args(run)
        if script_args != "":
            run_args.extend(['--script-args', f'"{script_args}"'])

        run_args_string = " ".join(run_args)

        return f"scripts/run_in_python_env.sh out/venv './scripts/tests/run_python_test.py {run_args_string}'"

