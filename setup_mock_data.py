import pandas as pd
from openpyxl.styles import Alignment, Font

def create_sample_file(output_file: str = "jama_test_cases.xlsx"):
    data = {
        'Test Run ID': ['US-33382'] * 10,
        'Test Case ID': ['TC-7686'] * 10,
        'Requirement ID': ['REQ-3506'] * 10,
        'Step': [str(i) for i in range(1, 11)],
        'UI Context': [
            'Salesforce Login', 'FSL Home', 'Service Work Order', 
            'Related List: Parts', 'Product Request Modal', 'Product Request Detail',
            'Stock Transfer Page', 'Shipment Detail', 'Inventory Ledger', 'Test Close'
        ],
        'Action': [
            '1) Open a web browser\n2) Enter the GEHC Salesforce URL: ga-healthcare.test.sandbox.salesforce.com\n3) Use valid SSO credentials for manish.batta@gehc.svc.test\n4) Navigate to the Production Sandbox environment.',
            '1) In the Global Search bar, type the Work Order ID: WO-00293847\n2) Select the matching record from the search results dropping down.',
            '1) Once the Work Order record loads, scroll down to the "Products Required" related list.\n2) Verify the list is visible and populated.',
            '1) Click the "New" button in the Products Required related list title bar.\n2) Wait for the modal window to load.',
            '1) Locate the SKU lookup field.\n2) Select SKU: GE-9988-X\n3) Set Quantity: 1\n4) Set Priority: "Expedited"\n5) Capture screenshot of the populated modal.',
            '1) Click "Save" on the modal.\n2) Verify the new PR-445566 record appears in the list.\n3) Capture screenshot of the record detail view.',
            '1) Navigate to the Stock Transfer sub-tab.\n2) Click "Transfer Inventory" button.',
            '1) Verify Shipment track number SHP-001928 is correctly generated.\n2) Check for "Shipped" status tag.',
            '1) Open the Inventory Ledger view.\n2) Search for Part: GE-9988-X to verify deduction.',
            '1) Finalize the test execution.\n2) Record total duration and sign off.'
        ],
        'Expected Result': [
            '1) System redirects to the Salesforce Home Page dashboard.\n2) User ID manish.batta@gehc.svc.test is visible in the profile section.',
            '1) Work Order WO-00293847 is successfully retrieved.\n2) The page header displays the correct Work Order number.',
            '1) The user is navigated to the correct "Related" tab view.\n2) The "Products Required" section is rendered correctly on the screen.',
            '1) The "New Product Required" modal window pops up over the current view.\n2) The focus shifts to the modal fields.',
            '1) All mandatory fields (SKU, Qty) are correctly filled.\n2) No validation error messages appear for the "Expedited" priority.',
            '1) The Product Request (PR-445566) is successfully saved.\n2) The record is visible in the parent Work Order Related List.',
            '1) Transfer modal opens correctly.\n2) Source warehouse "Global Depo" is autopopulated.',
            '1) Status changes to "Shipped".\n2) Transit time estimated at 24 hours.',
            '1) Ledger shows -1 unit for GE-9988-X.\n2) Remaining stock: 49 units.',
            '1) Test run status set to "Complete".\n2) All evidence files attached successfully.'
        ],
        'Actual Result': [
            '1) Salesforce URL ga-healthcare.test.sandbox.salesforce.com opened.\n2) manish.batta@gehc.svc.test logged in successfully at 09:05 AM.',
            '1) Search for WO-00293847 returned 1 match.\n2) Work Order record detail view loaded.',
            '1) Related list section found.\n2) Navigation to the list view confirmed.',
            '1) Modal window displayed.\n2) UI Context updated to Product Request Modal.',
            '1) SKU GE-9988-X successfully selected.\n2) Quantity set to 1.\n3) Screenshot captured: evidence/scenario_work_order.png',
            '1) PR-445566 saved successfully.\n2) Record visible in the list.\n3) Screenshot captured: evidence/scenario_pr_status.png',
            '1) Navigated to Transfer sub-tab.',
            '1) SHP-001928 generated.\n2) Status: Shipped.',
            '1) Part deduction confirmed for GE-9988-X.\n2) Deduction shown in ledger.',
            '1) Execution finalized at 11:30 AM.\n2) Sign off completed by manish.batta.'
        ],
        'Objective Evidence': [
            'evidence/scenario_login.png',
            'no objective evidence is required / attached',
            'no objective evidence is required / attached',
            'no objective evidence is required / attached',
            'evidence/scenario_work_order.png',
            'evidence/scenario_pr_status.png',
            'no objective evidence is required / attached',
            'no objective evidence is required / attached',
            'no objective evidence is required / attached',
            'no objective evidence is required / attached'
        ]
    }

    df = pd.DataFrame(data)
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        ws = writer.sheets['Sheet1']
        
        widths = {'A':15, 'B':15, 'C':15, 'D':10, 'E':25, 'F':50, 'G':50, 'H':50, 'I':30}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
            
        header_font = Font(bold=True)
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        top_left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)
        
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 120 # Consistent row height
            for cell in row:
                cell.alignment = top_left_align
                if cell.row == 1:
                    cell.font = header_font
                    cell.alignment = center_align
                elif cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
                    cell.alignment = center_align

    print(f"Richly Detailed GEHC Sample data restored with 10 steps: {output_file}")

if __name__ == "__main__":
    create_sample_file()
