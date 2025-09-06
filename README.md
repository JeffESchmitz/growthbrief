# GrowthBrief: Experimental Portfolio & AI Analysis Toolkit

## Project Overview
GrowthBrief is an experimental Python-based toolkit designed for portfolio analysis and AI-driven insights. It aims to provide a robust framework for financial data processing, signal generation, and analytical reporting.

## Quick Start (M1.1)

### Prerequisites
Ensure you have Python 3.11 (or compatible) installed. It's recommended to use a virtual environment.

### Installation
To set up the project and install its dependencies, run:
```bash
make install
```

### Running Signals
After installation, you can run the initial signal generation script:
```bash
python scripts/run_signals.py
```
*(Note: This script currently processes a predefined set of tickers and generates basic signals. Future updates will include caching mechanisms and more advanced signal processing.)*

## Project Structure
- `src/`: Core application source code.
- `prompts/`: Persona and LLM instruction files.
- `schema/`: Data definition schemas.
- `tests/`: Unit and integration tests.
- `scripts/`: Utility scripts for various tasks.
- `data/`: Placeholder for raw and processed data.
- `reports/`: Generated analytical reports.

## Development
This project is under active development. Contributions and feedback are welcome. Please refer to `GEMINI.md` for detailed development guidelines and persona-specific instructions.