import os
import shutil

import tomli
import tomli_w
from xdg_base_dirs import xdg_config_home

# Updated path to use underscore instead of hyphen for consistency
config_dir = os.path.join(xdg_config_home(), "cheap_research")
config_file = os.path.join(config_dir, "config.toml")
templates_dir = os.path.join(config_dir, "templates")

DEFAULTS = {
    "initialized": False,
    "orchestrator": {
        "model": "openrouter/anthropic/claude-3.7-sonnet",
        "api_key": "",
        "additional_system_prompt": (
            "As an expert PhD-level researcher, you will coordinate a team of "
            "research assistant agents with specialized tools to gather and "
            "analyze information on a given topic. Your goal is to produce a "
            "comprehensive and well-researched report on the topic.\n"
            "You will ensure that all information is appropriately cited and "
            "that the report is well-structured and easy to read.\n"
            "All citations must be verified by your research assistants."
            "Break up your research into smaller tasks and assign them to your "
            "research assistant agents. For example, you can have one task "
            "about gathering relevant web pages, and then have other tasks about "
            "analyzing and summarizing the information on those web pages.\n"
            "The workflow should be as such: \n"
            " 1. Gather relevant information. Prefer academic sources.\n"
            " 2. Use the web_page_agent to visit the web pages and save the "
            "content to files. Make sure to check the files using the "
            "list_files tool. Note that arXiv offers a HTML version of "
            "papers that should be used. "
            "They are accessible at https://arxiv.org/html/<arxiv_id>. "
            "The web_page_agent cannot understand PDFs."
            " 3. If there is insufficient information, repeat steps 1 and 2.\n"
            " 4. Plan the structure of the report and the content of each "
            "section.\n"
            " 5. Use the writing_agent to create a references.bib file with "
            " citations.\n"
            " 6. Make figures using matplotlib as appropriate.\n"
            " 7. Use the writing_agent to write each section or slide "
            "in separate tex files with appropriate \\section{} commands. "
            "Make sure to check the files using the list_files tool. "
            "You are better at making diagrams than the writing_agent, "
            "so if you expect a TikZ diagram, include it in the prompt. "
            "Remind the writing_agent to use \\cite{} commands to cite "
            "references and to check references.bib for the correct citation "
            "keys. "
            " 8. Use the create_latex_document tool to combine all the "
            "sections into a complete LaTeX document using either the article "
            "or beamer template, depending on the task.\n"
        ),
    },
    "web_search": {
        "model": "openrouter/mistralai/mistral-small-24b-instruct-2501",
        "api_key": "",
        "additional_system_prompt": (
            "Respond in a very concise manner. Ensure that your responses are "
            "as short as possible while retaining all necessary information.\n"
            "Make sure to include the full URL of any webpages you collect.\n"
        ),
    },
    "web_page": {
        "model": "openrouter/mistralai/mistral-small-24b-instruct-2501",
        "api_key": "",
        "additional_system_prompt": (
            "Respond in a very concise manner. Ensure that your responses are "
            "as short as possible while retaining all necessary information.\n"
            "Use the create_file tool "
            "to save the page content to a file in the specified location. "
            "Default to markdown files for webpage content and "
            "choose descriptive filenames based on the page title or URL. "
            "Within the file, make sure to include sufficient information "
            "to fully cite the webpage, including the URL, author, and "
            "date of publication, when available.\n"
            "Include the filename in your response.\n"
        ),
    },
    "writing": {
        "model": "openrouter/mistralai/mistral-small-24b-instruct-2501",
        "api_key": "",
        "additional_system_prompt": (
            "As a specialized writing assistant, you can read files, list "
            "available files, and create new files with content.\n"
            "When writing content, follow these guidelines:\n"
            "- Use clear, concise language appropriate for the requested "
            "content type\n"
            "- Properly attribute any sources used in your writing\n"
            "- Format content appropriately based on the file type and "
            "purpose\n"
            "- For markdown files, use proper markdown syntax for headings, "
            "lists, etc.\n"
            "- Always save files with appropriate extensions "
            "(.md, .tex, .bib, etc.)\n"
            "- For LaTeX files, be sure to include the appropriate \\section{} "
            "commands in each file if the content is for a document, or the"
            " appropriate \\begin{frame} and \\end{frame} commands if the "
            "content is for a presentation.\n"
            "Include the filename in your response.\n"
        ),
    },
    "file_saving": {
        "enabled": True,
        "default_directory": "saved_pages"  # Relative to working directory
    },
    "file_listing": {
        "enabled": True,
        "show_file_sizes": True,
        "show_modification_times": True
    },
    "latex": {
        "templates_directory": templates_dir,
        "available_templates": ["article", "beamer"],
        "default_template": "article",
        "output_directory": "latex_docs"  # Relative to working directory
    }
}


class ConfigManager:
    """
    Manages the configuration of the research agent.
    """

    def __init__(self):
        if not os.path.exists(config_file):
            os.makedirs(config_dir, exist_ok=True)
            with open(config_file, "wb") as f:
                tomli_w.dump(DEFAULTS, f)
        with open(config_file, "rb") as f:
            self.config = tomli.load(f)

        # Ensure all default values are present
        self.ensure_defaults()
        
        # Ensure LaTeX templates exist in config directory
        self.ensure_latex_templates()

    def reload(self):
        with open(config_file, "rb") as f:
            self.config = tomli.load(f)

    def save(self):
        with open(config_file, "wb") as f:
            tomli_w.dump(self.config, f)

    def ensure_defaults(self):
        """
        Ensure that all default configuration values are present in the current
        configuration. If any are missing, add them, print to console, and save
        the configuration.
        """
        changed = False

        def update_recursively(config, defaults, path=""):
            nonlocal changed

            for key, default_value in defaults.items():
                current_path = f"{path}.{key}" if path else key

                # If the key doesn't exist in the config, add it
                if key not in config:
                    config[key] = default_value
                    print(f"Added missing configuration entry: {current_path}")
                    changed = True
                # If the value is a dictionary, recursively update it
                elif isinstance(default_value, dict) and isinstance(
                    config[key], dict,
                ):
                    update_recursively(
                        config[key], default_value, current_path,
                    )

        update_recursively(self.config, DEFAULTS)

        if changed:
            self.save()
            print("Configuration file updated with new default values")
    
    def ensure_latex_templates(self):
        """
        Ensure that LaTeX templates exist in the config directory.
        If they don't exist, copy them from the package templates directory.
        """
        # Create templates directory in config directory if it doesn't exist
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)
            
        # Get the package templates directory path
        package_templates_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        
        # Copy templates if they don't exist in config directory
        for template_name in self.config["latex"]["available_templates"]:
            template_file = f"{template_name}.tex.j2"
            config_template_path = os.path.join(templates_dir, template_file)
            package_template_path = os.path.join(package_templates_dir, template_file)
            
            if not os.path.exists(config_template_path) and os.path.exists(package_template_path):
                shutil.copy2(package_template_path, config_template_path)
                print(f"Copied LaTeX template {template_file} to config directory")
