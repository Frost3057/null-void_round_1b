import json
import os
import argparse
import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import numpy as np
import unicodedata

class TextLanguageAnalyzer:
    def __init__(self):
        self.devanagari_unicode_range = range(0x0900, 0x097F + 1)
        self.english_alphabet_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
    def validate_devanagari_text(self, input_text: str) -> bool:
        if not input_text:
            return True
        contains_devanagari = any(ord(char) in self.devanagari_unicode_range for char in input_text)
        contains_english = any(char in self.english_alphabet_chars for char in input_text)
        return contains_devanagari or contains_english
    
    def analyze_script_composition(self, input_text: str) -> Dict[str, bool]:
        if not input_text:
            return {"en": False, "hi": False, "mr": False}
        devanagari_char_count = sum(1 for char in input_text if ord(char) in self.devanagari_unicode_range)
        english_char_count = sum(1 for char in input_text if char in self.english_alphabet_chars)
        total_alphabetic_chars = len([char for char in input_text if char.isalpha()])
        return {
            "en": english_char_count > 0,
            "hi": devanagari_char_count > 0,
            "mr": devanagari_char_count > 0
        }

def compute_performance_metrics(correct_predictions: int, incorrect_predictions: int, missed_predictions: int) -> Dict[str, float]:
    precision = correct_predictions / (correct_predictions + incorrect_predictions) if (correct_predictions + incorrect_predictions) > 0 else 0.0
    recall = correct_predictions / (correct_predictions + missed_predictions) if (correct_predictions + missed_predictions) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score
    }

class HeadingExtractionEvaluator:
    def __init__(self):
        self.language_analyzer = TextLanguageAnalyzer()
    def load_reference_data(self, reference_data_directory: str) -> Dict[str, Dict]:
        reference_annotations = {}
        if not os.path.exists(reference_data_directory):
            print(f"[WARNING] Ground truth directory {reference_data_directory} not found")
            return reference_annotations
        for filename in os.listdir(reference_data_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(reference_data_directory, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file_handle:
                        reference_annotations[filename] = json.load(file_handle)
                except Exception as error:
                    print(f"[ERROR] Could not load ground truth {file_path}: {error}")
        return reference_annotations
    
    def assess_heading_extraction_quality(self, prediction_file: str, reference_data: Dict = None) -> Dict[str, Any]:
        try:
            with open(prediction_file, 'r', encoding='utf-8') as file_handle:
                extraction_result = json.load(file_handle)
        except Exception as error:
            print(f"[ERROR] Could not load output file {prediction_file}: {error}")
            return {"error": str(error)}
        extracted_headings = []
        for heading_item in extraction_result.get("outline", []):
            if isinstance(heading_item.get("text"), dict):
                for language_code, heading_text in heading_item["text"].items():
                    extracted_headings.append({
                        "level": heading_item.get("level", "H1"),
                        "text": heading_text,
                        "page": heading_item.get("page", 1),
                        "lang": language_code
                    })
            else:
                extracted_headings.append({
                    "level": heading_item.get("level", "H1"),
                    "text": str(heading_item.get("text", "")),
                    "page": heading_item.get("page", 1),
                    "lang": "en"
                })
        text_quality_issues = []
        for heading_item in extracted_headings:
            heading_text = heading_item["text"]
            if not self.language_analyzer.validate_devanagari_text(heading_text):
                text_quality_issues.append({
                    "heading": heading_item,
                    "issue": "Invalid Devanagari characters or garbled text"
                })
        evaluation_metrics = {
            "total_headings": len(extracted_headings),
            "multilingual_issues": len(text_quality_issues),
            "multilingual_issues_details": text_quality_issues,
            "title_detected": bool(extraction_result.get("title")),
            "title_languages": list(extraction_result.get("title", {}).keys()) if extraction_result.get("title") else []
        }  
        if reference_data:
            reference_headings = reference_data.get("outline", [])
            correct_predictions = 0
            incorrect_predictions = len(extracted_headings)
            missed_predictions = len(reference_headings)
            for predicted_heading in extracted_headings:
                for reference_heading in reference_headings:
                    if (predicted_heading["text"].lower().strip() == reference_heading["text"].lower().strip() and
                        predicted_heading["level"] == reference_heading["level"]):
                        correct_predictions += 1
                        incorrect_predictions -= 1
                        missed_predictions -= 1
                        break
            evaluation_metrics.update(compute_performance_metrics(correct_predictions, incorrect_predictions, missed_predictions))
            evaluation_metrics.update({
                "true_positives": correct_predictions,
                "false_positives": incorrect_predictions,
                "false_negatives": missed_predictions
            })
        return evaluation_metrics
    
    def validate_multilingual_text_quality(self, prediction_file: str) -> Dict[str, Any]:
        try:
            with open(prediction_file, 'r', encoding='utf-8') as file_handle:
                extraction_result = json.load(file_handle)
        except Exception as error:
            return {"error": str(error)}
        text_quality_issues = []
        total_text_elements = 0
        valid_text_elements = 0
        document_title = extraction_result.get("title", {})
        for language_code, title_text in document_title.items():
            total_text_elements += 1
            if self.language_analyzer.validate_devanagari_text(title_text):
                valid_text_elements += 1
            else:
                text_quality_issues.append({
                    "type": "title",
                    "lang": language_code,
                    "text": title_text,
                    "issue": "Invalid or garbled text"
                })
        for heading_item in extraction_result.get("outline", []):
            if isinstance(heading_item.get("text"), dict):
                for language_code, heading_text in heading_item["text"].items():
                    total_text_elements += 1
                    if self.language_analyzer.validate_devanagari_text(heading_text):
                        valid_text_elements += 1
                    else:
                        text_quality_issues.append({
                            "type": "heading",
                            "level": heading_item.get("level"),
                            "lang": language_code,
                            "text": heading_text,
                            "issue": "Invalid or garbled text"
                        })
        return {
            "total_texts": total_text_elements,
            "valid_texts": valid_text_elements,
            "invalid_texts": len(text_quality_issues),
            "accuracy": valid_text_elements / total_text_elements if total_text_elements > 0 else 0.0,
            "issues": text_quality_issues
        }

class DocumentIntelligenceEvaluator:
    def __init__(self):
        self.language_analyzer = TextLanguageAnalyzer()
    def assess_semantic_relevance_quality(self, prediction_file: str, target_persona: str, target_job_description: str) -> Dict[str, Any]:
        try:
            with open(prediction_file, 'r', encoding='utf-8') as file_handle:
                extraction_result = json.load(file_handle)
        except Exception as error:
            return {"error": str(error)}
        extracted_sections = extraction_result.get("extracted_sections", [])
        sub_section_analysis = extraction_result.get("sub_section_analysis", [])
        relevance_scores = []
        text_quality_issues = []
        for section_item in extracted_sections:
            section_title_data = section_item.get("section_title", {})
            for language_code, title_text in section_title_data.items():
                if not self.language_analyzer.validate_devanagari_text(title_text):
                    text_quality_issues.append({
                        "section": section_item,
                        "lang": language_code,
                        "text": title_text,
                        "issue": "Invalid or garbled text"
                    })
        relevance_quality_metrics = {
            "total_sections": len(extracted_sections),
            "top_5_relevance": len(extracted_sections[:5]),
            "multilingual_issues": len(text_quality_issues),
            "multilingual_issues_details": text_quality_issues
        }
        domain_relevant_keywords = ["gnn", "drug", "discovery", "molecular", "neural", "biology", "computational"]
        keyword_match_count = 0
        for section_item in extracted_sections:
            combined_section_text = " ".join(section_item.get("section_title", {}).values()).lower()
            if any(keyword in combined_section_text for keyword in domain_relevant_keywords):
                keyword_match_count += 1
        relevance_quality_metrics["keyword_matches"] = keyword_match_count
        relevance_quality_metrics["keyword_accuracy"] = keyword_match_count / len(extracted_sections) if extracted_sections else 0.0
        return relevance_quality_metrics
    
    def analyze_bilingual_content_detection(self, prediction_file: str) -> Dict[str, Any]:
        """Evaluate bilingual text detection and preservation"""
        try:
            with open(prediction_file, 'r', encoding='utf-8') as file_handle:
                extraction_result = json.load(file_handle)
        except Exception as error:
            return {"error": str(error)}
        
        extracted_sections = extraction_result.get("extracted_sections", [])
        sub_section_analysis = extraction_result.get("sub_section_analysis", [])
        
        bilingual_content_sections = 0
        english_only_sections = 0
        devanagari_only_sections = 0
        total_analyzed_sections = len(extracted_sections)
        
        for section_item in extracted_sections:
            section_title_data = section_item.get("section_title", {})
            language_composition = self.language_analyzer.analyze_script_composition(" ".join(section_title_data.values()))
            
            if language_composition["en"] and (language_composition["hi"] or language_composition["mr"]):
                bilingual_content_sections += 1
            elif language_composition["en"]:
                english_only_sections += 1
            elif language_composition["hi"] or language_composition["mr"]:
                devanagari_only_sections += 1
        
        return {
            "total_sections": total_analyzed_sections,
            "bilingual_sections": bilingual_content_sections,
            "english_only": english_only_sections,
            "devangari_only": devanagari_only_sections,
            "bilingual_percentage": bilingual_content_sections / total_analyzed_sections if total_analyzed_sections > 0 else 0.0
        }

def run_evaluation_pipeline():
    argument_parser = argparse.ArgumentParser(description="Evaluate Round 1A and Round 1B accuracy")
    argument_parser.add_argument("--mode", choices=["r1a", "r1b", "both"], default="both", 
                       help="Evaluation mode")
    argument_parser.add_argument("--ground_truth_dir", type=str, default="ground_truth",
                       help="Directory containing ground truth annotations")
    argument_parser.add_argument("--output_1a_dir", type=str, default="output_1A",
                       help="Directory containing R1A outputs")
    argument_parser.add_argument("--output_1b_dir", type=str, default="output_1B",
                       help="Directory containing R1B outputs")
    argument_parser.add_argument("--detailed", action="store_true",
                       help="Show detailed evaluation results")
    
    command_args = argument_parser.parse_args()
    
    print("🔍 Adobe Hackathon Evaluation Pipeline")
    print("=" * 50)
    
    if command_args.mode in ["r1a", "both"]:
        print("\n📊 Evaluating Round 1A (Heading Detection)")
        print("-" * 40)
        
        heading_evaluator = HeadingExtractionEvaluator()
        reference_annotations = heading_evaluator.load_reference_data(command_args.ground_truth_dir)
        
        r1a_prediction_files = [filename for filename in os.listdir(command_args.output_1a_dir) if filename.endswith('.json')]
        
        for prediction_filename in r1a_prediction_files:
            prediction_file_path = os.path.join(command_args.output_1a_dir, prediction_filename)
            print(f"\n📄 Evaluating: {prediction_filename}")
            
            # Get corresponding ground truth
            reference_data_key = prediction_filename
            reference_data = reference_annotations.get(reference_data_key, {})
            
            # Evaluate heading detection
            heading_quality_metrics = heading_evaluator.assess_heading_extraction_quality(prediction_file_path, reference_data)
            
            # Evaluate multilingual correctness
            text_quality_metrics = heading_evaluator.validate_multilingual_text_quality(prediction_file_path)
            
            # Print results
            print(f"  📈 Heading Detection:")
            print(f"    - Total headings: {heading_quality_metrics.get('total_headings', 0)}")
            print(f"    - Title detected: {heading_quality_metrics.get('title_detected', False)}")
            print(f"    - Title languages: {heading_quality_metrics.get('title_languages', [])}")
            
            if 'precision' in heading_quality_metrics:
                print(f"    - Precision: {heading_quality_metrics['precision']:.3f}")
                print(f"    - Recall: {heading_quality_metrics['recall']:.3f}")
                print(f"    - F1 Score: {heading_quality_metrics['f1_score']:.3f}")
            
            print(f"  🌐 Multilingual Correctness:")
            print(f"    - Valid texts: {text_quality_metrics.get('valid_texts', 0)}/{text_quality_metrics.get('total_texts', 0)}")
            print(f"    - Accuracy: {text_quality_metrics.get('accuracy', 0):.3f}")
            
            if text_quality_metrics.get('issues'):
                print(f"    - Issues found: {len(text_quality_metrics['issues'])}")
                if command_args.detailed:
                    for quality_issue in text_quality_metrics['issues'][:3]:  # Show first 3 issues
                        print(f"      * {quality_issue['type']} ({quality_issue['lang']}): {quality_issue['text'][:50]}...")
    
    if command_args.mode in ["r1b", "both"]:
        print("\n📊 Evaluating Round 1B (Document Intelligence)")
        print("-" * 40)
        
        document_intelligence_evaluator = DocumentIntelligenceEvaluator()
        
        r1b_prediction_files = [filename for filename in os.listdir(command_args.output_1b_dir) if filename.endswith('.json')]
        
        for prediction_filename in r1b_prediction_files:
            prediction_file_path = os.path.join(command_args.output_1b_dir, prediction_filename)
            print(f"\n📄 Evaluating: {prediction_filename}")
            
            # Evaluate semantic relevance
            relevance_quality_metrics = document_intelligence_evaluator.assess_semantic_relevance_quality(
                prediction_file_path, 
                "PhD Researcher in Computational Biology",
                "Review GNNs for drug discovery"
            )
            
            # Evaluate bilingual detection
            bilingual_analysis_metrics = document_intelligence_evaluator.analyze_bilingual_content_detection(prediction_file_path)
            
            # Print results
            print(f"  🎯 Semantic Relevance:")
            print(f"    - Total sections: {relevance_quality_metrics.get('total_sections', 0)}")
            print(f"    - Keyword matches: {relevance_quality_metrics.get('keyword_matches', 0)}")
            print(f"    - Keyword accuracy: {relevance_quality_metrics.get('keyword_accuracy', 0):.3f}")
            
            print(f"  🌐 Bilingual Detection:")
            print(f"    - Bilingual sections: {bilingual_analysis_metrics.get('bilingual_sections', 0)}")
            print(f"    - English only: {bilingual_analysis_metrics.get('english_only', 0)}")
            print(f"    - Devanagari only: {bilingual_analysis_metrics.get('devangari_only', 0)}")
            print(f"    - Bilingual percentage: {bilingual_analysis_metrics.get('bilingual_percentage', 0):.3f}")
            
            if relevance_quality_metrics.get('multilingual_issues'):
                print(f"    - Multilingual issues: {relevance_quality_metrics['multilingual_issues']}")
    
    print("\n✅ Evaluation Complete!")
    print("\n📋 Summary:")
    print("- Check for garbled Unicode in Devanagari text")
    print("- Verify heading detection accuracy")
    print("- Assess semantic relevance for R1B")
    print("- Monitor bilingual content preservation")

if __name__ == "__main__":
    run_evaluation_pipeline() 