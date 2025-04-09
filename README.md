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

- **LaTeX document generation**:
  - Built-in LaTeX templates for articles and presentations
  - Combine section files into complete LaTeX documents
  - Support for customizing title, author, date, and other parameters
  - Templates stored in user configuration directory for easy customization

- **Research workflow**:
  1. Search for information on a topic
  2. Visit and save relevant webpages
  3. Read and analyze saved content
  4. Write sections for a LaTeX document
  5. Generate a complete LaTeX document from your sections

## Installation

### Requirements
- Python 3.11 or higher
- Required packages: smolagents, jinja2, and more (see pyproject.toml)

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
- **List LaTeX templates**: "What LaTeX templates are available?"
- **Create LaTeX document**: "Create a LaTeX article with introduction.tex and methods.tex as sections"

### LaTeX Template System

The research assistant includes a LaTeX template system that can combine section files into complete documents:

1. **Available Templates**:
   - `article`: Standard article format with academic styling
   - `beamer`: Presentation slides with the Madrid theme

2. **Creating LaTeX Documents**:
   - Write individual section files using the writing agent
   - Each section file should include its own `\section{}` commands
   - Use the `create_latex_document` tool to combine sections into a complete document
   - Generated documents are saved to the `latex_docs` directory

3. **Template Customization**:
   - Templates are stored in your user config directory
   - You can edit these templates to customize the styling or structure
   - Templates use Jinja2 syntax for variable substitution and loops

## License

MIT License