# Setup and Run Guide

This document explains how to set up and run the three AI agents in this repository on your local machine.

## Repository Structure

```
AI-Agents-Task/
    Assignment 1 - Content Writing Agent/
    Assignment 2 - Copywriting and Ads Agent/
    Assignment 3 - Video Production Agent/
    deliverables/
```

Each agent folder is self-contained. It has its own dependencies, its own environment file, and can be run independently of the other two.

## Prerequisites

- Python 3.10 or later
- pip (comes with Python)
- A Gemini API key from https://aistudio.google.com/app/apikey
- Internet access (required for the Gemini API calls; the agents cannot generate content offline)

To check your Python and pip installation:

```
python --version
pip --version
```

On some systems, particularly Linux and macOS, you may need to use `python3` and `pip3` instead of `python` and `pip`.

## Step 1: Clone or Download the Repository

```
git clone https://github.com/chron303/AI-Agents-Task.git
cd AI-Agents-Task
```

If you received this project as a ZIP file instead, extract it and open a terminal in the extracted folder.

## Step 2: Set Up Each Agent

Each agent needs its own dependency installation and its own environment file. Repeat the steps below for each of the three agent folders.

### 2.1 Install Dependencies

Navigate into the agent folder and install its requirements:

```
cd "Assignment 1 - Content Writing Agent"
pip install -r requirements.txt
```

If `pip` is not recognized, or you have multiple Python versions installed, use:

```
python -m pip install -r requirements.txt
```

### 2.2 Configure the Environment File

Each agent folder contains a `.env.example` file. Copy it to `.env` and add your Gemini API key.

On Windows (PowerShell):

```
copy .env.example .env
```

On macOS or Linux:

```
cp .env.example .env
```

Then open `.env` in a text editor and set your API key:

```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit your `.env` file to version control. It is already excluded through `.gitignore`.

Repeat the two steps above inside `Assignment 2 - Copywriting and Ads Agent` and `Assignment 3 - Video Production Agent`. Each agent requires its own `.env` file; they are not shared.

## Step 3: Run an Agent

Each agent can be run in two ways: through its Streamlit web interface or through its command-line interface. The commands below assume you are inside the relevant agent's folder.

### Agent 1: Content Writing Agent

```
cd "Assignment 1 - Content Writing Agent"
python -m streamlit run app.py
python content_writing_agent.py
python test_connection.py
python generate_samples.py
```

### Agent 2: Copywriting and Ads Agent

```
cd "Assignment 2 - Copywriting and Ads Agent"
python -m streamlit run app.py
python copywriting_ads_agent.py
python generate_samples.py
```

### Agent 3: Video Production Agent

```
cd "Assignment 3 - Video Production Agent"
python -m streamlit run app.py
python video_production_agent.py
python test_connection.py
python generate_samples.py
python tests/test_workflows.py
```

Command reference:

- `python -m streamlit run app.py` starts the web interface. A browser tab should open automatically; if not, open the local URL printed in the terminal, typically `http://localhost:8501`.
- The agent's own Python file (for example `content_writing_agent.py`) starts the interactive command-line interface.
- `test_connection.py` performs a simple call to the Gemini API to confirm your API key and model configuration are working.
- `generate_samples.py` regenerates the sample outputs stored under `deliverables/samples/`.
- `tests/test_workflows.py` (Agent 3 only) runs the automated unit test suite. This does not require an API key or internet access, since it uses a simulated language model for testing.

## Running Streamlit: Important Note for Windows Users

If you run `streamlit run app.py` directly and see an error similar to:

```
streamlit : The term 'streamlit' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

this means the `streamlit` command is not available on your system PATH, even though the package may be installed correctly. Use the module form instead, which works regardless of PATH configuration:

```
python -m streamlit run app.py
```

This is the recommended way to launch Streamlit throughout this project on Windows.

If you still see an error such as `No module named streamlit`, it usually means `pip` and `python` are pointing to different Python installations. Confirm the package is installed under the same interpreter you are using to run it:

```
python -m pip show streamlit
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Using a Virtual Environment (Recommended)

Using a virtual environment keeps each agent's dependencies isolated from your system Python installation and from each other.

On Windows (PowerShell):

```
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS or Linux:

```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To leave the virtual environment when finished:

```
deactivate
```

## Common Issues

**"GEMINI_API_KEY is not set" error at startup**
The agent could not find a `.env` file, or the file does not contain a valid key. Confirm that `.env` exists in the same folder as `app.py` and contains a real API key, not the placeholder text.

**Gemini API call fails with a network or connection error**
Confirm you have internet access and that your API key is valid and has not exceeded its usage quota. Run `python test_connection.py` to isolate the problem.

**Streamlit opens but shows a configuration error**
This usually means the `.env` file is missing or incomplete. Review Step 2.2 above.

**Different behavior between agents**
Each agent folder has its own `.env`, its own dependencies, and its own virtual environment if you choose to use one. Settings in one agent's folder do not affect another.

## Optional: Storyboard Reference Images (Agent 3 Only)

Agent 3's Storyboard workflow can optionally generate a single AI reference image using Imagen. This is off by default and controlled by a checkbox in the Streamlit interface, or a prompt in the command-line interface. It requires no additional setup beyond the same `GEMINI_API_KEY` already configured; an optional `GEMINI_IMAGE_MODEL` variable in `.env` can override the default image model if needed. If image generation is unavailable for any reason, the text-based storyboard remains fully functional.

## Summary of Commands

| Task | Command |
|---|---|
| Install dependencies | `python -m pip install -r requirements.txt` |
| Copy environment file | `cp .env.example .env` (or `copy` on Windows) |
| Run web interface | `python -m streamlit run app.py` |
| Run command-line interface | `python <agent_file>.py` |
| Test API connection | `python test_connection.py` |
| Regenerate samples | `python generate_samples.py` |
| Run unit tests (Agent 3 only) | `python tests/test_workflows.py` |
