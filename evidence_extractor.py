"""
Screenshot Analysis Module
Extracts data from objective evidence screenshots using OCR and AI vision
"""

import re
from datetime import datetime
from typing import Dict, Optional, List
import base64
from pathlib import Path


class ScreenshotAnalyzer:
    """
    Analyzes screenshots to extract relevant test data
    Supports multiple extraction methods: OCR, AI Vision APIs
    """
    
    def __init__(self, method: str = "ai_vision"):
        """
        Initialize screenshot analyzer
        
        Args:
            method: 'tesseract' for OCR, 'ai_vision' for Claude/GPT-4 Vision
        """
        self.method = method
        
    def analyze_screenshot(self, image_path: str) -> Dict:
        """
        Main method to analyze screenshot and extract data
        
        Returns:
            Dictionary containing extracted data:
            - salesforce_url
            - tester_id
            - timestamp
            - work_order_number
            - date
            - raw_text
        """
        if self.method == "tesseract":
            return self._analyze_with_tesseract(image_path)
        elif self.method == "ai_vision":
            return self._analyze_with_ai_vision(image_path)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _analyze_with_tesseract(self, image_path: str) -> Dict:
        """
        Use Tesseract OCR to extract text from screenshot
        """
        try:
            import pytesseract
            from PIL import Image
            
            # Open image and extract text
            image = Image.open(image_path)
            raw_text = pytesseract.image_to_string(image)
            
            # Extract structured data from raw text
            extracted_data = self._extract_structured_data(raw_text)
            extracted_data['screenshot_path'] = image_path
            extracted_data['raw_text'] = raw_text
            
            return extracted_data
            
        except ImportError:
            print("Tesseract not installed. Install with: pip install pytesseract pillow")
            return {}
        except Exception as e:
            print(f"Error in Tesseract OCR: {e}")
            return {}
    
    def _analyze_with_ai_vision(self, image_path: str) -> Dict:
        """
        Use AI Vision API (Claude/GPT-4) to analyze screenshot
        This provides more contextual understanding than pure OCR
        """
        # Convert image to base64
        image_data = self._encode_image(image_path)
        
        # Prepare prompt for AI vision
        prompt = """
        Analyze this Salesforce application screenshot and extract the following information:
        
        1. Salesforce URL (look for URLs like *.salesforce.com or *.force.com)
        2. Tester ID or Username (logged in user)
        3. Date and Timestamp (any visible date/time information)
        4. Work Order Number (look for WO#, Work Order, or similar patterns)
        5. Any other relevant identifiers
        
        Respond ONLY in JSON format:
        {
            "salesforce_url": "extracted URL or null",
            "tester_id": "extracted username or null",
            "timestamp": "extracted timestamp in ISO format or null",
            "work_order_number": "extracted WO# or null",
            "date": "extracted date or null",
            "confidence": "high/medium/low"
        }
        """
        
        # Note: This is a placeholder for actual API call
        # You would integrate with Claude API or OpenAI GPT-4 Vision here
        # For now, return structure for testing
        
        print(f"[AI Vision] Would analyze image: {image_path}")
        print(f"[AI Vision] Prompt prepared for vision model")
        
        # TODO: Implement actual API call
        # extracted_data = self._call_vision_api(image_data, prompt)
        
        return {
            'screenshot_path': image_path,
            'method': 'ai_vision',
            'status': 'pending_api_integration'
        }
    
    def _extract_structured_data(self, raw_text: str) -> Dict:
        """
        Extract structured data from raw OCR text using regex patterns
        """
        extracted = {
            'salesforce_url': None,
            'tester_id': None,
            'timestamp': None,
            'work_order_number': None,
            'date': None
        }
        
        # Extract Salesforce URL
        url_pattern = r'(https?://[^\s]+\.salesforce\.com[^\s]*|https?://[^\s]+\.force\.com[^\s]*)'
        url_match = re.search(url_pattern, raw_text, re.IGNORECASE)
        if url_match:
            extracted['salesforce_url'] = url_match.group(1)
        
        # Extract Work Order Number
        wo_patterns = [
            r'WO[#:\-\s]*(\d+)',
            r'Work\s+Order[#:\-\s]*(\d+)',
            r'W\.O\.[#:\-\s]*(\d+)'
        ]
        for pattern in wo_patterns:
            wo_match = re.search(pattern, raw_text, re.IGNORECASE)
            if wo_match:
                extracted['work_order_number'] = f"WO-{wo_match.group(1)}"
                break
        
        # Extract Timestamp
        timestamp = self._extract_timestamp(raw_text)
        if timestamp:
            extracted['timestamp'] = timestamp
        
        # Extract Date
        date = self._extract_date(raw_text)
        if date:
            extracted['date'] = date
        
        # Extract Tester ID (look for common patterns)
        tester_patterns = [
            r'Tester[:\s]+([A-Za-z]+)',
            r'User[:\s]+([A-Za-z]+)',
            r'Logged\s+in\s+as[:\s]+([A-Za-z]+)'
        ]
        for pattern in tester_patterns:
            tester_match = re.search(pattern, raw_text, re.IGNORECASE)
            if tester_match:
                extracted['tester_id'] = tester_match.group(1)
                break
        
        return extracted
    
    def _extract_timestamp(self, text: str) -> Optional[datetime]:
        """
        Extract timestamp from text
        Supports formats like: 6:16 PM IST, 18:16, etc.
        """
        # Pattern for time with AM/PM
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*IST',
            r'(\d{1,2}):(\d{2})\s*(AM|PM)',
            r'(\d{2}):(\d{2}):(\d{2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if 'AM' in pattern or 'PM' in pattern:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        am_pm = match.group(3).upper()
                        
                        # Convert to 24-hour format
                        if am_pm == 'PM' and hour != 12:
                            hour += 12
                        elif am_pm == 'AM' and hour == 12:
                            hour = 0
                        
                        # Try to extract date too
                        date_str = self._extract_date(text)
                        if date_str:
                            return datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")
                        else:
                            # Return time only (use current date as placeholder)
                            return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                except Exception as e:
                    print(f"Error parsing timestamp: {e}")
                    continue
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """
        Extract date from text
        Supports formats like: February 3, 2026 or 03/02/2026
        """
        # Month name format
        month_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
        match = re.search(month_pattern, text, re.IGNORECASE)
        if match:
            try:
                date_obj = datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%B %d %Y")
                return date_obj.strftime("%Y-%m-%d")
            except:
                pass
        
        # Numeric format (DD/MM/YYYY or MM/DD/YYYY)
        numeric_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(numeric_pattern, text)
        if match:
            # Assume DD/MM/YYYY format (common in India)
            try:
                date_obj = datetime.strptime(f"{match.group(1)}/{match.group(2)}/{match.group(3)}", "%d/%m/%Y")
                return date_obj.strftime("%Y-%m-%d")
            except:
                pass
        
        return None
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API calls"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def validate_screenshot_completeness(self, image_path: str) -> bool:
        """
        Validate that screenshot is complete (contains all corners)
        This is a basic check - could be enhanced with AI vision
        """
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            width, height = image.size
            
            # Basic checks
            if width < 800 or height < 600:
                print(f"Warning: Screenshot may be too small ({width}x{height})")
                return False
            
            # Could add more sophisticated checks here
            return True
            
        except Exception as e:
            print(f"Error validating screenshot: {e}")
            return False


# Integration helper function
def analyze_screenshots_for_test_step(screenshot_paths: List[str], method: str = "tesseract") -> List[Dict]:
    """
    Analyze multiple screenshots for a test step
    
    Args:
        screenshot_paths: List of paths to screenshot files
        method: 'tesseract' or 'ai_vision'
    
    Returns:
        List of extracted data dictionaries
    """
    analyzer = ScreenshotAnalyzer(method=method)
    results = []
    
    for screenshot_path in screenshot_paths:
        print(f"Analyzing screenshot: {screenshot_path}")
        extracted_data = analyzer.analyze_screenshot(screenshot_path)
        results.append(extracted_data)
    
    return results


if __name__ == "__main__":
    # Example usage
    analyzer = ScreenshotAnalyzer(method="tesseract")
    
    # Test text extraction
    sample_text = """
    Salesforce URL: https://ga-healthcare.test.sandbox.salesforce.com
    Tester: Manish
    Date: February 3, 2026
    Time: 6:16 PM IST
    Work Order: WO-738387
    """
    
    extracted = analyzer._extract_structured_data(sample_text)
    print("Extracted Data:")
    for key, value in extracted.items():
        print(f"  {key}: {value}")
