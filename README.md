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
## Useful commands

Run a specific tests with verbose printing, headed and tracing
```bash
uv run pytest -vs --headed --tracing=on -k {test}
```

Review a trace:
```bash
uv run playwright show-trace {trace}
```