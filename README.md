# Jama Connect Test Validation Automation

## Project Overview

This automation framework validates Salesforce Part Request test executions in Jama Connect by:
- ✅ Comparing Actions vs Expected vs Actual Results
- ✅ Extracting and validating data from objective evidence screenshots
- ✅ Verifying timestamp sequences are chronologically correct
- ✅ Checking Work Order numbers, URLs, Tester IDs match across test data and screenshots

**Goal**: Automate validation of 5+ test scripts per month, reducing manual verification effort.

---

## Key Features

### 1. **Action-Result Validation**
Automatically verifies that:
- Action performed matches Expected Result
- Action performed matches Actual Result
- Key terms and context align across all three fields

### 2. **Screenshot Data Extraction**
Uses OCR/AI Vision to extract from objective evidence:
- Salesforce URL
- Tester ID/Username
- Date and Timestamp
- Work Order Numbers (WO#)
- Other relevant identifiers

### 3. **Sequence Validation** ⚠️ **CRITICAL**
Ensures test steps are executed in chronological order:
- Flags if Step 3 (6:20 PM) was executed BEFORE Step 4 (6:10 PM)
- Prevents out-of-sequence test execution issues

### 4. **Screenshot Completeness**
Validates screenshots contain:
- Full screen capture (top-left to bottom-right)
- Date and timestamp visible
- All required data fields

---

## Installation

### Prerequisites
```bash
# Python 3.8+
python --version

# Install required packages
pip install pytesseract pillow anthropic openai pandas

# Install Tesseract OCR
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### Optional (for AI Vision)
```bash
# For Claude API integration
pip install anthropic

# For OpenAI GPT-4 Vision
pip install openai
```

---

## Project Structure

```
jama-automation/
│
├── jama_test_validator.py      # Core validation engine
├── screenshot_analyzer.py       # OCR & AI vision for screenshots
├── run_validation_example.py    # End-to-end workflow demo
│
├── screenshots/                 # Store objective evidence here
│   ├── login_screenshot.png
│   ├── work_order_screenshot.png
│   └── part_request_screenshot.png
│
├── validation_report.json       # Generated validation report
└── README.md                    # This file
```

---

## Usage

### Quick Start Example

```python
from jama_test_validator import JamaTestValidator, TestStep
from datetime import datetime

# Initialize validator
validator = JamaTestValidator()

# Add a test step
step = TestStep(
    step_number="1.1",
    action="User must have access to Salesforce application",
    expected_result="User shall have access to Salesforce application",
    actual_result="User had access to Salesforce. URL: ga-healthcare.test.sandbox",
    objective_evidence_required=True,
    screenshot_paths=["screenshots/login.png"],
    extracted_data={
        'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
        'tester_id': 'Manish',
        'timestamp': datetime(2026, 2, 3, 18, 16),
        'date': '2026-02-03'
    }
)

validator.add_test_step(step)

# Run validation and generate report
report = validator.generate_report("validation_report.json")
print(f"Validation complete: {report['passed']} passed, {report['failed']} failed")
```

### Run Complete Demo

```bash
python run_validation_example.py
```

This will:
1. Create sample test steps
2. Run all validations
3. Generate `validation_report.json`
4. Display results in console

---

## Validation Report Format

```json
{
  "total_steps": 4,
  "passed": 2,
  "failed": 2,
  "warnings": 1,
  "sequence_violations": [
    "⚠ SEQUENCE VIOLATION: Step 3.1 (18:10) executed AFTER Step 2.1 (18:20)"
  ],
  "step_details": [
    {
      "step_number": "1.1",
      "action": "User must have access to Salesforce application",
      "status": "PASS",
      "notes": [
        "✓ Action matches Expected and Actual results",
        "✓ Salesforce URL verified: ga-healthcare.test.sandbox",
        "✓ Tester ID verified: Manish",
        "✓ Timestamp found: 2026-02-03 18:16:00"
      ]
    }
  ]
}
```

---

## What Gets Validated

### ✅ PASS Criteria
- Action keywords match Expected and Actual results
- Screenshot data matches Actual result claims
- Salesforce URL correct
- Tester ID correct
- Work Order number correct
- Timestamps in chronological order

### ❌ FAIL Criteria
- Action ≠ Expected/Actual
- Screenshot URL ≠ Actual result URL
- Tester ID mismatch
- WO# mismatch
- Missing timestamp (when required)
- Out-of-sequence execution

---

## Screenshot Analysis Methods

### Method 1: Tesseract OCR (Default)
```python
from screenshot_analyzer import ScreenshotAnalyzer

analyzer = ScreenshotAnalyzer(method="tesseract")
extracted_data = analyzer.analyze_screenshot("screenshot.png")
```

**Pros**: Free, runs offline, fast  
**Cons**: May struggle with complex layouts or poor image quality

### Method 2: AI Vision (Claude/GPT-4)
```python
analyzer = ScreenshotAnalyzer(method="ai_vision")
extracted_data = analyzer.analyze_screenshot("screenshot.png")
```

**Pros**: Better accuracy, understands context  
**Cons**: Requires API key, costs per image

---

## Roadmap & Next Steps

### Phase 1 (Current)
- [x] Core validation logic
- [x] Screenshot OCR extraction
- [x] Timestamp sequence checking
- [x] JSON report generation

### Phase 2 (Month 1)
- [ ] Jama Connect API integration
- [ ] Auto-download screenshots from Jama
- [ ] Claude/GPT-4 Vision integration
- [ ] HTML report generation

### Phase 3 (Month 2)
- [ ] Web dashboard for results
- [ ] Email notifications to testers
- [ ] Batch processing multiple test cases
- [ ] Historical trend analysis

### Phase 4 (Month 3+)
- [ ] Auto-creation of Jama defects for failures
- [ ] Integration with CI/CD pipeline
- [ ] Machine learning for pattern detection

---

## Key Points from Rohan's Requirements

1. **NOT creating defects** - Only reporting mismatches
2. **Process stays same** - Validation logic consistent across test scripts
3. **Target**: 5 scripts automated in 1 month
4. **Initial period**: 1 month monitoring/evaluation
5. **Leverage AI** - Use AI vision for complex screenshot analysis
6. **Sequential order critical** - Must catch out-of-order execution

---

## Troubleshooting

### Tesseract not found
```bash
# Windows: Add Tesseract to PATH
# Default: C:\Program Files\Tesseract-OCR

# Mac/Linux: 
which tesseract  # Should show installation path
```

### Low OCR accuracy
- Ensure screenshots are high resolution
- Check screenshots are complete (all corners visible)
- Consider using AI Vision method for better accuracy

### Timestamp parsing errors
- Check date/time format in screenshots
- Update regex patterns in `screenshot_analyzer.py` if needed

---

## Contributing

This is a work-in-progress automation framework. Suggestions for improvement:
- Better OCR accuracy
- Additional validation rules
- Enhanced reporting formats
- Integration with other tools

---

## Contact

**Project Owner**: Harshavardhan  
**Project Manager**: Rohan  
**Company**: Wipro (Client project)

---

## License

Internal use only - Wipro confidential

---

## Appendix: Example Validation Scenarios

### Scenario 1: Perfect Match ✅
```
Action: "User logs into Salesforce"
Expected: "User shall log into Salesforce"
Actual: "User logged into Salesforce at ga-healthcare.test.sandbox"
Screenshot: Shows ga-healthcare.test.sandbox, User: Manish, 6:16 PM
Result: PASS
```

### Scenario 2: URL Mismatch ❌
```
Action: "System displays Work Order"
Expected: "WO-738387 displayed"
Actual: "WO-738387 displayed"
Screenshot: Shows WO-123456 (WRONG!)
Result: FAIL - WO# mismatch
```

### Scenario 3: Sequence Violation ⚠️
```
Step 1: Executed at 6:20 PM
Step 2: Executed at 6:10 PM (BEFORE Step 1!)
Result: WARNING - Out of sequence
```

---

**Last Updated**: February 10, 2026  
**Version**: 1.0.0
#   a u t o m a t i o n  
 