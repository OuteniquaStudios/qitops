from core.factories import factory_manager
from core.test_case_generator import TestCaseGenerator
from utils.file_utils import load_config
import logging
import sys
import os
import argparse

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        config = load_config(config_path)
        
        factory_manager.configure(config)

        parser = argparse.ArgumentParser(
            description='Generate test cases from PRs'
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
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()