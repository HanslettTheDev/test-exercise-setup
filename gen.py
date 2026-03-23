#!/usr/bin/env python3
"""
Generate folder structure for remote code execution engine with Gitea actions.

Creates:
- 5 top‑level modules (e.g., Backend_Development_with_Python)
- For each module:
    - Lessons/Exercises/   : 20 lessons × 20 exercises, each with test.sh & solution.py
    - Lessons/Projects/    : 20 lesson projects, each with test.sh & project_instructions.md
    - Projects/            : 2 capstone projects, each with test.sh & project_instructions.md
- Module‑level workflows/ folder with a base Gitea action (test.yml) that sets up the language
  environment and then runs the test.sh script.
- An empty workflows/ folder inside every exercise and project folder, ready for custom workflows.
"""

import os
import sys

# ----- Configuration -----
MODULES = [
    "Backend_Development_with_Python",
    "Vue.js_Full_Stack",
    "Data_Science_with_R",
    "DevOps_with_Docker_and_Kubernetes",
    "Mobile_App_Development_with_Flutter"
]

LESSONS_COUNT = 5
EXERCISES_PER_LESSON = 5
CAPSTONE_COUNT = 2

# Map module names to the language used for the base workflow
MODULE_LANGUAGE = {
    "Backend_Development_with_Python": "python",
    "Vue.js_Full_Stack": "nodejs",
    "Data_Science_with_R": "r",
    "DevOps_with_Docker_and_Kubernetes": "docker",
    "Mobile_App_Development_with_Flutter": "flutter"
}

# ----- Helper functions -----
def create_file(path, content, executable=False):
    """Create a file with given content, ensuring parent directories exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    if executable:
        os.chmod(path, 0o755)

def create_workflows_dir(path):
    """Create an empty workflows directory (with a .gitkeep to preserve it in Git)."""
    workflows_path = os.path.join(path, "workflows")
    os.makedirs(workflows_path, exist_ok=True)
    # Place a .gitkeep so the folder is tracked even if empty
    gitkeep_path = os.path.join(workflows_path, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write("")

def create_test_script(description="Test script"):
    """Return a simple bash script that runs a Python test (adjust as needed)."""
    return f"""#!/bin/bash
# {description}

# Run the test (example: compare output of solution.py)
output=$(python3 solution.py 2>&1)
expected="Hello, World!"

if [ "$output" == "$expected" ]; then
    echo "✅ Test passed"
    exit 0
else
    echo "❌ Test failed"
    echo "Expected: $expected"
    echo "Got: $output"
    exit 1
fi
"""

def create_solution_py():
    """Return a simple Python script as a placeholder."""
    return '''#!/usr/bin/env python3
print("Hello, World!")
'''

def create_project_instructions(title):
    """Return a simple markdown instruction file."""
    return f"""# {title}

## Instructions
Complete the project according to the requirements.

## Testing
Run the test script: `./test.sh`
"""

def generate_workflow_yaml(language):
    """Return a Gitea action YAML that sets up the given language and runs the test script."""
    setup_steps = {
        "python": """
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'""",
        "nodejs": """
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16.x'""",
        "r": """
      - name: Set up R
        uses: r-lib/actions/setup-r@v2""",
        "docker": "",
        "flutter": """
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.x'"""
    }
    setup = setup_steps.get(language, "")

    # Common workflow content
    yaml = f"""name: Run Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
{setup}
      - name: Run test script
        run: |
          # Find the test.sh in the changed files (simplified – you may need a custom script)
          # For demo, we assume the test.sh is in the current directory.
          chmod +x ./test.sh
          ./test.sh
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test.log
"""
    return yaml

# ----- Main generation function -----
def main(root_dir='.'):
    root = os.path.abspath(root_dir)
    print(f"Creating structure under: {root}")

    for module in MODULES:
        module_path = os.path.join(root, module)
        print(f"  Creating module: {module}")

        # ---- Module‑level workflow ----
        lang = MODULE_LANGUAGE.get(module, "python")  # fallback to python
        workflow_dir = os.path.join(module_path, "workflows")
        workflow_file = os.path.join(workflow_dir, "test.yml")
        create_file(workflow_file, generate_workflow_yaml(lang))

        # ---- Lessons / Exercises ----
        exercises_base = os.path.join(module_path, "Lessons", "Exercises")
        for lesson in range(1, LESSONS_COUNT + 1):
            for ex in range(1, EXERCISES_PER_LESSON + 1):
                ex_name = f"lesson{lesson:02d}_exercise{ex:02d}"
                ex_dir = os.path.join(exercises_base, ex_name)
                # test.sh
                create_file(os.path.join(ex_dir, "test.sh"), create_test_script(f"Test for {ex_name}"), executable=True)
                # solution.py
                create_file(os.path.join(ex_dir, "solution.py"), create_solution_py())
                # workflows directory for custom workflows
                create_workflows_dir(ex_dir)

        # ---- Lessons / Projects (one per lesson) ----
        projects_base = os.path.join(module_path, "Lessons", "Projects")
        for lesson in range(1, LESSONS_COUNT + 1):
            proj_name = f"lesson{lesson:02d}_project"
            proj_dir = os.path.join(projects_base, proj_name)
            create_file(os.path.join(proj_dir, "test.sh"), create_test_script(f"Test for {proj_name}"), executable=True)
            create_file(os.path.join(proj_dir, "project_instructions.md"), create_project_instructions(proj_name))
            create_workflows_dir(proj_dir)

        # ---- Capstone Projects ----
        capstone_base = os.path.join(module_path, "Projects")
        for cap in range(1, CAPSTONE_COUNT + 1):
            cap_name = f"capstone_{cap:02d}"
            cap_dir = os.path.join(capstone_base, cap_name)
            create_file(os.path.join(cap_dir, "test.sh"), create_test_script(f"Test for {cap_name}"), executable=True)
            create_file(os.path.join(cap_dir, "project_instructions.md"), create_project_instructions(cap_name))
            create_workflows_dir(cap_dir)

    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()