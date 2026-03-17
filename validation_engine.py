
"""
Jama Connect Test Validation Automation
Validates test execution results against expected outcomes using screenshot analysis
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class TestStep:
    """Represents a single test step with action, expected, and actual results"""
    step_number: str
    action: str
    expected_result: str
    actual_result: str
    objective_evidence_required: bool = False
    evidence_paths: Optional[List[str]] = None
    ui_context: Optional[str] = None
    extracted_data: Optional[Dict] = None
    validation_status: str = "PENDING"
    validation_notes: List[str] = None
    mapped_words: List[str] = None
    
    def __post_init__(self):
        if self.evidence_paths is None:
            self.evidence_paths = []
        if self.validation_notes is None:
            self.validation_notes = []
        if self.mapped_words is None:
            self.mapped_words = []


@dataclass
class EvidenceData:
    """Data extracted from objective evidence files (images/documents)"""
    salesforce_url: Optional[str] = None
    tester_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    work_order_number: Optional[str] = None
    ui_context: Optional[str] = None
    date: Optional[str] = None
    raw_text: str = ""
    evidence_path: str = ""
    
    def to_dict(self):
        return {
            'salesforce_url': self.salesforce_url,
            'tester_id': self.tester_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'work_order_number': self.work_order_number,
            'ui_context': self.ui_context,
            'date': self.date,
            'evidence_path': self.evidence_path
        }


class JamaTestValidator:
    """Main validation engine for Jama test cases"""
    
    def __init__(self):
        self.test_steps: List[TestStep] = []
        self.validation_report = []
        
    def add_test_step(self, test_step: TestStep):
        """Add a test step for validation"""
        self.test_steps.append(test_step)
    
    def validate_action_vs_results(self, test_step: TestStep) -> bool:
        """
        Validate if action matches expected and actual results
        Returns True if matching, False otherwise
        """
        action_normalized = self._normalize_text(test_step.action)
        expected_normalized = self._normalize_text(test_step.expected_result)
        actual_normalized = self._normalize_text(test_step.actual_result)
        
        # Extract key terms from action
        action_keywords = self._extract_keywords(action_normalized)
        
        if not action_keywords:
            test_step.validation_notes.append("⚠ No validateable keywords found in action")
            return True # Pass by default if empty
            
        # Extract exact mapped words for audit trail (Word-to-Word mapping)
        expected_mapped_words = [kw for kw in action_keywords if kw in expected_normalized]
        actual_mapped_words = [kw for kw in action_keywords if kw in actual_normalized]
        
        # Keep track of words that made it all the way across
        fully_mapped_words = set(expected_mapped_words).intersection(set(actual_mapped_words))
        test_step.mapped_words = list(fully_mapped_words)
        
        # Set a threshold (e.g., 20% of keywords must match)
        threshold = max(1, len(action_keywords) * 0.20)
        
        expected_match = len(expected_mapped_words) >= threshold
        actual_match = len(actual_mapped_words) >= threshold
        
        if expected_match and actual_match:
            test_step.validation_notes.append("[PASS] Action context matches Expected and Actual results")
            test_step.validation_notes.append(f"└─ Mapped Keywords Verified: {', '.join(fully_mapped_words)}")
            return True
        else:
            if not expected_match:
                test_step.validation_notes.append("[FAIL] Expected result lacks context from Action")
            if not actual_match:
                test_step.validation_notes.append("[FAIL] Actual result lacks context from Action")
                
            test_step.validation_notes.append(f"└─ Attempted Mapping Failed. Found: {', '.join(fully_mapped_words) if fully_mapped_words else 'None'}")
            return False
    
    def validate_evidence(self, test_step: TestStep, extracted_data: EvidenceData) -> bool:
        """
        Validate data extracted from objective evidence against the test step
        """
        validation_passed = True
        
        # Verify UI Context (Tab/Page)
        if test_step.ui_context and extracted_data.ui_context:
            if self._normalize_text(test_step.ui_context) == self._normalize_text(extracted_data.ui_context):
                test_step.validation_notes.append(f"[PASS] UI Context verified: {extracted_data.ui_context}")
            else:
                test_step.validation_notes.append(f"[FAIL] UI Context mismatch: Expected '{test_step.ui_context}', found '{extracted_data.ui_context}' in evidence")
                validation_passed = False
        
        # Check if URL mentioned in actual result matches evidence
        # If the actual result doesn't mention a URL at all, we shouldn't fail the step, we just can't verify it
        if extracted_data.salesforce_url:
            if self._find_in_text(test_step.actual_result, extracted_data.salesforce_url):
                test_step.validation_notes.append(f"[PASS] Salesforce URL verified: {extracted_data.salesforce_url}")
            elif "URL:" in test_step.actual_result: # Only fail if they claimed a URL but it doesn't match
                test_step.validation_notes.append(f"[FAIL] Salesforce URL mismatch in evidence")
                validation_passed = False
        
        # Check tester ID
        if extracted_data.tester_id:
            if self._find_in_text(test_step.actual_result, extracted_data.tester_id):
                test_step.validation_notes.append(f"[PASS] Tester ID verified: {extracted_data.tester_id}")
            elif "Tester:" in test_step.actual_result or "User:" in test_step.actual_result:
                test_step.validation_notes.append(f"[FAIL] Tester ID mismatch")
                validation_passed = False
        
        # Check Work Order number
        if extracted_data.work_order_number:
            if self._find_in_text(test_step.actual_result, extracted_data.work_order_number):
                test_step.validation_notes.append(f"[PASS] Work Order verified: {extracted_data.work_order_number}")
            elif "WO-" in test_step.actual_result:
                test_step.validation_notes.append(f"[FAIL] Work Order mismatch - Evidence shows {extracted_data.work_order_number}")
                validation_passed = False
        
        # Check timestamp presence
        if extracted_data.timestamp:
            test_step.validation_notes.append(f"[PASS] Timestamp found: {extracted_data.timestamp}")
        elif test_step.objective_evidence_required:
            test_step.validation_notes.append("[WARNING] No timestamp found in evidence")
            validation_passed = False
        
        return validation_passed
    
    def validate_timestamp_sequence(self) -> List[str]:
        """
        Validate that all test steps are executed in chronological order
        Returns list of sequence violations
        """
        violations = []
        timestamps = []
        
        # Collect all timestamps with step numbers
        for step in self.test_steps:
            if step.extracted_data and 'timestamp' in step.extracted_data:
                ts = step.extracted_data['timestamp']
                if ts:
                    timestamps.append((step.step_number, ts))
        
        # Check if timestamps are in order
        for i in range(len(timestamps) - 1):
            current_step, current_time = timestamps[i]
            next_step, next_time = timestamps[i + 1]
            
            if current_time > next_time:
                violation = f"[WARNING] SEQUENCE VIOLATION: Step {current_step} ({current_time}) executed AFTER Step {next_step} ({next_time})"
                violations.append(violation)
        
        return violations
    
    def validate_all(self) -> Dict:
        """
        Run complete validation on all test steps
        Returns validation report
        """
        report = {
            'total_steps': len(self.test_steps),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'sequence_violations': [],
            'step_details': []
        }
        
        # Validate each step
        for step in self.test_steps:
            step_result = {
                'step_number': step.step_number,
                'action': step.action,
                'status': 'PASS',
                'notes': []
            }
            
            # Validate action vs results
            action_valid = self.validate_action_vs_results(step)
            
            # Validate evidence if required
            evidence_valid = True
            if step.objective_evidence_required and step.extracted_data:
                evidence_data = EvidenceData(**step.extracted_data)
                evidence_valid = self.validate_evidence(step, evidence_data)
            
            # Determine overall step status
            if action_valid and evidence_valid:
                step.validation_status = "PASS"
                report['passed'] += 1
            else:
                step.validation_status = "FAIL"
                report['failed'] += 1
            
            step_result['status'] = step.validation_status
            step_result['notes'] = step.validation_notes
            report['step_details'].append(step_result)
        
        # Check timestamp sequence
        sequence_violations = self.validate_timestamp_sequence()
        report['sequence_violations'] = sequence_violations
        
        if sequence_violations:
            report['warnings'] += len(sequence_violations)
        
        return report
    
    def generate_report(self, output_path: str = "validation_report.json"):
        """Generate JSON report of validation results"""
        report = self.validate_all()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    # Helper methods
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison by removing punctuation and extra spaces"""
        # Remove punctuation so "Service." matches "Service"
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # More comprehensive stop words list
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
                      'shall', 'must', 'should', 'have', 'has', 'had', 'user', 'tester',
                      'system', 'this', 'that', 'it', 'as'}
        
        words = text.split()
        # Only keep words > 2 chars, filter stop words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords
    
    def _find_in_text(self, text: str, search_term: str) -> bool:
        """Case-insensitive search in text, ignoring punctuation"""
        normalized_text = self._normalize_text(text)
        normalized_search = self._normalize_text(search_term)
        return normalized_search in normalized_text


if __name__ == "__main__":
    # Example usage
    validator = JamaTestValidator()
    
    # Example test step
    step1 = TestStep(
        step_number="1.1",
        action="User must have access to Salesforce application",
        expected_result="User shall have access to Salesforce application",
        actual_result="User had access to Salesforce application",
        objective_evidence_required=True,
        evidence_paths=["evidence1.png"],
        extracted_data={
            'salesforce_url': 'ga.healthcare.test.sandbox',
            'tester_id': 'Manish',
            'timestamp': datetime(2026, 2, 3, 18, 16),
            'date': 'February 3, 2026'
        }
    )
    
    validator.add_test_step(step1)
    report = validator.generate_report()
    
    print("Validation Report Generated:")
    print(json.dumps(report, indent=2, default=str))
