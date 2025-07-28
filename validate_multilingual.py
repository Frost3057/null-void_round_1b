import json
import os
import argparse
import re
import unicodedata
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class TextEncodingIntegrityChecker:
    def __init__(self):
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
        if not input_text:
            return True
        contains_devanagari_characters = any(ord(character) in self.devanagari_unicode_range for character in input_text)
        if not contains_devanagari_characters:
            return True
        corruption_detection_patterns = [
            r'[^\u0900-\u097F\s\.,!?;:()\[\]{}"\'-]',
            r'[A-Za-z0-9]+[\u0900-\u097F]+',
            r'[\u0900-\u097F]+[A-Za-z0-9]+',
        ]
        for detection_pattern in corruption_detection_patterns:
            if re.search(detection_pattern, input_text):
                return False
        return True
    
    def analyze_text_corruption_patterns(self, input_text: str) -> Dict[str, Any]:
        identified_integrity_issues = []   
        if not input_text:
            return {"is_garbled": False, "issues": []}
        devanagari_character_collection = [character for character in input_text if ord(character) in self.devanagari_unicode_range]
        latin_character_collection = [character for character in input_text if character.isalpha() and ord(character) < 128]
        if devanagari_character_collection and latin_character_collection:
            identified_integrity_issues.append({
                "type": "mixed_scripts",
                "description": "Devanagari and Latin characters mixed",
                "devangari_count": len(devanagari_character_collection),
                "latin_count": len(latin_character_collection)
            })
        try:
            input_text.encode('utf-8').decode('utf-8')
        except UnicodeError:
            identified_integrity_issues.append({
                "type": "unicode_error",
                "description": "Invalid Unicode sequence"
            })
        detected_repeated_characters = re.findall(r'(.)\1{2,}', input_text)
        if detected_repeated_characters:
            identified_integrity_issues.append({
                "type": "repeated_characters",
                "description": "Repeated characters detected",
                "repeated_chars": list(set(detected_repeated_characters))
            })
        anomalous_character_patterns = [
            r'[^\u0900-\u097F\s\.,!?;:()\[\]{}"\'-]',
            r'[A-Z]{3,}',
            r'[0-9]+[A-Za-z]+',
        ]
        for anomalous_pattern in anomalous_character_patterns:
            pattern_matches = re.findall(anomalous_pattern, input_text)
            if pattern_matches:
                identified_integrity_issues.append({
                    "type": "unusual_patterns",
                    "description": "Unusual character patterns",
                    "patterns": pattern_matches[:5]
                })
        return {
            "is_garbled": len(identified_integrity_issues) > 0,
            "issues": identified_integrity_issues,
            "text_length": len(input_text),
            "devangari_chars": len(devanagari_character_collection),
            "latin_chars": len(latin_character_collection)
        }
    
    def perform_comprehensive_json_file_validation(self, json_file_path: str) -> Dict[str, Any]:
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
        
        def recursive_text_field_validation(text_content, json_field_path):
            if isinstance(text_content, dict):
                for language_key, content_value in text_content.items():
                    recursive_text_field_validation(content_value, f"{json_field_path}.{language_key}")
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
        if "title" in parsed_json_data:
            recursive_text_field_validation(parsed_json_data["title"], "title")
        if "outline" in parsed_json_data:
            for heading_index, heading_item in enumerate(parsed_json_data["outline"]):
                if "text" in heading_item:
                    recursive_text_field_validation(heading_item["text"], f"outline[{heading_index}].text")
        if "extracted_sections" in parsed_json_data:
            for section_index, section_item in enumerate(parsed_json_data["extracted_sections"]):
                if "section_title" in section_item:
                    recursive_text_field_validation(section_item["section_title"], f"extracted_sections[{section_index}].section_title")
        if comprehensive_validation_results["total_texts"] > 0:
            comprehensive_validation_results["accuracy"] = comprehensive_validation_results["valid_texts"] / comprehensive_validation_results["total_texts"]
        else:
            comprehensive_validation_results["accuracy"] = 0.0
        return comprehensive_validation_results

def execute_multilingual_validation_pipeline():
    command_line_argument_parser = argparse.ArgumentParser(description="Validate multilingual text correctness")
    command_line_argument_parser.add_argument("--input_dir", type=str, default="output_1A",
                       help="Directory containing JSON files to validate")
    command_line_argument_parser.add_argument("--output_file", type=str, default="multilingual_validation_report.json",
                       help="Output file for validation report")
    command_line_argument_parser.add_argument("--detailed", action="store_true",
                       help="Show detailed validation results")  
    parsed_arguments = command_line_argument_parser.parse_args()
    text_integrity_validator = TextEncodingIntegrityChecker()
    print("🔍 Multilingual Text Validation")
    print("=" * 40)
    comprehensive_validation_results = []
    total_processed_files = 0
    total_detected_issues = 0
    if os.path.exists(parsed_arguments.input_dir):
        for json_filename in os.listdir(parsed_arguments.input_dir):
            if json_filename.endswith('.json'):
                complete_file_path = os.path.join(parsed_arguments.input_dir, json_filename)
                print(f"\n📄 Validating: {json_filename}")
                file_validation_result = text_integrity_validator.perform_comprehensive_json_file_validation(complete_file_path)
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
                    if parsed_arguments.detailed:
                        for integrity_issue in file_validation_result['issues'][:3]:  # Show first 3 issues
                            print(f"      * {integrity_issue['field']}: {integrity_issue['text']}")
                            for corruption_detail in integrity_issue['garbled_info']['issues'][:2]:
                                print(f"        - {corruption_detail['type']}: {corruption_detail['description']}")
    validation_summary_report = {
        "total_files_processed": total_processed_files,
        "total_issues_found": total_detected_issues,
        "files_with_issues": len([validation_result for validation_result in comprehensive_validation_results if validation_result.get('garbled_texts', 0) > 0]),
        "overall_accuracy": sum(validation_result.get('accuracy', 0) for validation_result in comprehensive_validation_results) / len(comprehensive_validation_results) if comprehensive_validation_results else 0,
        "detailed_results": comprehensive_validation_results
    }
    with open(parsed_arguments.output_file, 'w', encoding='utf-8') as report_output_file:
        json.dump(validation_summary_report, report_output_file, ensure_ascii=False, indent=2)
    print(f"\n📊 Summary:")
    print(f"  - Files processed: {total_processed_files}")
    print(f"  - Files with issues: {validation_summary_report['files_with_issues']}")
    print(f"  - Total issues found: {total_detected_issues}")
    print(f"  - Overall accuracy: {validation_summary_report['overall_accuracy']:.3f}")
    print(f"  - Detailed report saved to: {parsed_arguments.output_file}")
    if validation_summary_report['files_with_issues'] > 0:
        print(f"\n⚠️  Files with multilingual issues:")
        for validation_result in comprehensive_validation_results:
            if validation_result.get('garbled_texts', 0) > 0:
                print(f"  - {os.path.basename(validation_result['file'])}: {validation_result['garbled_texts']} issues")

if __name__ == "__main__":
    execute_multilingual_validation_pipeline() 