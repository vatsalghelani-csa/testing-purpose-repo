import argparse
from metadata import Metadata, MetadataReader
from test_runner import TestRunner


def run_test():
    parser = argparse.ArgumentParser(description='Run python tests.')
    parser.add_argument('-e','--env')
    parser.add_argument('-s','--script')
    parser.add_argument('-d','--dry-run', action="store_true")
    
    args = parser.parse_args()

    runner = TestRunner(args.env)

    runner.run_test(args.script, args.dry_run)
    

if __name__ == "__main__":
    run_test()
