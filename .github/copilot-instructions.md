# GitHub Copilot Instructions

Welcome, Copilot! This document provides key instructions and project context to help you generate useful suggestions for this Python project.

## 🧠 Project Overview

This is a Python project using the following tools:

- **Visual Studio Code** as the primary development environment
- **uv** as the Python package manager
- **ruff** for formatting and linting
- **Docker** and **docker-compose** for containerized development
- **pytest** for testing
- **MkDocs** for project documentation

---

## Style Guide

We use Google-style docstrings.

---

## 🖥️ Development Environment

### Editor

- Recommended IDE: **Visual Studio Code**
- Recommended extensions:
  - Python (`ms-python.python`)
  - Pylance (`ms-python.vscode-pylance`)
  - Docker (`ms-azuretools.vscode-docker`)
  - Ruff (`charliermarsh.ruff`)

---

## 📦 Package Management with `uv`

### Install dependencies

```bash
uv add -r requirements.txt
```

### Add a new package

```bash
uv add <package-name>
```

### Remove a package

```bash
uv remove <package-name>
```

---

## 🧪 Running Tests

We use `pytest` to run tests:

```bash
pytest tests/
```

- All test files are located in the `tests/` directory.

---

## 🐳 Using Docker

### Build the container

```bash
docker build -t serverless .
```

### Run the container

```bash
docker run -it --rm -v $(pwd):/app serverless
```

> Alternatively, use `docker-compose up` if `docker-compose.yml` is configured.

---

## 📚 Documentation with MkDocs

### Serve the documentation locally

```bash
mkdocs serve
```

### Build static site

```bash
mkdocs build
```

- Configuration is managed in `mkdocs.yml`

---

## 💡 Copilot Guidance

Copilot, please prioritize:

- Suggesting code that works well with `uv` for dependency management
- Following best practices for Dockerized Python apps
- Writing tests using `pytest`
- Creating and updating documentation in Markdown for MkDocs
- Generating VS Code settings and config snippets when needed

Thanks, Copilot. Let's build something great 🚀
