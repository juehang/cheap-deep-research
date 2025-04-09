"""Custom tools for the cheap-research application."""

import os
import datetime
from typing import List, Optional
from smolagents import tool

from .config import ConfigManager


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


@tool
def read_file(filename: str, encoding: str = "utf-8") -> str:
    """
    Reads the content of a file within the current working directory or its subdirectories.
    
    Args:
        filename: The name of the file to read (can include subdirectories).
                  Example: "saved_pages/article.md" or "notes.txt"
        encoding: The character encoding of the file (default: utf-8)
    
    Returns:
        The content of the file as a string.
    """
    # Get current working directory as absolute path
    cwd = os.path.abspath(os.getcwd())
    
    # Normalize the path and make it absolute
    file_path = os.path.abspath(os.path.normpath(filename))
    
    # Security check: ensure the path is within the current working directory
    if not file_path.startswith(cwd):
        return f"Error: Cannot read files outside the current working directory. Path: {filename}"
    
    # Check if file exists
    if not os.path.exists(file_path):
        return f"Error: File does not exist: {filename}"
    
    # Check if path is a file (not a directory)
    if not os.path.isfile(file_path):
        return f"Error: '{filename}' is not a file."
    
    try:
        # Get file metadata
        size = os.path.getsize(file_path)
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        # Format modification time
        time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Read file content
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Format response with metadata and content
        rel_path = os.path.relpath(file_path, cwd)
        metadata = f"File: {rel_path} ({size_str}, last modified: {time_str})\n\n"
        return metadata + content
    
    except UnicodeDecodeError:
        return f"Error: File '{filename}' is not a text file or uses a different encoding than {encoding}."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_files(directory: str = "") -> str:
    """
    Lists files and directories in the specified directory.
    The directory must be within the current working directory or its subdirectories.
    If no directory is specified, lists files in the current working directory.
    
    Args:
        directory: The directory to list files from (can include subdirectories).
                   Example: "saved_pages" or "data"
                   Default is the current directory if not specified.
    
    Returns:
        A formatted list of files and directories.
    """
    # Get current working directory as absolute path
    cwd = os.path.abspath(os.getcwd())
    
    # If directory is empty, use current working directory
    if not directory:
        target_dir = cwd
        rel_dir = "."
    else:
        # Normalize the path and make it absolute
        target_dir = os.path.abspath(os.path.normpath(directory))
        
        # Security check: ensure the path is within the current working directory
        if not target_dir.startswith(cwd):
            return f"Error: Cannot list files outside the current working directory. Path: {directory}"
        
        # Check if directory exists
        if not os.path.exists(target_dir):
            return f"Error: Directory does not exist: {directory}"
        
        # Get relative path for display
        rel_dir = os.path.relpath(target_dir, cwd)
    
    # Check if the target is actually a directory
    if not os.path.isdir(target_dir):
        return f"Error: '{rel_dir}' is not a directory."
    
    try:
        # Get all files and directories in the target directory
        items = os.listdir(target_dir)
        
        # If no files found
        if not items:
            return f"No files found in directory: {rel_dir}"
        
        # Format the output
        result = [f"Files and directories in '{rel_dir}':\n"]
        
        # Sort items: directories first, then files
        dirs = []
        files = []
        
        for item in items:
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)
        
        # Add directories to result
        if dirs:
            result.append("Directories:")
            for d in sorted(dirs):
                result.append(f"  📁 {d}/")
        
        # Add files to result with size and modification time
        if files:
            result.append("\nFiles:")
            for f in sorted(files):
                file_path = os.path.join(target_dir, f)
                size = os.path.getsize(file_path)
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Format size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                
                # Format modification time
                time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
                
                result.append(f"  📄 {f} ({size_str}, {time_str})")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error listing files: {str(e)}"


@tool
def list_latex_templates() -> str:
    """
    Lists all available LaTeX templates in the config directory.
    
    Returns:
        A formatted list of available LaTeX templates.
    """
    config_manager = ConfigManager()
    templates = config_manager.config["latex"]["available_templates"]
    templates_dir = config_manager.config["latex"]["templates_directory"]
    
    if not templates:
        return "No LaTeX templates available."
    
    result = ["Available LaTeX templates:"]
    
    for template in sorted(templates):
        template_path = os.path.join(templates_dir, f"{template}.tex.j2")
        if os.path.exists(template_path):
            result.append(f"  📄 {template} - Available")
        else:
            result.append(f"  ❌ {template} - Missing")
    
    result.append("\nUse create_latex_document to create a document using one of these templates.")
    
    return "\n".join(result)


@tool
def create_latex_document(
    template_type: str,
    output_filename: str,
    section_files: List[str],
    title: Optional[str] = None,
    author: Optional[str] = None,
    date: Optional[str] = None,
    abstract: Optional[str] = None,
    institute: Optional[str] = None
) -> str:
    """
    Creates a LaTeX document using a Jinja2 template and includes sections using \input statements.
    
    Args:
        template_type: The type of template to use (e.g., "article", "beamer").
        output_filename: The name of the output LaTeX file.
        section_files: List of section files to include in the document.
        title: Optional custom title for the document.
        author: Optional custom author for the document.
        date: Optional custom date for the document.
        abstract: Optional abstract file to include (for article template).
        institute: Optional institute name (for beamer template).
        
    Returns:
        A message indicating the result of the operation.
    """
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        return "Error: Jinja2 is not installed. Please install it with 'pip install jinja2'."
    
    # Get current working directory as absolute path
    cwd = os.path.abspath(os.getcwd())
    
    # Initialize config manager to get template info
    config_manager = ConfigManager()
    templates_dir = config_manager.config["latex"]["templates_directory"]
    available_templates = config_manager.config["latex"]["available_templates"]
    latex_output_dir = config_manager.config["latex"]["output_directory"]
    
    # Validate template_type
    if template_type not in available_templates:
        templates_list = ", ".join(available_templates)
        return f"Error: Invalid template type '{template_type}'. Available templates: {templates_list}"
    
    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=False,  # Don't escape LaTeX syntax
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    try:
        # Load the template
        template = env.get_template(f"{template_type}.tex.j2")
        
        # Validate section files
        valid_section_files = []
        missing_section_files = []
        
        for section_file in section_files:
            section_path = os.path.join(cwd, section_file)
            if os.path.exists(section_path) and os.path.isfile(section_path):
                # Use relative paths for \input statements
                rel_section_path = os.path.relpath(section_path, os.path.dirname(os.path.join(cwd, latex_output_dir, output_filename)))
                # Replace backslashes with forward slashes for LaTeX
                rel_section_path = rel_section_path.replace('\\', '/')
                valid_section_files.append(rel_section_path)
            else:
                missing_section_files.append(section_file)
        
        if missing_section_files:
            missing_list = ", ".join(missing_section_files)
            return f"Error: The following section files do not exist: {missing_list}"
        
        # Validate abstract file if provided
        abstract_path = None
        if abstract:
            abs_abstract_path = os.path.join(cwd, abstract)
            if os.path.exists(abs_abstract_path) and os.path.isfile(abs_abstract_path):
                # Use relative path for \input statement
                abstract_path = os.path.relpath(abs_abstract_path, os.path.dirname(os.path.join(cwd, latex_output_dir, output_filename)))
                abstract_path = abstract_path.replace('\\', '/')
            else:
                return f"Error: Abstract file does not exist: {abstract}"
                
        # Create output directory if it doesn't exist
        output_dir = os.path.join(cwd, latex_output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Ensure filename has .tex extension
        if not output_filename.endswith('.tex'):
            output_filename += '.tex'
        output_path = os.path.join(output_dir, output_filename)
        
        # Render the template with data
        template_data = {
            "title": title,
            "author": author,
            "date": date,
            "sections": valid_section_files
        }
        
        # Add template-specific variables
        if template_type == "article" and abstract_path:
            template_data["abstract"] = abstract_path
        elif template_type == "beamer" and institute:
            template_data["institute"] = institute
            
        rendered_template = template.render(**template_data)
        
        # Write the rendered template to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_template)
        
        # Return success message
        rel_output_path = os.path.relpath(output_path, cwd)
        return (
            f"LaTeX document successfully created at: {rel_output_path}\n"
            f"Template used: {template_type}\n"
            f"Section files included: {len(valid_section_files)}\n"
            f"You can now compile this LaTeX document to generate the final output."
        )
        
    except Exception as e:
        return f"Error creating LaTeX document: {str(e)}"