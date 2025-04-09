import os

import tomli
import tomli_w
from xdg_base_dirs import xdg_config_home

# Updated path to use underscore instead of hyphen for consistency
config_dir = os.path.join(xdg_config_home(), "cheap_research")
config_file = os.path.join(config_dir, "config.toml")

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
            "list_files tool.\n"
            " 3. If there is insufficient information, repeat steps 1 and 2.\n"
            " 4. Plan the structure of the report and the content of each "
            "section.\n"
            " 5. Use the writing_agent to create a .bib file with all the "
            "citations.\n"
            " 6. Use the writing_agent to write each section or slide "
            "in a separate tex file. "
            "Make sure to check the files using the list_files tool.\n"
            " 7. Combine all the sections into a single tex file."
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
            "\nWhen requested to save a webpage, use the create_file tool "
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
            "- Note that you will be asked to write partial LaTeX documents, "
            "so do not include the \\documentclass or \\begin{document} "
            "commands in your responses Unless requested to do so.\n"
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