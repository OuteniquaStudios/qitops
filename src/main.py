from core.factories import factory_manager
from core.test_case_generator import TestCaseGenerator
from utils.file_utils import load_config
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Generate test cases from GitHub PRs'
    )
    parser.add_argument('repo')
    parser.add_argument('pr_number', type=int)
    parser.add_argument('--output', default='pr_test_cases.yaml')
    parser.add_argument('--config', default='config.yaml')
    args = parser.parse_args()

    config = load_config(args.config)
    factory_manager.configure(config)

    vcs = factory_manager.vcs_factory.create("github", token=config["providers"]["vcs"]["github"]["token"])
    llm = factory_manager.llm_factory.create("litellm", 
                                             model=config["providers"]["llm"]["litellm"]["model"], 
                                             temperature=config["providers"]["llm"]["litellm"]["temperature"])
    output = factory_manager.output_factory.create("yaml")

    generator = TestCaseGenerator(vcs, llm, output)
    generator.generate(args.repo, args.pr_number, args.output)

if __name__ == "__main__":
    main()