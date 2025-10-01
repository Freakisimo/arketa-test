# ETL Pipeline Project for Data Cleaning

This project implements an ETL (Extract, Transform, Load) pipeline in Python to consume data from a REST API, apply a series of cleaning and validation rules, and finally save the results in JSON and CSV files.

## Features

- **Data Extraction**: Consumes data from two API endpoints (`/users` and `/todos`).
- **Transformation and Cleaning**:
  - Parses and structures input data to a defined schema.
  - Validates and standardizes phone numbers to E.164 format.
  - Validates email format.
  - Performs deduplication of users based on email, phone, or name, keeping the record with the lowest ID.
- **Cross-Validation**: Validates that tasks (`todos`) belong to valid and existing users.
- **Data Loading**: Saves the processed data (accepted and rejected) into `.json` and `.csv` files in the `data/` directory.
- **Testing**: Includes a suite of unit tests to validate the processing logic.

## Project Structure

```
.
├── data/                 # Output directory for generated files
├── src/                  # Source code of the pipeline
│   ├── __init__.py
│   ├── api_client.py     # Client to make requests to the API
│   ├── file_writer.py    # Utility to write JSON and CSV files
│   └── main.py           # Main ETL logic and orchestration
├── tests/                # Unit test suite
│   ├── __init__.py
│   └── test_processors.py
├── main.py               # Entry point to run the pipeline
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Setup and Installation

To run this project, you need to have Python 3 installed. It is strongly recommended to use a virtual environment.

1. **Clone the repository (if applicable)**:
   ```bash
   git clone <repository-url>
   cd <directory-name>
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## How to Use

### Run the ETL Pipeline

To run the complete process of extraction, transformation, and loading, simply run the `main.py` script from the root of the project:

```bash
python3 main.py
```

The output files will be generated in the `data/` directory.

### Run the Tests

To verify that all business logic works as expected, you can run the unit test suite:

```bash
python3 -m unittest discover -s tests -t .
```

## Code Summary

- **`src/main.py`**: This is the heart of the project. It contains:
  - The `UserProcessor` and `TodoProcessor` classes, where all the transformation, validation, and deduplication logic resides.
  - The `run_processing_pipeline` function, which orchestrates the execution of the processors and their dependencies.
  - The `save_pipeline_results` function, which is in charge of the Load phase and saves the files.
- **`src/api_client.py`**: Abstracts the communication with the REST API.
- **`src/file_writer.py`**: Handles the writing of processed data in different file formats.
- **`tests/test_processors.py`**: Contains unit tests that simulate the API and validate the behavior of the processors in different scenarios (valid, duplicate, invalid data, etc.).