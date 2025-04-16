# Inspection & Mapping Automated Testing

## Overview
An automated test suite for running various regression suites, implemented using [Pytest](https://docs.pytest.org/) and [Playwright](https://playwright.dev/).

## Features
- Regression + Integration test suites
- Automated flake finding using [pytest-flake-finder](https://github.com/dropbox/pytest-flakefinder)
- Test Rails integration planned

## Prerequisites

- UV


## Installation

1. Clone the repository:
```bash
git clone https://github.com/davis-schenkenberger-skydio/im-automated-testing.git
cd im-automated-testing
```

2. Install dependencies:
```bash
uv sync
```

## Usage

Run the test suite with the following command:
```bash
uv run pytest
```

### Flags
- `-v`: Enable verbose printing.
- `-s`: Print stdout from tests.
- `--headed`: Display the web browser UI during tests.
- `--video on`: Record a video of each test and save it to `test-results`.
- `--trace on`: Record a trace of each test and save it to `test-results`.
- `-k {test}`: Run tests matching the specified name pattern.
- `--report-to-testrail`: Report results to a TestRail run defined by the `TESTRAIL_RUN_ID` environment variable.

## Useful commands

Review a trace:
```bash
uv run playwright show-trace {trace}
```