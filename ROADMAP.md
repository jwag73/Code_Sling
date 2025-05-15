# ROADMAP

## Version 1.0 Checklist

This checklist outlines the key tasks required to complete the initial version (v1.0) of the Code_Sling tool, incorporating all the discussed features and components except for the potential future Chrome plugin integration.

### Phase 0: Project Setup & Foundation

- [x] Create the GitHub repository (`jwag73/Code_Sling`).
- [ ] Clone the repository locally.
- [ ] Create the initial directory structure based on the defined architecture.
    - [ ] `src/`
    - [ ] `src/ui/`
    - [ ] `src/core/`
    - [ ] `src/models/`
    - [ ] `src/ai/`
    - [ ] `src/config/`
    - [ ] `src/utils/`
- [ ] Create placeholder `__init__.py` files in all `src/` subdirectories to make them packages.
- [ ] Create `.gitignore` file and add entries for `.env`, `__pycache__`, virtual environment folder, etc.
- [ ] Create `requirements.txt` file.
- [ ] Create `README.md` file (will be updated later).
- [ ] Create `main.py` (main entry point script).
- [ ] Create `architecture.md` (copy in the architecture document).
- [ ] Set up a Python virtual environment.
- [ ] Install core dependencies listed in `requirements.txt`.

### Phase 1: Configuration & Settings

- [ ] Implement the `src/config/settings.py` module to:
    - [ ] Define application settings using Pydantic.
    - [ ] Load configuration values from the `.env` file (e.g., API keys, default model names).
- [ ] Create the `.env` file in the project root with placeholder values for necessary settings (ensure it's in `.gitignore`).

### Phase 2: Core Code Processing Logic

- [ ] Implement the line numbering logic in `src/utils/code_utils.py`:
    - [ ] Function to add line numbers to input code strings.
    - [ ] Function to add line numbers to AI output strings (including snippets).
- [ ] Implement the AI interaction logic for the reasoning model in `src/ai/reasoning_agent.py`:
    - [ ] Function to format the prompt with numbered original code and numbered AI output.
    - [ ] Logic to call the chosen reasoning model API (e.g., OpenAI, Gemini) using the official client library.
    - [ ] Process the API response to extract the model's output (the line number mappings and change types).
- [ ] Implement the parsing logic in `src/core/parser.py`:
    - [ ] Function to parse the structured output from the `reasoning_agent.py`.
    - [ ] Extract specific instructions: target line number(s) in original code, source line number(s) in AI output (for snippets), and change type (insert, delete). Handle the defined symbols for deletions.
- [ ] Implement the code injection/modification logic in `src/core/injector.py`:
    - [ ] Function to read the original code into a list of lines.
    - [ ] Logic to apply changes to the list of lines based on the parsed instructions:
        - [ ] Handle insertions of snippets at specified line numbers.
        - [ ] Handle deletions of specified line numbers.
        - [ ] (Implicitly handle replacements as deletions followed by insertions, based on discussion).
    - [ ] Basic logic for handling indentation during insertion (e.g., matching the indentation of the preceding line).
    - [ ] Function to write the modified list of lines back to a string or file.

### Phase 3: User Interface

- [ ] Design and implement the basic PyQT UI in `src/ui/main_window.py`:
    - [ ] Create the main window.
    - [ ] Add text input area/box for the original code.
    - [ ] Add text input area/box for the AI's suggestion/output.
    - [ ] Add a button to trigger the code processing/injection.
    - [ ] Add a text output area/box to display the resulting modified code.
    - [ ] Connect UI elements to trigger the core processing workflow.

### Phase 4: Orchestration & Entry Point

- [ ] Implement the main application logic in `main.py`:
    - [ ] Initialize application settings using `src/config/settings.py`.
    - [ ] Create and display the main UI window (`src/ui/main_window.py`).
    - [ ] Connect UI actions (button clicks) to call the core processing logic in `src/core/`.
    - [ ] Orchestrate the workflow: Get input from UI -> Number lines -> Call reasoning agent -> Parse output -> Call injector -> Get result -> Display result in UI.

### Phase 5: Error Handling & Validation (V1 Approach)

- [ ] Implement basic error handling for core processing steps (e.g., API call failures, parsing errors, invalid line numbers).
- [ ] Document the planned workflow for using the AI chat "edit" feature for post-injection error checking in `README.md`.
- [ ] (Optional/Placeholder) Add a toggle in settings for enabling Pylint or another AI check (as discussed for future options/community use).
- [ ] (Optional/Placeholder) Integrate a basic local syntax check using Python's `ast` or `compile()` after injection as a first line of defense.

### Phase 6: Indentation Fixing & Data Generation (Decoupled but V1 Goal)

- [ ] Implement the basic indentation fixing logic in `src/ai/indentation_model.py`:
    - [ ] Function to format the input for the indentation model (numbered inputs + parsing output + system prompt/examples).
    - [ ] Logic to call the chosen indentation model (API or local fine-tuned) and get the corrected code.
    - [ ] (Integrate this into the main workflow after core injection).
- [ ] Implement dataset generation logic:
    - [ ] Capture the inputs (original code, AI suggestion, reasoning model output) and the final corrected code (after manual fixes or indentation pass).
    - [ ] Save this data in a structured format (e.g., JSON lines) to a local file for future fine-tuning datasets.
- [ ] Document the process for generating and using these datasets in `README.md` or a separate `docs/` file.

### Phase 7: Documentation & Community

- [ ] Expand the `README.md` with detailed instructions for setup, configuration, usage, and the error checking workflow.
- [ ] Add documentation for generating and using datasets for fine-tuning.
- [ ] Clearly state the intellectual property terms for contributions and data sharing.
- [ ] (Optional) Create initial files in a `docs/` directory for more detailed documentation (e.g., `fine_tuning_guide.md`).

### Phase 8: Testing

- [ ] Write basic unit tests for key modules in `src/core/`, `src/ai/`, `src/config/`, and `src/utils/` (even if they start simple with `assert True`).
- [ ] Ensure tests can be run using a standard test runner (like `pytest`).

### Phase 9: Polish & Release

- [ ] Clean up code, add comments where necessary.
- [ ] Ensure the tool is reasonably robust to common inputs.
- [ ] Prepare for initial commit and push to GitHub.
- [ ] Announce the release of version 1.0.

---