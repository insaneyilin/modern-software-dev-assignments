import ast
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Callable

from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 3

# Tool calling flow: (in mermaid markdown)
# flowchart LR
#     A[Tool Definitions] --> B[LLM Generates<br/>Structured Output]
#     B --> C[Parse & Validate]
#     C --> D[Tool Registry<br/>Name → Function]
#     D --> E[Execute]
#     E --> F[Tool Result]
#     style A fill:#e1f5ff
#     style B fill:#fff4e1
#     style D fill:#e8f5e9
#     style E fill:#f3e5f5
#     style F fill:#c8e6c9

# ==========================
# Tool implementation (the "executor")
# ==========================
def _annotation_to_str(annotation: Optional[ast.AST]) -> str:
    if annotation is None:
        return "None"
    try:
        return ast.unparse(annotation)  # type: ignore[attr-defined]
    except Exception:
        # Fallback best-effort
        if isinstance(annotation, ast.Name):
            return annotation.id
        return type(annotation).__name__


def _list_function_return_types(file_path: str) -> List[Tuple[str, str]]:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    results: List[Tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return_str = _annotation_to_str(node.returns)
            results.append((node.name, return_str))
    # Sort for stable output
    results.sort(key=lambda x: x[0])
    return results


def output_every_func_return_type(file_path: str = None) -> str:
    """Tool: Return a newline-delimited list of "name: return_type" for each top-level function."""
    path = file_path or __file__
    if not os.path.isabs(path):
        # Try file relative to this script if not absolute
        candidate = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(candidate):
            path = candidate
    pairs = _list_function_return_types(path)
    return "\n".join(f"{name}: {ret}" for name, ret in pairs)


# Sample functions to ensure there is something to analyze
def add(a: int, b: int) -> int:
    return a + b


def greet(name: str) -> str:
    return f"Hello, {name}!"

# Tool registry for dynamic execution by name
TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "output_every_func_return_type": output_every_func_return_type,
}

# ==========================
# Prompt scaffolding
# ==========================

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
You are a helpful assistant that can call tools to help you complete tasks.

Available tools:
- output_every_func_return_type: Analyzes a Python file and returns a newline-delimited list of "name: return_type" for each top-level function. This tool accepts an optional parameter "file_path" (string). If not provided, it will analyze the current file.

When asked to call a tool, you must respond with a valid JSON object in the following format:
{
  "tool": "tool_name",
  "args": {
    "parameter_name": "parameter_value"
  }
}

Important instructions:
1. Output ONLY the JSON object, no additional text, explanations, or markdown formatting
2. The "tool" field must be a string containing the exact tool name
3. The "args" field must be an object (dictionary) containing the tool parameters
4. If a parameter is optional and you don't need to specify it, you can omit it from "args" or use an empty object

Example tool call:
{
  "tool": "output_every_func_return_type",
  "args": {}
}

When the user asks you to call the tool, respond with the JSON tool call immediately.

NOTE: Do not include any markdown, code fences, explanations, or other text. Output only the raw JSON object.
"""


def resolve_path(p: str) -> str:
    if os.path.isabs(p):
        return p
    here = os.path.dirname(__file__)
    c1 = os.path.join(here, p)
    if os.path.exists(c1):
        return c1
    # Try sibling of project root if needed
    return p


def extract_tool_call(text: str) -> Dict[str, Any]:
    """Parse a single JSON object from the model output."""
    text = text.strip()
    # Some models wrap JSON in code fences; attempt to strip
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json\n"):
            text = text[5:]
    try:
        obj = json.loads(text)
        return obj
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON for the tool call")


def run_model_for_tool_call(system_prompt: str) -> Dict[str, Any]:
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Call the tool now."},
        ],
        options={"temperature": 0.3},
    )
    content = response.message.content
    return extract_tool_call(content)


def execute_tool_call(call: Dict[str, Any]) -> str:
    """
    Execute a tool call based on the JSON structure returned by the LLM.
    
    This function is the core of the tool calling mechanism. It demonstrates how
    an LLM's structured output (JSON) is translated into actual function execution.
    
    Tool calling flow:
    1. LLM generates a JSON tool call: {"tool": "tool_name", "args": {...}}
    2. This function parses the JSON and looks up the tool in the registry
    3. The tool function is executed with the provided arguments
    4. The tool's return value is passed back to the caller
    
    Args:
        call: A dictionary containing the tool call structure:
            - "tool": str, the name of the tool to execute (must exist in TOOL_REGISTRY)
            - "args": dict, the arguments to pass to the tool function
    
    Returns:
        str: The result returned by the executed tool function
    
    Raises:
        ValueError: If the tool call structure is invalid or the tool doesn't exist
    """
    # Step 1: Extract and validate the tool name from the LLM's JSON response
    # The LLM should have generated a JSON with a "tool" field containing the tool name
    name = call.get("tool")
    if not isinstance(name, str):
        raise ValueError("Tool call JSON missing 'tool' string")
    
    # Step 2: Look up the actual Python function in the tool registry
    # The registry maps tool names (strings) to callable functions
    # This is how we bridge from the LLM's text output to executable code
    func = TOOL_REGISTRY.get(name)
    if func is None:
        raise ValueError(f"Unknown tool: {name}")
    
    # Step 3: Extract and validate the arguments dictionary
    # The LLM should have provided an "args" object with parameter key-value pairs
    args = call.get("args", {})
    if not isinstance(args, dict):
        raise ValueError("Tool call JSON 'args' must be an object")

    # Step 4: Preprocess arguments (path resolution for file_path parameter)
    # This is tool-specific logic: if the tool expects a file_path, we resolve
    # relative paths and provide defaults. This makes the tool more robust.
    if "file_path" in args and isinstance(args["file_path"], str):
        # Resolve relative paths to absolute paths, or use current file as default
        args["file_path"] = resolve_path(args["file_path"]) if str(args["file_path"]) != "" else __file__
    elif "file_path" not in args:
        # Provide default for tools expecting file_path (use current file)
        args["file_path"] = __file__

    # Step 5: Execute the tool function with the prepared arguments
    # This is where the actual tool execution happens: we call the Python function
    # that was registered in TOOL_REGISTRY, passing the arguments unpacked from
    # the args dictionary. The function's return value becomes the tool's output.
    return func(**args)


def compute_expected_output() -> str:
    # Ground-truth expected output based on the actual file contents
    return output_every_func_return_type(__file__)


def test_your_prompt(system_prompt: str) -> bool:
    """Run once: require the model to produce a valid tool call; compare tool output to expected."""
    expected = compute_expected_output()
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES} ...")
        try:
            call = run_model_for_tool_call(system_prompt)
        except Exception as exc:
            print(f"Failed to parse tool call: {exc}")
            continue
        print(f"\nGenerated tool call before execution: \n{call}")
        try:
            # NOTE: `execute_tool_call` will update `call`'s "args" field with the actual values of the tool parameters.
            actual = execute_tool_call(call)
        except Exception as exc:
            print(f"Tool execution failed: {exc}")
            continue
        if actual.strip() == expected.strip():
            print(f"\nGenerated tool call after execution: \n{call}")
            print(f"\nGenerated output: \n{actual}")
            print("\nSUCCESS")
            return True
        else:
            print("Expected output:\n" + expected)
            print("Actual output:\n" + actual)
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
