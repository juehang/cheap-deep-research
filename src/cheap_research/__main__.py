from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
)

from .config import ConfigManager
from .tools import (
    create_file, list_files, read_file, list_latex_templates, 
    create_latex_document, compile_latex_document, visit_webpage, extract_pdf_text,
)
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

def main():
    """
    Main entry point for the cheap-research application.
    Initializes the configuration and sets up the agents.
    """
    # Initialize Phoenix
    register()
    SmolagentsInstrumentor().instrument()

    # Initialize configuration
    config_manager = ConfigManager()

    if not config_manager.config["initialized"]:
        print("Please edit the configuration file and run the program again.")
        return

    # Initialize models
    orchestrator_model = LiteLLMModel(
        model_id=config_manager.config["orchestrator"]["model"],
        api_key=config_manager.config["orchestrator"]["api_key"],
        )

    web_search_model = LiteLLMModel(
        model_id=config_manager.config["web_search"]["model"],
        api_key=config_manager.config["web_search"]["api_key"],
        )
    
    web_page_model = LiteLLMModel(
        model_id=config_manager.config["web_page"]["model"],
        api_key=config_manager.config["web_page"]["api_key"],
        )

    writing_model = LiteLLMModel(
        model_id=config_manager.config["writing"]["model"],
        api_key=config_manager.config["writing"]["api_key"],
        )

    plotting_model = LiteLLMModel(
    model_id=config_manager.config["plotting"]["model"],
    api_key=config_manager.config["plotting"]["api_key"],
    )

    # Initialize tools
    web_search_agent = ToolCallingAgent(
        tools=[DuckDuckGoSearchTool()],
        model=web_search_model,
        max_steps=10,
        name="web_search_agent",
        description=(
            "Runs web searches for you.\n"
            "Only ask for one search at a time, as you are better at "
            "understanding context than this agent is.\n"
            ),
    )

    # Add file saving capability to web page agent with our custom webpage tool
    web_page_agent = CodeAgent(
        tools=[visit_webpage, extract_pdf_text, create_file],
        model=web_page_model,
        max_steps=10,
        name="web_page_agent",
        description=(
            "Accesses web pages for you and can save page content to files. "
            "Make sure to only ask for one web page at a time."
            "This agent can extract text from PDFs, but text-based "
            "formats such as markdown or HTML are preferred.\n"
            "If you are trying to read an arXiv paper, be sure to "
            "try the HTML version of the paper first. Remember "
            "that you can change an arXiv URL to the HTML version "
            "by replacing the 'abs' in the URL with 'html'. "
            "If possible, prompt this agent to use the HTML version "
            "of the paper.\n"
            "VERY IMPORTANT: Remind the agent to clean up the webpage content "
            "and save his own writing to a file, not the raw webpage content. "
            "This is the most common mistake made by this agent, so emphasize "
            "the importance of this step. The agent will be confused if you "
            "just say to clean up; you must remind the agent to save his own "
            "writing and to NOT use coding to clean up the webpage content.\n"
            "Give the agent a filename with a .md extension."
            ),
    )

    # Create the writing agent with file management capabilities
    writing_agent = ToolCallingAgent(
        tools=[list_files, create_file, read_file],
        model=writing_model,
        max_steps=15,  # More steps for complex writing tasks
        name="writing_agent",
        description=(
            "Creates, reads, and edits text content. Can work files to "
            "summarize information, reformat content, or create original "
            "writings. Remember that the writing agent needs to be "
            "provided with a bib file for citations when writing.\n"
            "Make sure to only ask for one writing task at a time.\n"
            "Make sure to prompt the writing agent with TikZ diagrams "
            "when you want to include diagrams in your writing.\n"
            "If you want this agent to write a section, make sure to "
            "remind it about any files it should read, including "
            "both the relevant content files and the references file.\n"
            "You should mention the filenames of the files you want the "
            "agent to read EXPLICITLY.\n"
            "Also include the filename of any saved diagrams in your "
            "request.\n"
            ),
    )

    plotting_agent = CodeAgent(
        tools=[list_files, create_file, read_file],
        model=plotting_model,
        max_steps=10,
        name="plotting_agent",
        additional_authorized_imports=[
                "time", "numpy", "pandas", "matplotlib"
            ],
        description=(
            "Makes plots and diagrams. Can create plots from data and "
            "save them as PDF or PNG files. Can also create TikZ diagrams "
            "for inclusion in LaTeX documents.\n"
            "Make sure to only ask for one plotting task at a time.\n"
            ),
    )


    
    web_search_agent.prompt_templates["system_prompt"] = (
        web_search_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["web_search"]["additional_system_prompt"]
    )

    web_page_agent.prompt_templates["system_prompt"] = (
        web_page_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["web_page"]["additional_system_prompt"]
    )

    writing_agent.prompt_templates["system_prompt"] = (
        writing_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["writing"]["additional_system_prompt"]
    )

    plotting_agent.prompt_templates["system_prompt"] = (
        plotting_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["plotting"]["additional_system_prompt"]
    )

    # Add LaTeX tools and file management tools to the orchestrator
    manager_agent = CodeAgent(
        tools=[
                list_files, list_latex_templates, read_file, create_latex_document,
            compile_latex_document,
            ],
        model=orchestrator_model,
        managed_agents=[
                web_search_agent, web_page_agent, writing_agent, plotting_agent
            ],
        additional_authorized_imports=[
                "time", "numpy", "pandas",
            ],
        planning_interval=6,
        max_steps=30,
    )

    manager_agent.prompt_templates["system_prompt"] = (
        manager_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["orchestrator"]["additional_system_prompt"]
    )
    manager_agent.prompt_templates["planning"]["update_plan_post_messages"] = (
        manager_agent.prompt_templates["planning"]["update_plan_post_messages"]
        + "\n"
        + config_manager.config["orchestrator"]["reminders"]
    )

    # Welcome message
    print("Research assistant is ready. Type 'exit' to quit.")
    print("Available LaTeX templates: " + ", ".join(config_manager.config["latex"]["available_templates"]))

    # Simple interactive loop
    while True:
        try:
            user_input = input("\nWhat would you like to research? > ")

            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                print("Exiting research assistant. Goodbye!")
                break

            if not user_input.strip():
                continue
            
            # Process the user input with the manager agent
            print("\nProcessing your request...")
            response = manager_agent.run(user_input, reset=False)
            
            # Display the response
            print("\n--- Research Results ---")
            print(response)
            print("----------------------")
            
        except KeyboardInterrupt:
            print("\nOperation interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again with a different query.")
    
    print("Research assistant has been shut down.")

if __name__ == "__main__":
    main()