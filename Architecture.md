# Code\_Sling Architecture Document

## Project Overview

Code\_Sling is a Python-based tool designed to streamline the process of integrating AI-generated code suggestions and snippets into existing codebases. By leveraging AI models and programmatic code manipulation, it aims to reduce the manual effort and potential errors associated with copy-pasting and re-indenting code provided by large language models. The tool focuses on providing a simple user interface for developers and automates the core task of applying targeted code changes based on AI instructions.

## Directory Structure

The project follows a standard Python package structure for organization:

```
Code_Sling/
├── .gitignore
├── .env
├── requirements.txt
├── README.md
├── main.py
└── src/
    ├── ui/
    ├── core/
    ├── models/
    ├── ai/
    ├── config/
    └── utils/
```

## Component Descriptions

Below is a description of the purpose of each significant file and directory within the project:

### Root Directory Files

  * **`.gitignore`**: Specifies intentionally untracked files that Git should ignore. This typically includes temporary files, build artifacts, and sensitive information like the `.env` file.
  * **`.env`**: A plain text file used to store environment-specific configuration variables, such as API keys for AI models and paths to local resources. It is crucial that this file is listed in `.gitignore` to prevent committing sensitive data.
  * **`requirements.txt`**: Lists the Python package dependencies required for the project to run. These dependencies can be installed using `pip install -r requirements.txt`.
  * **`README.md`**: Provides a comprehensive overview of the Code\_Sling tool. This includes a description of its purpose, instructions for setup and installation, how to configure the `.env` file, usage examples, and potentially information about contributing or the project's vision.
  * **`main.py`**: This is the primary entry point for the application. It is responsible for initializing the application (e.g., loading settings, setting up the UI) and starting the main application loop.

### `src/` Directory (Source Code)

This directory contains all the Python modules that constitute the core logic and interface of the Code\_Sling tool.

  * **`src/ui/`**: Contains the code for the graphical user interface.
      * **`src/ui/main_window.py`**: Implements the main window and user interface elements of the application using a library like PyQT. It handles user interactions, displays input/output fields, and orchestrates calls to the core logic based on user actions.
  * **`src/core/`**: Holds the central processing logic of the tool.
      * **`src/core/injector.py`**: Contains the logic for applying the code changes to the original source code. It takes the original code (as a list of lines), the parsed instructions (including target line numbers and change types like insert/delete/replace), and programmatically modifies the code list. It is responsible for handling the mechanics of inserting, deleting, or replacing lines based on the instructions.
      * **`src/core/parser.py`**: Is responsible for parsing the raw text output received from the AI reasoning model. It interprets the structured output from the AI to extract the specific instructions for code modification, such as which snippet goes where and what type of action to perform (insert, delete). It translates the AI's line number mappings into actionable instructions for the `injector.py`.
  * **`src/models/`**: This directory is intended for defining any structured data models or classes used throughout the application, if needed beyond basic Python data structures like dictionaries or lists.
  * **`src/ai/`**: Contains modules for interacting with the AI models.
      * **`src/ai/reasoning_agent.py`**: Encapsulates the logic for communicating with the primary reasoning model (e.g., via OpenAI or Gemini API). It formats the input (numbered original code and AI suggestion) into a prompt suitable for the reasoning model and processes the model's response to obtain the line number mappings and change instructions.
      * **`src/ai/indentation_model.py`**: Contains the logic for interacting with the model responsible for fixing code indentation. This could involve making API calls to a dedicated formatting model or running inference on a locally hosted, fine-tuned model (like a fine-tuned CodeParrot). It takes code (potentially with new insertions) and returns code with corrected indentation. This module is designed to be decoupled initially but provides a clear place for this functionality.
  * **`src/config/`**: Manages the application's configuration and settings.
      * **`src/config/settings.py`**: Defines the application's configuration using a library like Pydantic. It loads settings from the `.env` file and provides access to these settings throughout the application. This includes API keys, model names, default paths, and potentially toggles for features like using Pylint for checks.
  * **`src/utils/`**: Contains general-purpose utility functions.
      * **`src/utils/code_utils.py`**: Provides helper functions specifically for working with code text. This includes functions for adding line numbers to code strings, potentially basic syntax checking (e.g., using Python's `ast` module), and other code-related text manipulation if needed.

This architecture separates concerns into logical modules, making the codebase easier to develop, test, and maintain. The core logic is separated from the UI and AI interaction, allowing for flexibility in changing UI frameworks or AI providers in the future while keeping the core functionality intact.