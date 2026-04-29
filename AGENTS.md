# Repository Guidelines

## Project Structure & Module Organization

This repository is a LangChain workspace with tutorials, notebooks, and sample projects.

- `docs/` contains written guides and tutorial material.
- `docs/01-python-basics/` covers Python standard-library basics.
- `docs/02-fastapi/` contains FastAPI tutorial notes.
- `docs/03-fastapi-langchain-sample/` is a runnable LangChain/FastAPI package, using `src/fastapi_langchain_sample/` for application code and `tests/` for pytest tests.
- Additional `docs/*-sample/` projects should keep their own dependencies, `src/`, tests, and README.
- `Ch01-LangChainBasic/` and `Ch02-RAG/` contain notebook-based LangChain/RAG examples and local data artifacts.

Avoid committing caches and local vector-store outputs unless intentionally part of a tutorial.

## Build, Test, and Development Commands

Run sample-specific commands from that sample directory, for example `docs/03-fastapi-langchain-sample/`.

```bash
pip install -e ".[dev]"
```

Installs the sample app and development tools.

```bash
pytest -v
```

Runs API tests with mocked LangChain/OpenAI calls.

```bash
mypy src/fastapi_langchain_sample tests
```

Runs strict type checks from `pyproject.toml`.

```bash
uvicorn fastapi_langchain_sample.main:app --reload --port 8000
```

Starts the API server. Create `.env` from the sample's `.env.example` and set `OPENAI_API_KEY` for real model calls.

## Coding Style & Naming Conventions

Use Python 3.13 for the FastAPI sample. Follow the existing style: 4-space indentation, explicit type annotations, Pydantic request/response models, and `snake_case` for modules, functions, variables, and fixtures. Keep package code under each sample's `src/` tree; do not add importable modules at a sample root.

Tutorial Markdown should use clear headings, short runnable examples, and paths relative to the repository root.

## Testing Guidelines

Tests use `pytest` and FastAPI `TestClient`. Name test files `test_*.py`, test classes `Test*`, and test functions `test_*`. Mock external API calls as in `tests/conftest.py`; tests should not require a real OpenAI key or network access. Add endpoint tests for status codes, response shape, validation errors, and failure paths.

## Commit & Pull Request Guidelines

This checkout has no Git history, so no project-specific convention can be inferred. Use concise imperative commits, optionally scoped, such as `docs: add FastAPI tutorial notes` or `test: cover chat validation`.

Pull requests should include a summary, affected paths, test results (`pytest -v`, `mypy ...` where relevant), and screenshots only for rendered docs or UI changes. Link issues when available and call out required environment variables or data files.

## Security & Configuration Tips

Do not commit `.env`, credential files, or real API keys. Keep examples in `.env.example` only. For notebooks and RAG artifacts, remove sensitive prompts, documents, and generated outputs before sharing changes.
