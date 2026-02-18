# Overview

## What is changes-roller?

changes-roller is a command-line tool for creating and managing coordinated patch series across multiple Git repositories simultaneously. It automates the workflow of applying consistent changes to many projects and optionally submitting them for code review.

## Why changes-roller?

It's Tuesday morning, and you've just discovered a critical security vulnerability affecting 47 of your repositories. You know what comes next: hours of manual cloning, editing, committing, and reviewing. Your afternoon vanishes into mechanical `git clone`, `git commit`, `git review` while your actual development work waits.

changes-roller transforms this soul-crushing routine into a five-minute automation. Write your patch script once, then watch as it executes across all repositories in parallel. What used to consume your entire afternoon now runs while you grab coffee—with consistent changes, uniform commit messages, and organized code reviews.

## Perfect For

- Security updates across multiple microservices
- Dependency upgrades throughout your service ecosystem
- API migrations affecting client libraries
- License header updates for compliance
- Configuration file standardization
- Any scenario requiring identical changes across multiple repositories

## How It Works

Configure once, execute everywhere. You provide the repositories to update and a script containing your changes. changes-roller handles everything else—cloning, patching, testing, committing, and submitting for review.

Parallel execution means 50 repositories finish almost as quickly as one. Built-in error handling ensures you get clear feedback about any issues, while successful repositories continue processing.

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
