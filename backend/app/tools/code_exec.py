import subprocess
import sys
import tempfile

from langchain_core.tools import tool


@tool
def code_exec(code: str) -> str:
    """Execute Python code in a sandboxed subprocess and return stdout/stderr. Use for calculations, data processing, or generating outputs programmatically."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tempfile.gettempdir(),
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            return output.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out after 30 seconds."
        except Exception as e:
            return f"Error executing code: {e}"
