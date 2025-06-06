"""Custom tools for the cheap-research application."""

import os
import datetime
import re
from typing import List, Optional
from smolagents import tool

from .config import ConfigManager

@tool
def compile_latex_document(tex_file_path: str) -> str:
    """
    Compiles a LaTeX document using latexmk with the LuaLaTeX engine.
    This automatically handles multiple compilation passes for references, TOC, etc.
    
    Args:
        tex_file_path: Path to the LaTeX document to compile.
    
    Returns:
        A message indicating the result of the compilation.
    """
    import os
    import subprocess
    
    # Get current working directory as absolute path
    cwd = os.path.abspath(os.getcwd())
    
    # Normalize the path and make it absolute
    file_path = os.path.abspath(os.path.normpath(tex_file_path))
    
    # Security check: ensure the path is within the current working directory
    if not file_path.startswith(cwd):
        return f"Error: Cannot compile files outside the current working directory. Path: {tex_file_path}"
    
    # Check if file exists
    if not os.path.exists(file_path):
        return f"Error: File does not exist: {tex_file_path}"
    
    # Check if path is a .tex file
    if not file_path.endswith('.tex'):
        return f"Error: '{tex_file_path}' is not a LaTeX (.tex) file."
    
    # Get directory and filename
    file_dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    # Check if latexmk is installed
    try:
        result = subprocess.run(['latexmk', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return "Error: latexmk is not installed or not available in the system PATH."
    except FileNotFoundError:
        return "Error: latexmk is not installed or not available in the system PATH."
    
    try:
        # Run latexmk with lualatex engine
        result = subprocess.run(
            ['latexmk', '-lualatex', '-interaction=nonstopmode', filename],
            cwd=file_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output filename (change extension from .tex to .pdf)
        pdf_name = os.path.splitext(filename)[0] + '.pdf'
        pdf_path = os.path.join(file_dir, pdf_name)
        
        # Check if compilation was successful
        if result.returncode != 0 or not os.path.exists(pdf_path):
            # Extract error message from output
            error_lines = [line for line in result.stdout.split('\n') if 'error' in line.lower()]
            error_message = '\n'.join(error_lines) if error_lines else 'Unknown compilation error'
            return f"LaTeX compilation failed: {error_message}"
        
        # Get relative path for display
        rel_path = os.path.relpath(pdf_path, cwd)
        
        return f"LaTeX document successfully compiled: {rel_path}"
        
    except Exception as e:
        return f"Error during LaTeX compilation: {str(e)}"

@tool
def extract_pdf_text(url: str) -> str:
    """
    Fetches a PDF from the given URL and extracts its text content.
    Does not save the PDF file locally.
    
    Args:
        url: The URL of the PDF to process
        
    Returns:
        The extracted text content from the PDF
    """
    try:
        import requests
        import pymupdf
        import pymupdf4llm
    except ImportError:
        return "Error: Required packages not installed. Please install pymupdf and requests."
    
    try:
        # Fetch the PDF content
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 ..."})
        response.raise_for_status()
        
        # Process the PDF content directly
        pdf_document = pymupdf.Document(stream=response.content)
        markdown_content = pymupdf4llm.to_markdown(pdf_document)
        markdown_content = markdown_content.encode("ascii", "replace").decode("utf-8")
        max_output_length = 100000
        if len(markdown_content) > max_output_length:
            markdown_content = markdown_content[:max_output_length] + "\n\n[Content truncated due to length...]"


        return f"PDF Source: {url}\n\n" + markdown_content
    except requests.exceptions.RequestException as e:
        return f"Error fetching PDF: {str(e)}"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

@tool
def visit_webpage(url: str) -> str:
    """
    Visits a webpage at the given url and reads its content as a markdown string.
    Uses a custom user agent to avoid being blocked.
    
    Args:
        url: The url of the webpage to visit.
    
    Returns:
        The webpage content as markdown.
    """
    try:
        import requests
        from markdownify import markdownify
        from requests.exceptions import RequestException
    except ImportError as e:
        return (
            "You must install packages `markdownify` and `requests` to run this tool: "
            f"for instance run `pip install markdownify requests`. Error: {e}"
        )
    
    # Define headers with a user agent to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
    }
    
    try:
        # Send a GET request to the URL with headers and a 20-second timeout
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        
        # Add source URL at the beginning
        markdown_content = f"Source: {url}\n\n{markdown_content}"
        
        # Truncate content if it's too long (40,000 characters as in reference implementation)
        max_output_length = 100000
        if len(markdown_content) > max_output_length:
            markdown_content = markdown_content[:max_output_length] + "\n\n[Content truncated due to length...]"

        return markdown_content

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later or check the URL."
    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


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
    Reads the content of a file within the current working directory or its
    subdirectories. To avoid using too many tokens, do not print
    the full content of the file unless you have a good reason to do so.
    Instead, print a portion of the content.

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
    Creates a LaTeX document using a Jinja2 template and includes sections using \\input statements.
    
    Args:
        template_type: The type of template to use (e.g., "article", "beamer").
        output_filename: The name of the output LaTeX file.
        section_files: List of section files to include in the document.
            These files should be .tex files containing the content of each section,
            without the \\begin{document} and \\end{document} commands but 
            with appropriate \\section{} commands. You can use the
            writing_agent to generate these files, and to ensure they are
            in the correct format.
        title: Optional custom title for the document.
        author: Optional custom author for the document.
        date: Optional custom date for the document.
        abstract: Optional abstract file to include (for article template).
            The abstract file should be a .tex file containing the abstract content
            without the \\begin{abstract} and \\end{abstract} commands.
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
                rel_section_path = os.path.relpath(section_path, os.path.dirname(os.path.join(cwd, output_filename)))
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
                abstract_path = os.path.relpath(abs_abstract_path, os.path.dirname(os.path.join(cwd, output_filename)))
                abstract_path = abstract_path.replace('\\', '/')
            else:
                return f"Error: Abstract file does not exist: {abstract}"

        output_dir = cwd
        
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