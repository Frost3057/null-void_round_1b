"""
Text Encoding Integrity Checker
Validates multilingual text for encoding issues and corruption patterns.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional


class TextEncodingIntegrityChecker:
    """
    Validates text encoding integrity and detects corruption patterns in multilingual content.
    """
    
    def __init__(self):
        """Initialize the integrity checker with Devanagari character sets."""
        self.devanagari_unicode_range = range(0x0900, 0x097F + 1)
        self.standard_devanagari_characters = {
            'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ',
            'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ',
            'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न',
            'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह',
            'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ',
            'ं', 'ः', '्', '।', '॥'
        }
        
    def verify_devanagari_script_authenticity(self, input_text: str) -> bool:
        """
        Verify if Devanagari text is authentic and not corrupted.
        
        Args:
            input_text: Text to verify
            
        Returns:
            True if text is authentic, False if corrupted
        """
        if not input_text:
            return True
            
        contains_devanagari_characters = any(
            ord(character) in self.devanagari_unicode_range 
            for character in input_text
        )
        
        if not contains_devanagari_characters:
            return True
        
        # Check for corruption patterns
        corruption_detection_patterns = [
            r'[^\u0900-\u097F\s\.,!?;:()\[\]{}"\'-]',  # Non-Devanagari chars in Devanagari text
            r'[A-Za-z0-9]+[\u0900-\u097F]+',  # Latin followed by Devanagari
            r'[\u0900-\u097F]+[A-Za-z0-9]+',  # Devanagari followed by Latin
        ]
        
        for detection_pattern in corruption_detection_patterns:
            if re.search(detection_pattern, input_text):
                return False
                
        return True
    
    def analyze_text_corruption_patterns(self, input_text: str) -> Dict[str, Any]:
        """
        Analyze text for various corruption patterns and encoding issues.
        
        Args:
            input_text: Text to analyze
            
        Returns:
            Dictionary with corruption analysis results
        """
        identified_integrity_issues = []
        
        if not input_text:
            return {"is_garbled": False, "issues": []}
        
        # Count character types
        devanagari_character_collection = [
            character for character in input_text 
            if ord(character) in self.devanagari_unicode_range
        ]
        latin_character_collection = [
            character for character in input_text 
            if character.isalpha() and ord(character) < 128
        ]
        
        # Check for mixed scripts
        if devanagari_character_collection and latin_character_collection:
            identified_integrity_issues.append({
                "type": "mixed_scripts",
                "description": "Devanagari and Latin characters mixed",
                "devanagari_count": len(devanagari_character_collection),
                "latin_count": len(latin_character_collection)
            })
        
        # Check for Unicode encoding errors
        try:
            input_text.encode('utf-8').decode('utf-8')
        except UnicodeError:
            identified_integrity_issues.append({
                "type": "unicode_error",
                "description": "Invalid Unicode sequence"
            })
        
        # Check for repeated characters (potential corruption)
        detected_repeated_characters = re.findall(r'(.)\\1{2,}', input_text)
        if detected_repeated_characters:
            identified_integrity_issues.append({
                "type": "repeated_characters",
                "description": "Repeated characters detected",
                "repeated_chars": list(set(detected_repeated_characters))
            })
        
        # Check for anomalous patterns
        anomalous_character_patterns = [
            r'[^\u0900-\u097F\s\.,!?;:()\[\]{}"\'-]',  # Invalid chars in Devanagari
            r'[A-Z]{3,}',  # All caps sequences
            r'[0-9]+[A-Za-z]+',  # Number-letter combinations
        ]
        
        for anomalous_pattern in anomalous_character_patterns:
            pattern_matches = re.findall(anomalous_pattern, input_text)
            if pattern_matches:
                identified_integrity_issues.append({
                    "type": "unusual_patterns",
                    "description": "Unusual character patterns",
                    "patterns": pattern_matches[:5]  # Limit to first 5 matches
                })
        
        return {
            "is_garbled": len(identified_integrity_issues) > 0,
            "issues": identified_integrity_issues,
            "text_length": len(input_text),
            "devanagari_chars": len(devanagari_character_collection),
            "latin_chars": len(latin_character_collection)
        }
    
    def perform_comprehensive_json_file_validation(self, json_file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive validation of JSON file containing multilingual text.
        
        Args:
            json_file_path: Path to JSON file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file_handle:
                parsed_json_data = json.load(file_handle)
        except Exception as file_reading_error:
            return {"error": str(file_reading_error)}
        
        comprehensive_validation_results = {
            "file": json_file_path,
            "total_texts": 0,
            "valid_texts": 0,
            "garbled_texts": 0,
            "issues": []
        }
        
        def recursive_text_field_validation(text_content: Any, json_field_path: str) -> None:
            """Recursively validate text fields in JSON structure."""
            if isinstance(text_content, dict):
                for language_key, content_value in text_content.items():
                    recursive_text_field_validation(
                        content_value, 
                        f"{json_field_path}.{language_key}"
                    )
            elif isinstance(text_content, str):
                comprehensive_validation_results["total_texts"] += 1
                
                if self.verify_devanagari_script_authenticity(text_content):
                    comprehensive_validation_results["valid_texts"] += 1
                else:
                    comprehensive_validation_results["garbled_texts"] += 1
                    text_corruption_analysis = self.analyze_text_corruption_patterns(text_content)
                    comprehensive_validation_results["issues"].append({
                        "field": json_field_path,
                        "text": text_content[:100] + "..." if len(text_content) > 100 else text_content,
                        "garbled_info": text_corruption_analysis
                    })
        
        # Validate different sections of the JSON
        if "title" in parsed_json_data:
            recursive_text_field_validation(parsed_json_data["title"], "title")
        
        if "outline" in parsed_json_data:
            for heading_index, heading_item in enumerate(parsed_json_data["outline"]):
                if "text" in heading_item:
                    recursive_text_field_validation(
                        heading_item["text"], 
                        f"outline[{heading_index}].text"
                    )
        
        if "extracted_sections" in parsed_json_data:
            for section_index, section_item in enumerate(parsed_json_data["extracted_sections"]):
                if "section_title" in section_item:
                    recursive_text_field_validation(
                        section_item["section_title"], 
                        f"extracted_sections[{section_index}].section_title"
                    )
        
        # Calculate accuracy
        if comprehensive_validation_results["total_texts"] > 0:
            comprehensive_validation_results["accuracy"] = (
                comprehensive_validation_results["valid_texts"] / 
                comprehensive_validation_results["total_texts"]
            )
        else:
            comprehensive_validation_results["accuracy"] = 0.0
        
        return comprehensive_validation_results


class MultilingualValidationPipeline:
    """
    Complete pipeline for multilingual text validation and reporting.
    """
    
    def __init__(self):
        """Initialize the validation pipeline."""
        self.text_integrity_validator = TextEncodingIntegrityChecker()
    
    def validate_directory(self, input_directory: str, detailed_output: bool = False) -> Dict[str, Any]:
        """
        Validate all JSON files in a directory.
        
        Args:
            input_directory: Directory containing JSON files
            detailed_output: Whether to show detailed validation results
            
        Returns:
            Dictionary with comprehensive validation results
        """
        comprehensive_validation_results = []
        total_processed_files = 0
        total_detected_issues = 0
        
        if not os.path.exists(input_directory):
            return {
                "error": f"Directory {input_directory} does not exist",
                "total_files_processed": 0,
                "total_issues_found": 0
            }
        
        print("🔍 Multilingual Text Validation")
        print("=" * 40)
        
        for json_filename in os.listdir(input_directory):
            if json_filename.endswith('.json'):
                complete_file_path = os.path.join(input_directory, json_filename)
                print(f"\\n📄 Validating: {json_filename}")
                
                file_validation_result = self.text_integrity_validator.perform_comprehensive_json_file_validation(
                    complete_file_path
                )
                comprehensive_validation_results.append(file_validation_result)
                total_processed_files += 1
                
                if "error" in file_validation_result:
                    print(f"❌ Error: {file_validation_result['error']}")
                    continue
                
                print(f"  📊 Results:")
                print(f"    - Total texts: {file_validation_result['total_texts']}")
                print(f"    - Valid texts: {file_validation_result['valid_texts']}")
                print(f"    - Garbled texts: {file_validation_result['garbled_texts']}")
                print(f"    - Accuracy: {file_validation_result.get('accuracy', 0):.3f}")
                
                if file_validation_result['issues']:
                    total_detected_issues += len(file_validation_result['issues'])
                    print(f"    - Issues found: {len(file_validation_result['issues'])}")
                    
                    if detailed_output:
                        for integrity_issue in file_validation_result['issues'][:3]:
                            print(f"      * {integrity_issue['field']}: {integrity_issue['text']}")
                            for corruption_detail in integrity_issue['garbled_info']['issues'][:2]:
                                print(f"        - {corruption_detail['type']}: {corruption_detail['description']}")
        
        # Generate summary report
        validation_summary_report = {
            "total_files_processed": total_processed_files,
            "total_issues_found": total_detected_issues,
            "files_with_issues": len([
                validation_result for validation_result in comprehensive_validation_results 
                if validation_result.get('garbled_texts', 0) > 0
            ]),
            "overall_accuracy": (
                sum(validation_result.get('accuracy', 0) for validation_result in comprehensive_validation_results) / 
                len(comprehensive_validation_results) 
                if comprehensive_validation_results else 0
            ),
            "detailed_results": comprehensive_validation_results
        }
        
        print(f"\\n📊 Summary:")
        print(f"  - Files processed: {total_processed_files}")
        print(f"  - Files with issues: {validation_summary_report['files_with_issues']}")
        print(f"  - Total issues found: {total_detected_issues}")
        print(f"  - Overall accuracy: {validation_summary_report['overall_accuracy']:.3f}")
        
        if validation_summary_report['files_with_issues'] > 0:
            print(f"\\n⚠️  Files with multilingual issues:")
            for validation_result in comprehensive_validation_results:
                if validation_result.get('garbled_texts', 0) > 0:
                    print(f"  - {os.path.basename(validation_result['file'])}: {validation_result['garbled_texts']} issues")
        
        return validation_summary_report
    
    def save_validation_report(self, validation_results: Dict[str, Any], output_file: str) -> None:
        """
        Save validation results to JSON file.
        
        Args:
            validation_results: Validation results to save
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as report_output_file:
                json.dump(validation_results, report_output_file, ensure_ascii=False, indent=2)
            print(f"  - Detailed report saved to: {output_file}")
        except Exception as save_error:
            print(f"❌ Failed to save report: {save_error}")
