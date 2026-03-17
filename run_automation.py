
"""
Excel-based Jama Test Validator
Reads test cases from Excel and runs validation
"""

import pandas as pd
from validation_engine import JamaTestValidator, TestStep, EvidenceData
from evidence_extractor import analyze_screenshots_for_test_step
from datetime import datetime
import json
import os

def run_excel_validation(excel_file: str):
    print(f"Reading test cases from: {excel_file}")
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Initialize Validator
    validator = JamaTestValidator()
    
    # Mock data extraction for this example (since we don't have real evidence yet)
    mock_evidence_data = {
        'evidence/scenario_login.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'timestamp': datetime(2026, 2, 23, 9, 5), # 09:05 AM
            'date': '2026-02-23'
        },
        'evidence/scenario_work_order.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'timestamp': datetime(2026, 2, 23, 9, 12), # 09:12 AM
            'work_order_number': 'WO-998877',
            'date': '2026-02-23'
        },
        'evidence/scenario_priority.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'timestamp': datetime(2026, 2, 23, 9, 13), # 09:13 AM
            'work_order_number': 'WO-998877',
            'date': '2026-02-23'
        },
        'evidence/scenario_part_request_created.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'timestamp': datetime(2026, 2, 23, 9, 17), # 09:17 AM
            'date': '2026-02-23'
        },
        'evidence/scenario_pr_status.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'timestamp': datetime(2026, 2, 23, 9, 18), # 09:18 AM
            'date': '2026-02-23'
        },
        'evidence/scenario_parts_flag.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'Ramesh Kumar',
            'ui_context': 'Related Tab',
            # INTENTIONAL SEQUENCE VIOLATION: Timestamp is 09:10 AM, but previous step was 09:18 AM
            'timestamp': datetime(2026, 2, 23, 9, 10), 
            'work_order_number': 'WO-998877',
            'date': '2026-02-23'
        },
        'evidence/jama_login_shadow.png': {
            'salesforce_url': 'gehealthcare.svc--test.sandbox.my.salesforce.com',
            'tester_id': 'manish.batta@gehc.svc.test',
            'ui_context': 'Home Page',
            'timestamp': datetime(2026, 2, 3, 17, 18),
            'date': '2026-02-03'
        }
    }

    # Process each row
    for index, row in df.iterrows():
        test_run_id = str(row['Test Run ID'])
        test_case_id = str(row['Test Case ID'])
        req_id = str(row['Requirement ID'])
        step_number = str(row['Step'])
        ui_context = str(row['UI Context']) if not pd.isna(row['UI Context']) else ""
        action = str(row['Action'])
        expected = str(row['Expected Result'])
        actual = str(row['Actual Result'])
        evidence_path = str(row['Objective Evidence']) if not pd.isna(row['Objective Evidence']) else ""
        
        print(f"Processing Step {step_number}...")

        extracted_data = None
        evidence_paths = []
        requires_evidence = False

        no_evidence_str = "no objective evidence is required / attached"
        if evidence_path and evidence_path.lower() != 'nan' and evidence_path.lower() != no_evidence_str:
            requires_evidence = True
            evidence_paths = [evidence_path]
            # In a real run: extracted_data = analyze_screenshots_for_test_step([evidence_path])[0]
            extracted_data = mock_evidence_data.get(evidence_path)
        
        # Create TestStep object
        step = TestStep(
            step_number=step_number,
            ui_context=ui_context,
            action=action,
            expected_result=expected,
            actual_result=actual,
            objective_evidence_required=requires_evidence,
            evidence_paths=evidence_paths,
            extracted_data=extracted_data
        )

        validator.add_test_step(step)

    # Generate Report
    print("\nRunning Validation Logic...")
    report = validator.generate_report("excel_validation_report.json")
    
    # Write results back to Excel
    print("\nWriting results back to Excel file...")
    # Initialize new columns
    df['Validation Status'] = ''
    df['Validation Notes'] = ''
    
    # Populate columns based on report
    for step_result in report['step_details']:
        # Find the row corresponding to the step number
        # Note: step_number in report is str, so we convert df['Step'] to str for comparison
        mask = df['Step'].astype(str) == step_result['step_number']
        
        df.loc[mask, 'Validation Status'] = step_result['status']
        # Join notes into a single string
        df.loc[mask, 'Validation Notes'] = '\n'.join(step_result['notes'])
    
    # Save the updated DataFrame back to a new Excel file to avoid overwriting the original input
    output_excel_file = "validated_" + excel_file
    
    # Use ExcelWriter to allow formatting
    with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        
        # Get the workbook and active sheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Apply formatting
        from openpyxl.styles import Alignment, Font
        wrap_alignment = Alignment(wrap_text=True, vertical='center')
        header_font = Font(bold=True)
        
        # Dictionary of column widths
        column_widths = {
            'A': 15,  # Test Run ID
            'B': 15,  # Test Case ID
            'C': 15,  # Requirement ID
            'D': 10,  # Step
            'E': 20,  # UI Context
            'F': 40,  # Action
            'G': 40,  # Expected
            'H': 40,  # Actual
            'I': 30,  # Objective Evidence
            'J': 15,  # Status
            'K': 50   # Notes
        }
        
        # Set column widths
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
            
        # Format headers and set row heights for padding
        for row in worksheet.iter_rows():
            # Adjust row height for padding (default is usually ~15, 60 gives good spacing)
            worksheet.row_dimensions[row[0].row].height = 80
            
            for cell in row:
                cell.alignment = wrap_alignment
                if cell.row == 1:
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                    worksheet.row_dimensions[cell.row].height = 50 # Header height
                
                # Center align the ID, Step, Context, and Status columns
                if cell.column_letter in ['A', 'B', 'C', 'D', 'E', 'J']:
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    print(f"Excel file updated and beautifully formatted. Results saved to: {output_excel_file}")

    # Print Summary
    print("\n" + "=" * 50)
    print("EXCEL VALIDATION REPORT SUMMARY")
    print("=" * 50)
    print(f"Total Steps: {report['total_steps']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Warnings: {report['warnings']}")
    
    if report['sequence_violations']:
        print("\nSEQUENCE VIOLATIONS:")
        for violation in report['sequence_violations']:
            print(f"   {violation}")

    print("\nDetailed JSON report saved to: excel_validation_report.json")

if __name__ == "__main__":
    # Create the sample excel file if it doesn't exist
    if not os.path.exists("jama_test_cases.xlsx"):
        print("Generating sample Excel file...")
        import setup_mock_data

    run_excel_validation("jama_test_cases.xlsx")
