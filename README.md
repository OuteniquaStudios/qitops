# qitops

A GitOps-oriented framework for automated test generation using LLMs.

## Overview
QitOps integrates automated testing into developer workflows by analyzing version control changes and generating contextual test cases. It follows a modular architecture allowing flexible integration with different VCS platforms and LLM providers.

## Key Features
- Pluggable VCS providers
- Interchangeable LLM backends
- Automated risk pattern analysis
- Context-aware test case generation
- Standard YAML/JSON output formats
- Extensible prompt engineering system

## Installation

```bash
git clone https://github.com/OuteniquaStudios/qitops.git
cd qitops
pip install -r requirements.txt
```

## Configuration

Create `config.yaml` from template:

```yaml
providers:
    vcs:
        type: github  # or bitbucket, codecommit
        token: your_token
    llm:
        type: ollama  # or openai, anthropic
        model: mistral
        temperature: 0.7
output:
    format: yaml
    file: test_cases.yaml
```

## Usage

```bash
python main.py <repo> <pr_number> [--output output.yaml] [--config config.yaml]
```

Example:
```bash
python main.py username/repo 123 --output test_cases.yaml
```

## Architecture

```
src/
├── core/           # Core business logic
│   ├── analyzer/   # Risk analysis engine
│   └── generator/  # Test case generation
├── providers/      # Provider implementations
│   ├── vcs/       # VCS integrations
│   └── llm/       # LLM backends
├── models/        # Domain models
├── services/      # Service abstractions
└── prompts/       # LLM prompt templates
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

AGPL-3.0 license