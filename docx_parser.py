import re
import json

def parse_jama_text_export(filepath: str):
    """
    Programmatically extracts Test Steps from an unstructured Jama Word Export.
    Relies on structural heuristics rather than hardcoded text.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split the document into blocks separated by empty lines
    blocks = text.split('\n\n')
    parsed_steps = []
    
    for block in blocks:
        block = block.strip()
        # Flatten newlines within a single block for easier regex matching
        block = re.sub(r'\n+', ' ', block)
        
        # Heuristic Pattern matching:
        # Looks for "1: [Action], [Expected], RequiresObjectiveEvidence: [Yes/No], [Status], [Actual]"
        # We use non-greedy matching (.*?) to accurately split at the commas before specific keywords
        pattern = r'^(\d+):\s*(.*?),\s*(.*?),\s*RequiresObjectiveEvidence:\s*(Yes|No),\s*(Passed|Failed|Pass with Errors|Not Run|Blocked),\s*(.*)$'
        
        match = re.match(pattern, block, re.IGNORECASE)
        
        if match:
            step_num = match.group(1).strip()
            action = match.group(2).strip()
            expected = match.group(3).strip()
            req_evidence = match.group(4).strip().lower() == 'yes'
            status = match.group(5).strip()
            actual = match.group(6).strip()
            
            # Smart Variable Extractor finding anything between < >
            expected_placeholders = re.findall(r'<([^>]+)>', expected)
            actual_values = re.findall(r'<([^>]+)>', actual)
            
            parsed_steps.append({
                'step_number': step_num,
                'action': action,
                'expected_result': expected,
                'actual_result': actual,
                'objective_evidence_required': req_evidence,
                'tester_status': status,
                'dynamic_variables': {
                    'expected': expected_placeholders,
                    'actual': actual_values
                }
            })

    return parsed_steps

if __name__ == '__main__':
    # Test the parser against the extracted text
    results = parse_jama_text_export('extracted_review.txt')
    print(f"Successfully extracted {len(results)} steps.\n")
    print(json.dumps(results[:2], indent=2)) # Print first 2 for review
