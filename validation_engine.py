import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestStep:
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
        self.evidence_paths = self.evidence_paths or []
        self.validation_notes = self.validation_notes or []
        self.mapped_words = self.mapped_words or []

@dataclass
class EvidenceData:
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
    """Core logic for validating Jama Connect test results against evidence."""
    
    def __init__(self):
        self.test_steps: List[TestStep] = []
        
    def add_test_step(self, test_step: TestStep):
        self.test_steps.append(test_step)
    
    def validate_action_vs_results(self, test_step: TestStep) -> bool:
        action_norm = self._normalize_text(test_step.action)
        expected_norm = self._normalize_text(test_step.expected_result)
        actual_norm = self._normalize_text(test_step.actual_result)
        
        keywords = self._extract_keywords(action_norm)
        if not keywords:
            test_step.validation_notes.append("No validateable keywords found in action")
            return True
            
        expected_mapped = [kw for kw in keywords if kw in expected_norm]
        actual_mapped = [kw for kw in keywords if kw in actual_norm]
        
        fully_mapped = set(expected_mapped).intersection(set(actual_mapped))
        test_step.mapped_words = list(fully_mapped)
        
        threshold = max(1, len(keywords) * 0.20)
        expected_match = len(expected_mapped) >= threshold
        actual_match = len(actual_mapped) >= threshold
        
        if expected_match and actual_match:
            test_step.validation_notes.append("[PASS] Action context matches Expected and Actual results")
            test_step.validation_notes.append(f"Mapped Keywords: {', '.join(fully_mapped)}")
            return True

        if not expected_match:
            test_step.validation_notes.append("[FAIL] Expected result lacks context from Action")
        if not actual_match:
            test_step.validation_notes.append("[FAIL] Actual result lacks context from Action")
            
        test_step.validation_notes.append(f"Audit Trail: {', '.join(fully_mapped) if fully_mapped else 'None'}")
        return False
    
    def validate_evidence(self, test_step: TestStep, evidence_data: EvidenceData) -> bool:
        is_valid = True
        
        # UI Tab/Page Verification
        if test_step.ui_context and evidence_data.ui_context:
            if self._normalize_text(test_step.ui_context) == self._normalize_text(evidence_data.ui_context):
                test_step.validation_notes.append(f"[PASS] UI Context: {evidence_data.ui_context}")
            else:
                test_step.validation_notes.append(f"[FAIL] UI Context mismatch: Expected '{test_step.ui_context}', found '{evidence_data.ui_context}'")
                is_valid = False
        
        # Attribute Verification (URL, Tester, Work Order)
        mappings = [
            (evidence_data.salesforce_url, "Salesforce URL", "URL:"),
            (evidence_data.tester_id, "Tester ID", "Tester:"),
            (evidence_data.work_order_number, "Work Order", "WO-")
        ]

        for val, label, trigger in mappings:
            if not val: continue
            if self._find_in_text(test_step.actual_result, val):
                test_step.validation_notes.append(f"[PASS] {label} verified: {val}")
            elif trigger in test_step.actual_result:
                test_step.validation_notes.append(f"[FAIL] {label} mismatch")
                is_valid = False

        if evidence_data.timestamp:
            test_step.validation_notes.append(f"[PASS] Timestamp: {evidence_data.timestamp}")
        elif test_step.objective_evidence_required:
            test_step.validation_notes.append("[WARNING] Missing timestamp in evidence")
            is_valid = False
            
        return is_valid
    
    def validate_timestamp_sequence(self) -> List[str]:
        violations = []
        steps_with_ts = [
            (s.step_number, s.extracted_data['timestamp']) 
            for s in self.test_steps 
            if s.extracted_data and s.extracted_data.get('timestamp')
        ]
        
        for i in range(len(steps_with_ts) - 1):
            curr_step, curr_ts = steps_with_ts[i]
            next_step, next_ts = steps_with_ts[i + 1]
            if curr_ts > next_ts:
                violations.append(f"[WARNING] Sequence Violation: Step {curr_step} ({curr_ts}) after Step {next_step} ({next_ts})")
        return violations
    
    def validate_all(self) -> Dict:
        report = {
            'total_steps': len(self.test_steps),
            'passed': 0, 'failed': 0, 'warnings': 0,
            'sequence_violations': [],
            'step_details': []
        }
        
        for step in self.test_steps:
            action_valid = self.validate_action_vs_results(step)
            evidence_valid = True
            
            if step.objective_evidence_required and step.extracted_data:
                evidence_data = EvidenceData(**step.extracted_data)
                evidence_valid = self.validate_evidence(step, evidence_data)
            
            step.validation_status = "PASS" if (action_valid and evidence_valid) else "FAIL"
            if step.validation_status == "PASS": report['passed'] += 1
            else: report['failed'] += 1
            
            report['step_details'].append({
                'step_number': step.step_number,
                'status': step.validation_status,
                'notes': step.validation_notes
            })
        
        violations = self.validate_timestamp_sequence()
        report['sequence_violations'] = violations
        report['warnings'] = len(violations)
        return report
    
    def generate_report(self, path: str = "validation_report.json"):
        report = self.validate_all()
        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        return report
    
    def _normalize_text(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_keywords(self, text: str) -> List[str]:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
                      'shall', 'must', 'should', 'have', 'has', 'had', 'user', 'tester',
                      'system', 'this', 'that', 'it', 'as'}
        return [w for w in text.split() if w not in stop_words and len(w) > 2]
    
    def _find_in_text(self, text: str, term: str) -> bool:
        return self._normalize_text(term) in self._normalize_text(text)

if __name__ == "__main__":
    v = JamaTestValidator()
    step = TestStep("1.1", "Log in", "Log in", "Logged in", True, ["ev.png"], "Home")
    v.add_test_step(step)
    print(json.dumps(v.generate_report(), indent=2, default=str))
