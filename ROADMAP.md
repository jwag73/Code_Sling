ROADMAP
Version 1.0 Checklist
This checklist outlines the key tasks required to complete the initial version (v1.0) of the Code_Sling tool, incorporating all the discussed features and components except for the potential future Chrome plugin integration.

Phase 0: Project Setup & Foundation
[x] Create the GitHub repository (jwag73/Code_Sling).
[x] Clone the repository locally.
[x] Create the initial directory structure based on the defined architecture.
[x] src/
[ ] src/ui/ (To be created in User Interface Phase)
[x] src/core/
[ ] src/models/ (If needed for local ML models later)
[x] src/ai/
[x] src/config/
[x] src/utils/
[x] src/cli/ (Created for CLI phase)
[x] Create placeholder __init__.py files in all src/ subdirectories to make them packages.
[x] Create .gitignore file and add entries for .env, __pycache__, virtual environment folder, etc.
[x] Create requirements.txt file. (Note: Using pyproject.toml for dependencies)
[x] Create README.md file (will be updated later).
[x] Create main.py (main entry point script at root, e.g., for UI orchestration - basic placeholder).
[x] Create architecture.md (copy in the architecture document).
[x] Set up a Python virtual environment.
[x] Install core dependencies listed in requirements.txt (via pyproject.toml).
Phase 1: Configuration & Settings
[x] Implement the src/config/settings.py module to:
[x] Define application settings using Pydantic.
[x] Load configuration values from the .env file (e.g., API keys, default model names).
[x] Create the .env file in the project root with placeholder values for necessary settings (ensure it's in .gitignore).
Phase 2: Core Code Processing Logic
[x] Implement the line numbering logic in src/utils/code_utils.py:
[x] Function to add line numbers to input code strings.
[x] Function to add line numbers to AI output strings (including snippets).
[x] Implement the AI interaction logic for the reasoning model in src/ai/reasoning_agent.py:
[x] Function to format the prompt with numbered original code and numbered AI output.
[x] Logic to call the chosen reasoning model API (e.g., OpenAI, Gemini) using the official client library.
[x] Process the API response to extract the model's output (the line number mappings and change types).
[x] Implement the parsing logic in src/core/parser.py:
[x] Function to parse the structured output from the reasoning_agent.py.
[x] Extract specific instructions: target line number(s) in original code, source line number(s) in AI output (for snippets), and change type (insert, delete). Handle the defined symbols for deletions.
[x] Implement the code injection/modification logic in src/core/injector.py:
[x] Function to read the original code into a list of lines (injector takes string, splits).
[x] Logic to apply changes to the list of lines based on the parsed instructions:
[x] Handle insertions of snippets at specified line numbers.
[x] Handle deletions of specified line numbers.
[x] (Implicitly handle replacements as deletions followed by insertions, based on discussion).
[x] Basic logic for handling indentation during insertion (e.g., content inserted as-is, preserving its own indentation).
[x] Function to write the modified list of lines back to a string or file (injector returns string; file I/O handled by caller e.g. CLI).
Phase 3: Command-Line Interface (CLI)
[x] Design the basic CLI arguments (original_file, suggestion_file, output_file).
[x] Implement src/utils/file_operations.py for reading/writing files.
[x] Implement CLI argument parsing in src/cli/main.py.
[ ] Implement the main application flow in src/cli/main.py (integrate actual calls):
[x] Read original code from input file (using file_operations) (code written, needs final integration).
[x] Read AI's suggested code from input file (using file_operations) (code written, needs final integration).
[x] Use reasoning_agent to get transformation instructions (code written, needs final integration).
[x] Use parser to parse instructions (code written, needs final integration).
[x] Use injector to apply instructions to the original code (code written, needs final integration).
[x] Write modified code to output file (using file_operations) or print to console (code written, needs final integration).
[x] Basic error handling and user feedback in CLI.
[ ] AI Safety Note: Ensure the CLI tool does not create execution loops. The tool should only modify code; execution of modified code must be a separate, user-initiated step. Maintain a clear "air gap" between code modification and execution.
[ ] Unit/integration tests for CLI operations (basic file_op tests exist; full CLI flow tests pending).
Phase 4: User Interface (PyQT)
[x ] Design and implement the basic PyQT UI in src/ui/main_window.py:
[x ] Create the main window.
[x ] Add text input area/box for the original code.
[ x] Add text input area/box for the AI's suggestion/output.
[ x] Add a button to trigger the code processing/injection.
[ x] Add a text output area/box to display the resulting modified code.
[x ] Connect UI elements to trigger the core processing workflow.
Phase 5: Orchestration & Entry Point (UI Focus)
[x ] Implement the main application logic in root main.py:
[x ] Initialize application settings using src/config/settings.py.
[x ] Create and display the main UI window (src/ui/main_window.py).
[x ] Connect UI actions (button clicks) to call the core processing logic in src/core/.
[ ] Orchestrate the workflow: Get input from UI -> Number lines -> Call reasoning agent -> Parse output -> Call injector -> Get result -> Display result in UI.
Phase 6: Error Handling & Validation (V1 Approach)
[ ] Implement basic error handling for core processing steps (e.g., API call failures, parsing errors, invalid line numbers).
[ ] Document the planned workflow for using the AI chat "edit" feature for post-injection error checking in README.md.
[ ] (Optional/Placeholder) Add a toggle in settings for enabling Pylint or another AI check (as discussed for future options/community use).
[ ] (Optional/Placeholder) Integrate a basic local syntax check using Python's ast or compile() after injection as a first line of defense.
Phase 7: Indentation Fixing & Data Generation (Decoupled but V1 Goal)
[ ] Implement the basic indentation fixing logic in src/ai/indentation_model.py:
[ ] Function to format the input for the indentation model (numbered inputs + parsing output + system prompt/examples).
[ ] Logic to call the chosen indentation model (API or local fine-tuned) and get the corrected code.
[ ] (Integrate this into the main workflow after core injection).
[ ] Implement dataset generation logic:
[ ] Capture the inputs (original code, AI suggestion, reasoning model output) and the final corrected code (after manual fixes or indentation pass).
[ ] Save this data in a structured format (e.g., JSON lines) to a local file for future fine-tuning datasets.
[ ] Document the process for generating and using these datasets in README.md or a separate docs/ file.
Phase 8: Documentation & Community
[ ] Expand the README.md with detailed instructions for setup, configuration, usage, and the error checking workflow.
[ ] Add documentation for generating and using datasets for fine-tuning.
[ ] Clearly state the intellectual property terms for contributions and data sharing.
[ ] (Optional) Create initial files in a docs/ directory for more detailed documentation (e.g., fine_tuning_guide.md).
Phase 9: Testing (Overall)
[x] Write basic unit tests for key modules in src/core/, src/ai/, src/config/, and src/utils/.
[x] Ensure tests can be run using a standard test runner (like pytest).
[ ] (Future) Expand test coverage, including integration tests for CLI and UI workflows.
Phase 10: Polish & Release
[ ] Clean up code, add comments where necessary.
[ ] Ensure the tool is reasonably robust to common inputs.
[ ] Prepare for initial commit and push to GitHub.
[ ] Announce the release of version 1.0.