from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    VisitWebpageTool,
)

from .config import ConfigManager
from .tools import create_file

def main():
    """
    Main entry point for the cheap-research application.
    Initializes the configuration and sets up the agents.
    """
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

    # Initialize tools
    web_search_agent = ToolCallingAgent(
        tools=[DuckDuckGoSearchTool()],
        model=web_search_model,
        max_steps=10,
        name="web_search_agent",
        description=(
            "Runs web searches for you."
            ),
    )
    
    # Add file saving capability to web page agent
    web_page_agent = ToolCallingAgent(
        tools=[VisitWebpageTool(), create_file],
        model=web_page_model,
        max_steps=10,
        name="web_page_agent",
        description=(
            "Accesses web pages for you and can save page content to files. "
            "Make sure to only ask for one web page at a time."
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
    
    manager_agent = CodeAgent(
        tools=[],
        model=orchestrator_model,
        managed_agents=[web_search_agent, web_page_agent],
        additional_authorized_imports=["time", "numpy", "pandas", "matplotlib"],
    )
    
    manager_agent.prompt_templates["system_prompt"] = (
        manager_agent.prompt_templates["system_prompt"]
        + "\n"
        + config_manager.config["orchestrator"]["additional_system_prompt"]
    )
    
    # Ensure the default save directory exists
    import os
    default_save_dir = config_manager.config["file_saving"]["default_directory"]
    if not os.path.exists(default_save_dir):
        os.makedirs(default_save_dir, exist_ok=True)
        print(f"Created default save directory: {default_save_dir}")
    
    # Welcome message
    print("Research assistant is ready. Type 'exit' to quit.")
    print(f"Webpage content can be saved to files in the '{default_save_dir}' directory.")
    
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
            response = manager_agent.run(user_input)
            
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