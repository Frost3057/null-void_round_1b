#!/usr/bin/env python3
"""
Multilingual Text Validation Script
Validates multilingual text correctness and encoding integrity.
"""

import sys
import os
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation.text_integrity import MultilingualValidationPipeline


def main():
    """Main function for multilingual text validation."""
    command_line_argument_parser = argparse.ArgumentParser(
        description="Validate multilingual text correctness and encoding integrity"
    )
    command_line_argument_parser.add_argument(
        "--input_dir", 
        type=str, 
        default="output_1A",
        help="Directory containing JSON files to validate"
    )
    command_line_argument_parser.add_argument(
        "--output_file", 
        type=str, 
        default="multilingual_validation_report.json",
        help="Output file for validation report"
    )
    command_line_argument_parser.add_argument(
        "--detailed", 
        action="store_true",
        help="Show detailed validation results"
    )
    
    parsed_arguments = command_line_argument_parser.parse_args()
    
    # Initialize validation pipeline
    validation_pipeline = MultilingualValidationPipeline()
    
    # Perform validation
    validation_results = validation_pipeline.validate_directory(
        parsed_arguments.input_dir, 
        parsed_arguments.detailed
    )
    
    # Save validation report
    validation_pipeline.save_validation_report(
        validation_results, 
        parsed_arguments.output_file
    )


if __name__ == "__main__":
    main()
