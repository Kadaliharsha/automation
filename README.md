# Jama Connect Test Validation Automation

An enterprise-grade automation framework designed to validate Jama Connect test execution results against objective evidence and expected outcomes. This solution focuses on reducing manual verification effort, ensuring data integrity, and maintaining regulatory compliance.

## Overview

The framework processes Excel exports from Jama Cloud to perform automated cross-verification between test instructions (Actions), expected results, and actual recorded outcomes. It provides a detailed audit trail by mapping specific terminology and verifying UI context across the test execution lifecycle.

## Core Features

### 1. Multi-Dimensional Traceability
The engine maintains strict traceability by tracking and verifying unique identifiers across all steps:
*   Test Run ID (Execution Instance)
*   Test Case ID (Design Blueprint)
*   Requirement ID (Originating Business Logic)

### 2. Word-to-Word Mapping
Moves beyond simple pass/fail status by performing keyword extraction and mapping:
*   Identifies core nouns and verbs within the 'Action' column.
*   Verifies the presence of these terms in both 'Expected' and 'Actual' result columns.
*   Generates an audit trail of mapped keywords for compliance review.

### 3. UI Context Verification (Tab Sequence Tracking)
Ensures tests were performed in the correct system area:
*   Extracts UI context (e.g., "Details Tab", "Related List") from instructions.
*   Verifies focused UI state against user-provided evidence.
*   Detects navigation anomalies and out-of-sequence screenshots.

### 4. Data Integrity Auditing
Automated checks for recurring data points:
*   **Timestamp Sequencing**: Validates chronological execution order across steps.
*   **Variable Verification**: Cross-references identifiers like Work Order numbers, Tester IDs, and Environment URLs between textual results and evidence data.

## Project Structure

*   `validation_engine.py`: Core logic for text normalization, keyword extraction, and score calculation.
*   `evidence_extractor.py`: Module for data extraction from objective evidence (supports simulated data and OCR integration).
*   `run_automation.py`: Main execution entry point; handles data ingestion, orchestration, and report generation.
*   `setup_mock_data.py`: Utility for generating standardized Jama-format test data for validation purposes.

## Installation

The solution requires Python 3.8+ and the following dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1.  **Prepare Input**: Ensure test execution data is formatted in an Excel sheet (`.xlsx`) matching the Jama Cloud export structure.
2.  **Execute Validation**: Run the automation suite.
    ```bash
    python run_automation.py
    ```
3.  **Review Results**: The system generates a formatted `validated_*.xlsx` report and a detailed `excel_validation_report.json` for technical analysis.

## Roadmap

*   **REST API Integration**: Direct connection to Jama Connect for automated data ingestion and result upload.
*   **AI Vision Integration**: Connection to OCR/Vision models (Azure Form Recognizer, AWS Textract, or OpenAI Vision) for automated evidence reading.
*   **Identity Verification**: Automated cross-match between Active Directory and Tester IDs in evidence metadata.
