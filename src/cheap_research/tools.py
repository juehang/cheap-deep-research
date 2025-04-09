"""Custom tools for the cheap-research application."""

import os
from smolagents import tool


@tool
def create_file(content: str, filename: str) -> str:
    """
    Creates a file with the given content at the specified path.
    The file must be within the current working directory or its subdirectories.
    
    Args:
        content: The content to write to the file.
        filename: The name of the file to create (can include subdirectories).
                  Example: "data/webpage.html" or "output.txt"
    
    Returns:
        A message indicating the result of the operation.
    """
    # Get current working directory as absolute path
    cwd = os.path.abspath(os.getcwd())
    
    # Normalize the path and make it absolute 
    # (handles both relative and already absolute paths)
    file_path = os.path.abspath(os.path.normpath(filename))
    
    # Security check: ensure the path is within the current working directory
    if not file_path.startswith(cwd):
        return f"Error: Cannot write files outside the current working directory. Path: {filename}"
    
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # Write content to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Return relative path from CWD for cleaner output
        rel_path = os.path.relpath(file_path, cwd)
        return f"File successfully created at: {rel_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"
