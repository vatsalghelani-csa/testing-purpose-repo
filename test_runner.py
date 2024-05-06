from metadata import Metadata, MetadataReader
from typing import List, Union
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

    def __append_arg__(self, full_arg_string: str, arg_type: str, arg_val: Union[str,bool,None,int]) -> str:
        """
        Helper method to add new argument values to the final argument 
        string that will be sent to shell.

        Parameters:

        full_arg_string:
         The the argument string as it currently exists

        arg_type:
         Argument type; example, "--factoryreset", "--app"

        arg_val:
         Value associated with the argument type
        """

        if type(arg_val)==bool:
            if arg_val:
                return full_arg_string+" "+arg_type
            else:
                return full_arg_string
            
            
        if arg_val != None and arg_val != "":
            return full_arg_string + " " + arg_type+" "+str(arg_val)

        return full_arg_string
    
    def get_app_args(self, run: Metadata) -> str:
        """
        Gets the app arguments associated with the run. These arguments
        will be passed the --app-args option.

        Parameters:
        
        run
         Object that contains all the run arguments including app args
        """

        app_args=""
        app_args = self.__append_arg__(app_args,"--discriminator",run.discriminator)
        app_args = self.__append_arg__(app_args,"--KVS",run.KVS)
        app_args = self.__append_arg__(app_args,"--enable-key",run.enable_key)
        app_args = self.__append_arg__(app_args,"--trace-to", run.trace_to_app_args)

        return app_args

    
    
    def get_script_args(self, run: Metadata) -> str:
        """
        Gets the script arguments associated with the run. These arguments
        will be passed the --script-args option.

        Parameters:
        
        run
         Object that contains all the run arguments including script args
        """

        script_args=""

        script_args = self.__append_arg__(script_args,"--log-level", run.log_level)
        script_args = self.__append_arg__(script_args,"--t", run.t)
        script_args = self.__append_arg__(script_args,"--disable-test", run.disable_test)
        script_args = self.__append_arg__(script_args,"--storage-path", run.storage_path)
        script_args = self.__append_arg__(script_args,"--commissioning-method", run.commissioning_method)
        script_args = self.__append_arg__(script_args,"--discriminator", run.discriminator)
        script_args = self.__append_arg__(script_args,"--passcode", run.passcode)
        script_args = self.__append_arg__(script_args,"--PICS", run.PICS)
        script_args = self.__append_arg__(script_args,"--endpoint", run.endpoint)
        script_args = self.__append_arg__(script_args,"--int-arg", run.int_arg)
        script_args = self.__append_arg__(script_args,"--hex-arg", run.hex_arg)
        script_args = self.__append_arg__(script_args,"--manual-code", run.manual_code)
        script_args = self.__append_arg__(script_args,"--tests", run.tests)
        script_args = self.__append_arg__(script_args,"--bool-arg", run.bool_arg)
        script_args = self.__append_arg__(script_args,"--trace-to",run.trace_to_script_args_json)
        script_args = self.__append_arg__(script_args,"--trace-to", run.trace_to_script_args_perfetto)
               
        return script_args

    
    def generate_run_arg_string(self, run: Metadata) -> str:
        """
        Converts a run metadata object into a string format that
        can be passed to shell for executing a test script.

        Parameters:
        
        run
         Object that contains all the run arguments including app args
        """

        run_arg_string = "scripts/run_in_python_env.sh out/venv './scripts/tests/run_python_test.py"
        app_args = self.get_app_args(run)
        script_args = self.get_script_args(run)

        run_arg_string = self.__append_arg__(run_arg_string,"--app",run.app)
        run_arg_string = self.__append_arg__(run_arg_string,"--factoryreset",run.factoryreset)
        
                        
        if app_args != "":
            run_arg_string = run_arg_string + ' --app-args "' + app_args + '"'

        if run.py_script_path != None:
            run_arg_string = run_arg_string + ' --script "' + str(run.py_script_path) + '"'

        if script_args != "":
            run_arg_string = run_arg_string + ' --script-args "' + script_args + '"'

        run_arg_string = run_arg_string + "'"

        return run_arg_string
