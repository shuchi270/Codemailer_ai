# CodeMailer AI

CodeMailer AI is a Python project that combines Gmail access, AI-based code analysis, and HTML report generation. The current codebase can authenticate with Gmail, read unread messages, analyze a code file with an AI model through OpenRouter, and render the analysis into a simple report page.

## Project Overview

The idea behind this project is to build an assistant that can:

- connect to Gmail
- read incoming emails
- extract code content
- analyze that code with AI
- generate a readable report for the user

Right now, the project has the building blocks for that workflow, but the full end-to-end email-to-report automation is not finished yet.

## Current Completion Status

The project is roughly **60-70% complete**.

What is already implemented:

- Gmail OAuth authentication in `gmail_auth.py`
- unread email listing and message fetch helpers in `gmail_reader.py`
- AI code analysis using OpenRouter in `ai_analyzer.py`
- basic HTML report generation with Jinja2 in `report_generator.py`
- a runnable entry point in `main.py`

What is still incomplete or basic:

- `main.py` currently analyzes a local test file instead of processing Gmail message content
- email parsing and code extraction are not yet connected to the main workflow
- the generated HTML report is functional but very simple
- there are no formal automated tests yet
- configuration and secret handling still need cleanup before public sharing

## Current Workflow

At the moment, the app works more like a prototype than a finished product:

1. Load environment variables from `.env`
2. Read a local Python file
3. Send the code to OpenRouter for analysis
4. Save the AI response into `report.html`

The Gmail modules are present, but they are not fully wired into this flow yet.

## Project Structure

- `main.py` - runs the current local-file analysis flow
- `gmail_auth.py` - handles Gmail OAuth login
- `gmail_reader.py` - fetches unread emails and email content
- `ai_analyzer.py` - sends code to the AI model and returns the analysis
- `report_generator.py` - renders the HTML report
- `templates/report.html` - Jinja2 template for the report
- `test.py` - sample code file used for analysis

## Next Steps

To complete the project, the next useful steps are:

- connect Gmail message content to the analyzer
- extract code snippets from email bodies or attachments
- improve report formatting and readability
- add error handling and logging
- add automated tests
- clean up secrets and ignored files before publishing

## Summary

CodeMailer AI already demonstrates the core idea and has the major modules in place. The project is best described as a **working prototype** with the analysis engine and report generation completed, while the full Gmail-to-analysis automation is still under development.
