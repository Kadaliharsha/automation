import pandas as pd

def create_sample_file():
    # Comprehensive, realistic data mimicking a real-world Jama test case execution (15 Steps)
    data = {
        'Test Run ID': ['US-33382', 'US-33382', 'US-33382', 'US-33382', 'US-33382'],
        'Test Case ID': ['TC-7686', 'TC-7686', 'TC-7686', 'TC-7686', 'TC-7686'],
        'Requirement ID': ['REQ-3506', 'REQ-3506', 'REQ-3506', 'REQ-3506', 'REQ-3506'],
        'Step': ['1', '2', '3', '4', '5'],
        'UI Context': ['Login Page', 'Home Page', 'Lightning Experience', 'Work Orders Tab', 'Related Tab'],
        'Action': [
            'Navigate to Salesforce URL',
            'Login to Salesforce\n1) Open a web browser\n2) Record Salesforce URL\n3) Use Tester\'s id and valid password credentials to log into Salesforce.com\n4) Record Tester ID, Login Date, time and time zone',
            'Click on "Switch to Lightning Experience" mode',
            'Navigate to Work Orders',
            'Create Part Request'
        ],
        'Expected Result': [
            'Salesforce login screen is displayed.',
            '1) Web browser is opened\n2) Salesforce URL is recorded https://gehealthcare.svc--test.sandbox.my.salesforce.com\n3) Tester is logged into Salesforce.com.\n4) Tester ID, Login Date, time and time zone are recorded',
            'Verified that user is on Lightning mode',
            'Work Orders List View is displayed.',
            'New Part Request screen opens with required fields.'
        ],
        'Actual Result': [
            'Salesforce login screen displayed successfully.',
            '1) Web browser was opened.\n2) Salesforce URL was recorded https://gehealthcare.svc--test.sandbox.my.salesforce.com\n3) Tester was logged into Salesforce.com.\n4) Tester ID, Login Date, time and time zone was recorded\n(manish.batta@gehc.svc.test 03-Feb-2026 5:18 PM IST)',
            'Verified that user was on Lightning mode',
            'Work Order WO-998877 displayed perfectly.',
            'Part Request PR-44556 created successfully.'
        ],
            'Objective Evidence': [
            'No Objective Evidence is required / attached', 
            'evidence/jama_login_shadow.png', 
            'No Objective Evidence is required / attached', 
            'evidence/scenario_work_order.png', 
            'evidence/scenario_part_request_created.png'
        ]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to Excel
    output_file = 'jama_test_cases.xlsx'
    
    # Format the Excel file using openpyxl
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        from openpyxl.styles import Alignment, Font
        wrap_alignment = Alignment(wrap_text=True, vertical='center')
        header_font = Font(bold=True)
        
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
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
            
        for row in worksheet.iter_rows():
            # Adjust row height for padding
            worksheet.row_dimensions[row[0].row].height = 60
            
            for cell in row:
                cell.alignment = wrap_alignment
                if cell.row == 1:
                    cell.font = header_font
                    worksheet.row_dimensions[cell.row].height = 30 # Header height
                
                # Center align the ID and Step columns
                if cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    print(f"Formatted Sample Excel file created with 15 scenarios: {output_file}")

if __name__ == "__main__":
    create_sample_file()
