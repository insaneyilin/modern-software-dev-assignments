import os
import re
from collections import Counter
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# Self-consistency prompting flow: (in mermaid markdown)
# flowchart TD
#     A[User Prompt] --> B[Run 1]
#     A --> C[Run 2]
#     A --> D[Run 3]
#     A --> E[Run 4]
#     A --> F[Run 5]
#     B --> G[Answer 1]
#     C --> H[Answer 2]
#     D --> I[Answer 3]
#     E --> J[Answer 4]
#     F --> K[Answer 5]
#     G --> L[Collect all answers]
#     H --> L
#     I --> L
#     J --> L
#     K --> L
#     L --> M[Majority Vote]
#     M --> N[Final Answer]
#     style A fill:#e1f5ff
#     style N fill:#c8e6c9
#     style M fill:#fff9c4

# TODO: Fill this in! Try to get as close to 100% correctness across all runs as possible.
YOUR_SYSTEM_PROMPT = """
You are a precise mathematical problem solver. When solving distance problems, follow these steps carefully:

1. Identify all given information (total distance, stop locations)
2. Calculate the position of each stop point
3. Determine the distance between stops by subtracting the earlier position from the later position
4. Verify your calculation makes sense

For problems involving stops:
- If a stop is "after X miles", the stop is at position X
- If a stop is "Y miles before the end", calculate: total distance - Y

Always show your reasoning step by step, then provide the final answer in the exact format: "Answer: <number>"
"""

USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

Henry made two stops during his 60-mile bike trip. He first stopped after 20
miles. His second stop was 15 miles before the end of the trip. How many miles
did he travel between his first and second stops?
"""

EXPECTED_OUTPUT = "Answer: 25"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES, majority-vote on the extracted 'Answer: ...' lines.

    Prints "SUCCESS" if the majority answer equals EXPECTED_OUTPUT.
    """
    answers: list[str] = []
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 1},
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        print(f"Run {idx + 1} answer: {final_answer}")
        answers.append(final_answer.strip())

    if not answers:
        print("No answers produced.")
        return False

    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    print(f"Majority answer: {majority_answer} ({majority_count}/{len(answers)})")

    if majority_answer.strip() == EXPECTED_OUTPUT.strip():
        print("SUCCESS")
        return True

    # Print distribution for debugging when majority does not match expected
    print(f"Expected output: {EXPECTED_OUTPUT}")
    print("Answer distribution:")
    for answer, count in counts.most_common():
        print(f"  {answer}: {count}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


