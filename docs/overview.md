# Overview

## What is changes-roller?

changes-roller is a command-line tool for creating and managing coordinated patch series across multiple Git repositories simultaneously. It automates the workflow of applying consistent changes to many projects and optionally submitting them for code review.

```{include} ../README.md
:start-after: "## Why changes-roller?"
:end-before: "## Project Status"
```

```{include} ../README.md
:start-after: "## How It Works"
:end-before: "## Features"
```

## Problem Statement

Software organizations often need to apply the same changes across multiple related projects—such as security updates, dependency upgrades, API migrations, or compliance fixes. Doing this manually for dozens of repositories is:

- **Time-consuming**: Cloning, patching, committing, and submitting each project individually
- **Error-prone**: Risk of inconsistent changes or missing repositories
- **Tedious**: Repetitive tasks that could be automated
- **Hard to track**: Difficult to maintain overview of progress across all projects

## Goals and Objectives

### Primary Goals

1. Enable bulk patching of multiple Git repositories from a single command
2. Automate repetitive Git operations (clone, commit, stage)
3. Ensure consistency of changes and commit messages across all projects
4. Integrate with existing workflows (testing, code review)
5. Provide clear feedback on success/failure for each repository

### Non-Goals

- Not a version control system replacement
- Not a patch management system for tracking patch state over time
- Not a code review platform (integrates with existing ones)
