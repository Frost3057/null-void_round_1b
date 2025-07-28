#!/usr/bin/env python3
"""
Document Structure Extraction Script
Extracts hierarchical document structures from multilingual PDFs.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_processing.structure_extractor import DocumentStructureExtractor
import json


def main():
    """Main function to process PDF documents and extract structure."""
    input_directory = "input_1A"
    output_directory = "output_1A"
    
    print("🔍 Document Structure Extraction")
    print("=" * 40)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Initialize the structure extractor
    extractor = DocumentStructureExtractor(debug=True)
    
    # Process all PDF files in input directory
    if os.path.exists(input_directory):
        for pdf_filename in os.listdir(input_directory):
            if pdf_filename.lower().endswith('.pdf'):
                pdf_document_path = os.path.join(input_directory, pdf_filename)
                json_output_filename = pdf_filename.replace('.pdf', '.json')
                json_output_path = os.path.join(output_directory, json_output_filename)
                
                print(f"\\n📄 Processing: {pdf_filename}")
                
                try:
                    # Extract document structure
                    extraction_result = extractor.extract_document_structure_and_metadata(pdf_document_path)
                    
                    # Save result to JSON file
                    with open(json_output_path, 'w', encoding='utf-8') as file_handle:
                        json.dump(extraction_result, file_handle, ensure_ascii=False, indent=2)
                    
                    print(f"✅ Generated: {json_output_path}")
                    print(f"   - Headings: {len(extraction_result.get('outline', []))}")
                    print(f"   - Tables: {len(extraction_result.get('tables', []))}")
                    print(f"   - Pages: {extraction_result.get('metadata', {}).get('page_count', 0)}")
                    
                except Exception as processing_error:
                    print(f"❌ Error processing {pdf_document_path}: {processing_error}")
    else:
        print(f"❌ Input directory '{input_directory}' not found")
        print("Please ensure PDF files are placed in the input_1A directory")


if __name__ == "__main__":
    main()
