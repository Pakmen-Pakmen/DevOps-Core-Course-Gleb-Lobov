# Lab 3 — CI/CD with GitHub Actions

## Overview

In this lab, CI/CD pipeline was implemented using GitHub Actions.

The workflow includes:
- Code linting (flake8)
- Automated testing (pytest + coverage)
- Docker image build
- Docker Hub push
- Security scanning with Snyk
- Dependency caching for performance optimization

The goal was to automate quality checks, container publishing, and security validation.

## CI Status Badge

A status badge was added to README.md to provide visible proof that the CI pipeline is working.

Example badge:

![CI](https://github.com/Pakmen-Pakmen/DevOps-Core-Course-Gleb-Lobov/actions/workflows/python-ci.yml/badge.svg)

This badge updates automatically on every push or pull request.
Green status confirms that all pipeline stages passed successfully.

## Caching Implementation & Performance Improvement

To improve workflow speed, dependency caching was implemented using GitHub Actions cache.

Example configuration:

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Why caching matters

### Without caching:
-Dependencies are downloaded on every run
-Slower builds
-Increased network usage

### With caching:
-Dependencies are restored from cache
-Faster test execution
-Reduced CI time

## Measured Improvement

First run (no cache): ~2–3 minutes
Subsequent runs (cache hit): ~1–1.5 minutes

This demonstrates significant CI speed optimization.

## CI Best Practices Applied

### 1. Separate Jobs and Clear Steps
Each stage (lint, test, build, scan) is separated into clear logical steps.
This improves readability and debugging.

### 2. Fail Fast Strategy
Linting and testing run before Docker build.
If code quality fails, the image is not built or pushed.

### 3. Version Tagging Strategy
Docker images are tagged with:
- latest
- Application version extracted from SERVICE_VERSION

This ensures traceability and reproducibility.

### 4. Use of GitHub Secrets
Sensitive data such as:
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN
- SNYK_TOKEN

are stored securely in GitHub Secrets and not hardcoded in the repository.

### 5. Minimal Permissions Principle
Only required permissions are used in the workflow.
Secrets are only accessed in relevant jobs.

## Snyk Security Scanning

Snyk was integrated into the CI pipeline to scan for vulnerabilities in dependencies and Docker images.

### Integration Steps

1. Created Snyk account
2. Generated API token
3. Added SNYK_TOKEN to GitHub Secrets
4. Added Snyk scan step to workflow

Example step:

```yaml
- name: Run Snyk Scan
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### Why Snyk Matters
-Detects known vulnerabilities in dependencies
-Helps prevent insecure deployments
-Enforces security in CI pipeline

### Vulnerability Handling

If vulnerabilities are detected:
-The pipeline fails
-Developer must update dependencies
-Re-run CI after fix

This enforces secure development practices.

## Workflow Performance Output

### First Run (Cache Miss)

Cache not found for input keys: Linux-pip-...

Total workflow time: 2m 34s

### Second Run (Cache Hit)

Cache restored successfully

Total workflow time: 1m 21s

The workflow execution time decreased by approximately 50%, demonstrating effective dependency caching.
Screenshot LAB03_1

## Technical Analysis

The CI pipeline enforces quality gates before container publication.

Order of execution:
1. Lint
2. Test + Coverage
3. Docker Build
4. Security Scan
5. Push to Docker Hub

If any step fails, the workflow stops.

Caching improves speed without sacrificing reliability.
Secrets protect credentials.
Snyk ensures secure dependency management.

This structure reflects real-world DevOps CI/CD pipelines.


## Challenges & Solutions

### Issue 1 — Missing pytest
pytest was not installed in the local environment.
Solution: Install dependencies via requirements.txt and activate virtual environment.

### Issue 2 — Flake8 errors in CI
The pipeline failed due to formatting violations.
Solution: Fixed blank lines and line length issues.

### Issue 3 — Version extraction error
GitHub Actions failed to process VERSION environment variable.
Solution: Corrected version extraction command to properly write to $GITHUB_ENV.

### Issue 4 — Branch had no upstream
Git push failed because branch had no upstream.
Solution: Used:
git push --set-upstream origin lab03
