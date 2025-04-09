"""Custom tools for the cheap-research application."""

import os
import datetime
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