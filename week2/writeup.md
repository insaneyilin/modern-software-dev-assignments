# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```text
First, analyze how `extract_action_items` works.

Then, I need to implement a LLM-powered function `extract_action_items_llm`, which should use Ollama to perform action item extraction via a large language model.

NOTE: Ollama supports structured outputs making it possible to constrain a model’s output to a specific format defined by a JSON schema. Below is an example:


    from ollama import chat
    from pydantic import BaseModel

    class Pet(BaseModel):
    name: str
    animal: str
    age: int
    color: str | None
    favorite_toy: str | None

    class PetList(BaseModel):
    pets: list[Pet]

    response = chat(
    messages=[
        {
        'role': 'user',
        'content': '''
            I have two pets.
            A cat named Luna who is 5 years old and loves playing with yarn. She has grey fur.
            I also have a 2 year old black cat named Loki who loves tennis balls.
        ''',
        }
    ],
    model='llama3.1',
    format=PetList.model_json_schema(),
    )

    pets = PetList.model_validate_json(response.message.content)
    print(pets)


Tips:
- Use Pydantic (Python) to define the schema for the response
- Add “return as JSON” to the prompt to help the model understand the request
- Set the temperature to 0 for more deterministic output

``` 

Generated Code Snippets:
```python
from pydantic import BaseModel

class ActionItemsResponse(BaseModel):
    action_items: list[str]

def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using LLM via Ollama.
    
    Args:
        text: Input text to extract action items from
        
    Returns:
        List of extracted action items as strings
    """
    if not text.strip():
        return []
    
    prompt = f"""Extract all action items, tasks, todos, and actionable items from the following text.
Return them as a JSON array of strings. Each action item should be a clear, concise task statement.

Text:
{text}

Return as JSON with a list of action items."""
    
    try:
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                }
            ],
            model='llama3.1',
            format=ActionItemsResponse.model_json_schema(),
            options={
                'temperature': 0,
            }
        )
        
        result = ActionItemsResponse.model_validate_json(response.message.content)
        return result.action_items
    except Exception as e:
        # Fallback to rule-based extraction if LLM fails
        # You might want to log the error here
        return extract_action_items(text)
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.
```

Generated Code Snippets:
```python
# Tests for extract_action_items_llm

def test_extract_action_items_llm_bullet_lists():
    """Test LLM extraction with bullet point lists"""
    text = """
    Meeting notes:
    - Set up database connection
    * Implement authentication
    • Add error handling
    Some regular text here.
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) == 3
    assert "Set up database connection" in items
    assert "Implement authentication" in items
    assert "Add error handling" in items

```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling. 

The backend codes are in the 'app/' directory.
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```

#### Summary by File

| File | Status | Lines Changed/Added | Purpose/Changed |
|------|--------|---------------------|-----------------|
| `app/main.py` | Modified | Lines 1-77 (complete rewrite) | • Added app lifecycle management with `lifespan()` context manager<br>• Added centralized exception handlers (NotFoundError, DatabaseError, RequestValidationError)<br>• Moved initialization from module-level to startup<br>• Integrated configuration settings<br>• Enhanced index route with error handling |
| `app/db.py` | Modified | Lines 1-222 (complete rewrite) | • Converted to context manager pattern for connection management with proper rollback/cleanup<br>• Added custom exceptions (DatabaseError, NotFoundError)<br>• Changed return types from raw `sqlite3.Row` to Pydantic models (NoteResponse, ActionItemResponse)<br>• Added comprehensive error handling with try/except blocks<br>• Added database indexes for performance<br>• Added ON DELETE CASCADE for foreign keys<br>• Added datetime conversion for timestamps |
| `app/routers/notes.py` | Modified | Lines 1-34 (significant refactor) | • Replaced `Dict[str, Any]` with Pydantic schemas (NoteCreate, NoteResponse)<br>• Added proper response models and HTTP status codes<br>• Added new `list_all_notes()` endpoint<br>• Replaced manual validation with schema validation<br>• Improved error handling with NotFoundError |
| `app/routers/action_items.py` | Modified | Lines 1-47 (significant refactor) | • Replaced `Dict[str, Any]` with Pydantic schemas (ExtractRequest, ExtractResponse, ActionItemUpdate, ActionItemResponse)<br>• Added proper response models and HTTP status codes<br>• Changed query parameters to use FastAPI `Query`<br>• Replaced manual validation with schema validation<br>• Improved return types to use full Pydantic models |
| `app/schemas.py` | **NEW** | Lines 1-51 (entire file) | • Created comprehensive Pydantic schemas for all API contracts<br>• Includes: NoteBase, NoteCreate, NoteResponse, ActionItemBase, ActionItemResponse, ExtractRequest, ExtractResponse, ActionItemUpdate<br>• Provides type safety, validation, and automatic API documentation |
| `app/config.py` | **NEW** | Lines 1-24 (entire file) | • Centralized application configuration<br>• Manages paths (BASE_DIR, DATA_DIR, DB_PATH, FRONTEND_DIR)<br>• Defines API settings (title, version)<br>• Provides directory management utility<br>• Eliminates hardcoded paths and provides single source of truth for configuration |


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 