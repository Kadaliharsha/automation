import pandas as pd
from validation_engine import JamaTestValidator, TestStep
from docx_parser import parse_jama_text_export
from openpyxl.styles import Alignment, Font

def run_word_doc_validation(parsed_txt_path: str):
    print(f"Reading unstructured data via Heuristic Parser: {parsed_txt_path}")
    
    # 1. Parse the unstructured document
    extracted_steps = parse_jama_text_export(parsed_txt_path)
    
    validator = JamaTestValidator()
    
    # 2. Feed the unstructured data into our powerful structured engine
    for raw_step in extracted_steps:
        # We append the extracted dynamic variables to the expected/actual strings 
        # so the Validation Engine evaluates them in its Word-to-Word mapping.
        action_text = raw_step['action']
        expected_text = raw_step['expected_result'] 
        actual_text = raw_step['actual_result']

        step = TestStep(
            step_number=raw_step['step_number'],
            action=action_text,
            expected_result=expected_text,
            actual_result=actual_text,
            objective_evidence_required=raw_step['objective_evidence_required'],
            validation_status="PENDING" 
        )
        validator.add_test_step(step)

    # 3. Run the Core Validation Engine (Word-to-Word Mapping & Logic Checks)
    report = validator.validate_all()
    
    # 4. Generate the Audit Report
    df_data = []
    for step, raw in zip(report['step_details'], extracted_steps):
        dyn = raw['dynamic_variables']
        exp_vars = ", ".join([f"<{v}>" for v in dyn['expected']]) if dyn.get('expected') else "None"
        act_vars = ", ".join([f"<{v}>" for v in dyn['actual']]) if dyn.get('actual') else "None"
        dynamic_display = f"Expected: {exp_vars}\nActual: {act_vars}"

        df_data.append({
            'Step': raw['step_number'],
            'Action': raw['action'],
            'Expected Result': raw['expected_result'],
            'Actual Result': raw['actual_result'],
            'Dynamic Variables': dynamic_display,
            'Tester Claimed Status': raw['tester_status'], 
            'Script Validation Status': step['status'], 
            'Script Validation Notes': '\n'.join(step['notes'])
        })
        
    df = pd.DataFrame(df_data)
    
    out_file = "validated_manager_docx_run_v2.xlsx"
    with pd.ExcelWriter(out_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        ws = writer.sheets['Sheet1']
        
        widths = {'A':10, 'B':40, 'C':40, 'D':40, 'E':25, 'F':15, 'G':20, 'H':50}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
            
        header_font = Font(bold=True)
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)
        
        for row in ws.iter_rows():
            if row[0].row > 1:
                ws.row_dimensions[row[0].row].height = 100
            for cell in row:
                cell.alignment = left_align
                if cell.row == 1:
                    cell.font = header_font
                    cell.alignment = center_align

    print(f"Validation complete! Machine-audited report generated: {out_file}")

if __name__ == "__main__":
    run_word_doc_validation("Review - Test Run US32200_Windows_Enhance offline experience + action buttons always visible on the WO card.docx")
