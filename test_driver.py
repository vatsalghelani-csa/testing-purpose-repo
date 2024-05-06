from test_runner import TestRunner
from pathlib import Path


def run_tests(test_directory, env_yaml):

    runner = TestRunner(env_yaml)
    
    for path in Path(test_directory).glob("*.py"):
        for run in runner.run_test(path):
            print(run)


if __name__ == "__main__":
    run_tests("src/python_testing", "env_test.yaml")
