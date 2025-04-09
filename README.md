# Cheap Research

Agentic AI assistant for research based on smolagents.

## Description

Cheap Research is an AI-powered research assistant that helps you gather and analyze information on a given topic. It uses multiple specialized agents to perform different tasks like web searching, webpage analysis, and content creation.

## Features

- **Multi-agent system** - Specialized agents work together to complete research tasks:
  - **Orchestrator**: Coordinates all other agents and manages the research workflow
  - **Web Search Agent**: Finds information on topics through search engines
  - **Web Page Agent**: Visits specific webpages and saves their content to files
  - **Writing Agent**: Creates, reads, and edits content with full file management

- **File management capabilities**:
  - Create files with webpage content or generated text
  - Read existing files to analyze or summarize information
  - List available files and directories for easy navigation
  - Security features prevent directory traversal and ensure safe file operations

- **Research workflow**:
  1. Search for information on a topic
  2. Visit and save relevant webpages
  3. Read and analyze saved content
  4. Create reports and summaries based on research

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
- Writing Agent: Claude 3.7 Sonnet via OpenRouter

### Example Commands

- **Web search**: "Find information about quantum computing advances in 2024"
- **Save webpage content**: "Visit https://example.com and save the content to a file"
- **List files**: "Show me what files are in the saved_pages directory"
- **Read file**: "Read the content of saved_pages/quantum.md"
- **Create content**: "Create a summary of the quantum computing research I've saved"

## License

MIT License