# Cheap Research

Agentic AI assistant for research based on smolagents.

## Description

Cheap Research is an AI-powered research assistant that helps you gather and analyze information on a given topic. It uses multiple specialized agents to perform different tasks like web searching and webpage analysis.

## Installation

### Requirements
- Python 3.11 or higher

### Install from source
```bash
git clone https://github.com/your-username/cheap-research.git
cd cheap-research
pip install -e .
```

### Install from PyPI
```bash
pip install cheap-research
```

## Usage

After installation, you can run the research assistant from the command line:

```bash
cheapresearch
```

On first run, a configuration file will be created at `~/.config/cheap_research/config.toml` (Linux/macOS) or in the appropriate XDG config location on your system. You'll need to edit this file to add your API keys before running the assistant again.

### Configuration

Edit the configuration file to add your API keys and customize the behavior of the research assistant. The default configuration uses the following models:
- Orchestrator: Claude 3.7 Sonnet via OpenRouter
- Web Search: Mistral Small 24B via OpenRouter
- Web Page Analysis: Mistral Small 24B via OpenRouter

## License

MIT License
