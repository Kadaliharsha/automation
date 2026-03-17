import pandas as pd
from validation_engine import JamaTestValidator, TestStep, EvidenceData
from datetime import datetime
import os
from openpyxl.styles import Alignment, Font

def run_excel_validation(excel_file: str):
    print(f"Reading: {excel_file}")
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading {excel_file}: {e}")
        return

    validator = JamaTestValidator()
    
    # Mock evidence mapping for realistic GEHC/FSL steps
    mock_evidence = {
        'evidence/scenario_login.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'manish.batta@gehc.svc.test', 'ui_context': 'Salesforce Login',
            'timestamp': datetime(2026, 3, 17, 9, 5), 'date': '2026-03-17'
        },
        'evidence/scenario_work_order.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'manish.batta@gehc.svc.test', 'ui_context': 'Product Request Modal',
            'timestamp': datetime(2026, 3, 17, 9, 15), 'work_order_number': 'WO-00293847', 'date': '2026-03-17'
        },
        'evidence/scenario_pr_status.png': {
            'salesforce_url': 'ga-healthcare.test.sandbox.salesforce.com',
            'tester_id': 'manish.batta@gehc.svc.test', 'ui_context': 'Product Request Detail',
            'timestamp': datetime(2026, 3, 17, 9, 20), 'date': '2026-03-17'
        }
    }

    for _, row in df.iterrows():
        evi_path = str(row['Objective Evidence']) if not pd.isna(row['Objective Evidence']) else ""
        no_evidence = "no objective evidence is required / attached"
        
        requires_evidence = evi_path and evi_path.lower() not in ['nan', no_evidence]
        extracted = mock_evidence.get(evi_path) if requires_evidence else None
        
        step = TestStep(
            step_number=str(row['Step']),
            action=str(row['Action']),
            expected_result=str(row['Expected Result']),
            actual_result=str(row['Actual Result']),
            ui_context=str(row['UI Context']) if not pd.isna(row['UI Context']) else None,
            objective_evidence_required=requires_evidence,
            evidence_paths=[evi_path] if requires_evidence else [],
            extracted_data=extracted
        )
        validator.add_test_step(step)

    report = validator.validate_all()
    
    df['Validation Status'] = ''
    df['Validation Notes'] = ''
    for res in report['step_details']:
        mask = df['Step'].astype(str) == res['step_number']
        df.loc[mask, 'Validation Status'] = res['status']
        df.loc[mask, 'Validation Notes'] = '\n'.join(res['notes'])
    
    out_file = f"validated_{excel_file}"
    with pd.ExcelWriter(out_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        ws = writer.sheets['Sheet1']
        
        # Column width definitions
        col_widths = {'A':15, 'B':15, 'C':15, 'D':10, 'E':25, 'F':40, 'G':40, 'H':40, 'I':30, 'J':15, 'K':50}
        for col, width in col_widths.items():
            ws.column_dimensions[col].width = width
            
        header_font = Font(bold=True)
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        top_left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)

        # Apply consistent cell formatting and alignment to avoid "crooked" look
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 120 # Consistent height for all data rows
            for cell in row:
                cell.alignment = top_left_align
                if cell.row == 1:
                    cell.font = header_font
                    cell.alignment = center_align
                elif cell.column_letter in ['A', 'B', 'C', 'D', 'E', 'J']:
                    cell.alignment = center_align

        # Merge identical IDs into professional blocks (Columns A, B, C)
        for col_idx in range(1, 4):
            start_row = 2
            while start_row <= ws.max_row:
                current_val = ws.cell(row=start_row, column=col_idx).value
                end_row = start_row
                while end_row + 1 <= ws.max_row and ws.cell(row=end_row + 1, column=col_idx).value == current_val:
                    end_row += 1
                
                if end_row > start_row:
                    ws.merge_cells(start_row=start_row, start_column=col_idx, end_row=end_row, end_column=col_idx)
                    ws.cell(row=start_row, column=col_idx).alignment = center_align
                
                start_row = end_row + 1

    print(f"Validation complete. Report generated with 10 steps: {out_file}")

if __name__ == "__main__":
    import setup_mock_data
    setup_mock_data.create_sample_file()
    run_excel_validation("jama_test_cases.xlsx")
