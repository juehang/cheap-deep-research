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
            "Your report should include diagrams, tables, and other visual "
            "elements when appropriate.\n"
            "There should be on average at least one diagram or table per "
            "section unless you have a good reason not to include one.\n"
            "Note that your assistants have no memory of previous "
            "interactions, so you will need to ensure that they have all the "
            "information they need to complete their tasks.\n"
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
            "papers; this is preferable to the PDF version. "
            "They are accessible at https://arxiv.org/html/<arxiv_id>. "
            " 3. Use the writing_agent to create a references.bib file with "
            " citations if it does not already exist, and add any new "
            "citations to it.\n"
            " 4. If there is insufficient information, repeat steps 1, 2, and 3.\n"
            " 5. Plan the structure of the report and the content of each "
            "section.\n"
            " 6. Make figures using the plotting_agent as appropriate. "
            "You can also use TikZ to make diagrams by simply passing the "
            "TikZ code to the writing agent.\n"
            " 7. Use the writing_agent to write each section or slide "
            "in separate tex files with appropriate \\section{} commands. "
            "Make sure to check the files using the list_files tool. "
            "You are better at making diagrams than the writing_agent, "
            "so if you expect a TikZ diagram, include it in the prompt. "
            "Remind the writing_agent to use \\cite{} commands to cite "
            "references and to check references.bib for the correct citation "
            "keys. Also remind the writing_agent that it should not use "
            "the \\begin{document} and \\end{document} commands when writing "
            "sections. IMPORTANT: You must remind the writing agent to "
            "only use citation keys that are in the references.bib file, and "
            "to refer to the references.bib file, the other tex files, and "
            "the information collected from the web search agent."
            " 8. Remind the writing agent to verify that all citation keys "
            "are from the references.bib file. If additional citations are "
            "needed, repeat steps 1 and 2.\n"
            " 9. Use the create_latex_document tool to combine all the "
            "sections into a complete LaTeX document using either the article "
            "or beamer template, depending on the task.\n"
            " 10. Use the compile_latex_document tool to compile the LaTeX "
            "document into a PDF.\n"
            "Ensure that you finish all of the above steps before "
            "returning the final answer.\n"
        ),
        "reminders": (
            "REMINDER: The references.bib file must be created before "
            "writing the sections.\n"
            "REMINDER: Remind the writing_agent to only use citation keys "
            "that are in references.bib.\n"
            "REMINDER: Remind the writing_agent to read references.bib, "
            "the other tex files, and the information collected from the "
            "web search agent.\n"
            "REMINDER: Remind the writing_agent to verify that all citation "
            "keys are from references.bib before combining the sections.\n"
            "REMINDER: Use plots, diagrams, and tables to make the document "
            "more engaging.\n"
        ),
    },
    "web_search": {
        "model": "openrouter/mistralai/mistral-small-3.1-24b-instruct",
        "api_key": "",
        "additional_system_prompt": (
            "Respond in a very concise manner. Ensure that your responses are "
            "as short as possible while retaining all necessary information.\n"
            "Make sure to include the full URL of any webpages you collect.\n"
        ),
    },
    "web_page": {
        "model": "openrouter/mistralai/mistral-small-3.1-24b-instruct",
        "api_key": "",
        "additional_system_prompt": (
            "Respond in a very concise manner. Ensure that your responses are "
            "as short as possible while retaining all necessary information.\n"
            "Make sure you do not include unnecessary formatting carried over "
            "from the webpage. This cannot be done by coding, so you must "
            "manually remove it and otherwise clean up the text.\n"
            "This means that you should not directly save the webpage content "
            "to a file without first cleaning it up!\n"
            "Use the create_file tool "
            "to save the page content to a file in the specified location. "
            "Use markdown files for webpage content and "
            "choose a short filename based on the page title.\n"
            "Do not pass a variable from another tool directly to the "
            "create_file tool. Instead, this tool should be called with "
            "your own writing, which should be the cleaned up content "
            "of the webpage that you have visited.\n"
            "Include the filename in your response.\n"
            "Use the extract_pdf_text if the webpage is a PDF.\n"
            "If you encounter an error, report it to your manager "
            "and ask for help. Do not attempt to fix the error yourself.\n"
            "Do NOT use coding to clean up content. Write it yourself. "
            "Do NOT use strip to clean up content. Write it yourself. "
            "As you are very hardworking, you should be able to write long "
            "documents without making mistakes.\n"
            "IMPORTANT: Within the file, make sure to include sufficient "
            "information to fully cite the webpage, including the URL, "
            "author, DOI, title, and date of publication, when available.\n"

        ),
    },
    "writing": {
        "model": "openrouter/anthropic/claude-3.5-haiku",
        "api_key": "",
        "additional_system_prompt": (
            "As a specialized writing assistant, you can read files, list "
            "available files, and create new files with content.\n"
            "When writing content, follow these guidelines:\n"
            "- Use clear, concise language appropriate for the requested "
            "content type\n"
            "- Properly attribute any sources used in your writing. "
            "If you are writing a LaTeX document, use the \\cite{} command "
            "to cite sources, as there will be a separate .bib file for "
            "references. Read the references.bib file to ensure that you"
            " know which references are available. If you need a new reference,"
            " ask your manager to add it to the references.bib file.\n"
            "- For LaTeX files, be sure to include the appropriate \\section{} "
            "commands in each file if the content is for a document, or the"
            " appropriate \\begin{frame} and \\end{frame} commands if the "
            "content is for a presentation.\n"
            "- When writing a LaTeX document, do not split content into "
            "too many small subsections. Instead, organize the content "
            "as peer-reviewed articles do.\n"
            "- Format content appropriately based on the file type and "
            "purpose.\n"
            "- For markdown files, use proper markdown syntax for headings, "
            "lists, etc.\n"
            "- Always save files with appropriate extensions "
            "(.md, .tex, .bib, etc.)\n"
            "- Include the filename in your response.\n"
            "- Unless requested, do not include the whole file content in "
            "your response; instead, provide a brief summary of the content.\n"
            "- Minimize use of lists or numbered lists. "
            "Instead, write the content in a coherent paragraph.\n"
            "- IMPORTANT: Make sure to review other files in the directory "
            "to ensure consistency and coherence. This includes both other "
            "LaTeX files and files that contain paper summaries."
            "- Use tables to organize data when appropriate.\n"
        ),
    },
    "plotting": {
        "model": "openrouter/anthropic/claude-3.5-haiku",
        "api_key": "",
        "additional_system_prompt": (
            "You are skilled at data visualization and can create "
            "matplotlib code to generate plots.\n"
            "Make sure to save the plot either as a .png or a .pdf "
            "file.\n"
            "Include the filename in your response.\n"
            "If you are unable to make your code work, try asking "
            "your manager for help.\n"
        ),
    },
    "file_saving": {
        "enabled": True,
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
