import subprocess
import os

def execute_command(command: str) -> str:
    """Executes a shell command on the local machine and returns the output."""
    try:
        # Note: In a real production system, you'd want to be VERY careful with shell commands!
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"
    except Exception as e:
         return f"Unexpected error: {str(e)}"

def read_file(filepath: str) -> str:
    """Reads the contents of a local file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a local file, overwriting if it exists."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file {filepath}: {str(e)}"
