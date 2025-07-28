import os
import sys
import subprocess
import json
import argparse
from datetime import datetime

def execute_shell_command_with_logging(shell_command: str, operation_description: str) -> bool:
    print(f"\n🔄 {operation_description}")
    print(f"Command: {shell_command}")
    print("-" * 50)
    try:
        command_execution_result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
        if command_execution_result.returncode == 0:
            print("✅ Success")
            if command_execution_result.stdout:
                print("Output:", command_execution_result.stdout[:500] + "..." if len(command_execution_result.stdout) > 500 else command_execution_result.stdout)
            return True
        else:
            print("❌ Failed")
            if command_execution_result.stderr:
                print("Error:", command_execution_result.stderr)
            return False
    except Exception as execution_error:
        print(f"❌ Exception: {execution_error}")
        return False

def validate_system_prerequisites():
    print("🔍 Checking Dependencies")
    print("=" * 30)  
    essential_script_files = [
        "r1a_outline_extractor.py",
        "r1b_document_intelligence.py",
        "evaluate_accuracy.py",
        "validate_multilingual.py"
    ]
    absent_required_files = []
    for script_filename in essential_script_files:
        if not os.path.exists(script_filename):
            absent_required_files.append(script_filename)
    if absent_required_files:
        print(f"❌ Missing files: {absent_required_files}")
        return False
    print("✅ All required files found")
    return True

def execute_round1a_comprehensive_evaluation():
    print("\n📊 Round 1A Evaluation")
    print("=" * 30)
    if not execute_shell_command_with_logging("python r1a_outline_extractor.py", "Running R1A outline extraction"):
        return False
    if not execute_shell_command_with_logging("python validate_multilingual.py --input_dir output_1A --detailed", 
                      "Validating multilingual text correctness"):
        return False
    if not execute_shell_command_with_logging("python evaluate_accuracy.py --mode r1a --detailed", 
                      "Evaluating R1A accuracy"):
        return False
    return True

def execute_round1b_comprehensive_evaluation():
    print("\n📊 Round 1B Evaluation")
    print("=" * 30)
    if not execute_shell_command_with_logging("python r1b_document_intelligence.py", "Running R1B document intelligence"):
        return False
    if not execute_shell_command_with_logging("python validate_multilingual.py --input_dir output_1B --detailed", 
                      "Validating multilingual text correctness"):
        return False
    if not execute_shell_command_with_logging("python evaluate_accuracy.py --mode r1b --detailed", 
                      "Evaluating R1B accuracy"):
        return False
    return True

def compile_comprehensive_evaluation_report():
    print("\n📋 Generating Evaluation Report")
    print("=" * 30)
    evaluation_summary_report = {
        "timestamp": datetime.now().isoformat(),
        "evaluation_summary": {},
        "r1a_results": {},
        "r1b_results": {},
        "multilingual_validation": {},
        "recommendations": []
    }
    r1a_output_files = [output_filename for output_filename in os.listdir("output_1A") if output_filename.endswith('.json')]
    evaluation_summary_report["r1a_results"]["files_processed"] = len(r1a_output_files)
    identified_problematic_files = []
    for output_filename in r1a_output_files:
        output_file_path = os.path.join("output_1A", output_filename)
        try:
            with open(output_file_path, 'r', encoding='utf-8') as file_handle:
                parsed_data = json.load(file_handle)
                if not parsed_data.get("outline") or len(parsed_data["outline"]) == 0:
                    identified_problematic_files.append(f"{output_filename}: No headings detected")
                if not parsed_data.get("title") or len(parsed_data["title"]) == 0:
                    identified_problematic_files.append(f"{output_filename}: No title detected")
        except Exception as file_processing_error:
            identified_problematic_files.append(f"{output_filename}: Error reading file - {file_processing_error}")
    
    evaluation_summary_report["r1a_results"]["problematic_files"] = identified_problematic_files
    r1b_output_files = [output_filename for output_filename in os.listdir("output_1B") if output_filename.endswith('.json')]
    evaluation_summary_report["r1b_results"]["files_processed"] = len(r1b_output_files)
    improvement_recommendations = []
    if identified_problematic_files:
        improvement_recommendations.append("Fix heading detection in problematic R1A files")
    if len(r1a_output_files) == 0:
        improvement_recommendations.append("No R1A output files found - check input_1A directory")
    if len(r1b_output_files) == 0:
        improvement_recommendations.append("No R1B output files found - check input_1B directory")
    try:
        with open("multilingual_validation_report.json", 'r', encoding='utf-8') as validation_file_handle:
            multilingual_validation_data = json.load(validation_file_handle)
            if multilingual_validation_data.get("files_with_issues", 0) > 0:
                improvement_recommendations.append("Fix multilingual text encoding issues")
    except FileNotFoundError:
        improvement_recommendations.append("Run multilingual validation to check for encoding issues")
    evaluation_summary_report["recommendations"] = improvement_recommendations
    with open("evaluation_report.json", 'w', encoding='utf-8') as report_output_file:
        json.dump(evaluation_summary_report, report_output_file, ensure_ascii=False, indent=2)
    print("✅ Evaluation report saved to: evaluation_report.json")
    print(f"\n📊 Evaluation Summary:")
    print(f"  - R1A files processed: {evaluation_summary_report['r1a_results']['files_processed']}")
    print(f"  - R1B files processed: {evaluation_summary_report['r1b_results']['files_processed']}")
    print(f"  - Problematic files: {len(identified_problematic_files)}")
    print(f"  - Recommendations: {len(improvement_recommendations)}")
    if improvement_recommendations:
        print(f"\n💡 Recommendations:")
        for recommendation_item in improvement_recommendations:
            print(f"  - {recommendation_item}")

def orchestrate_evaluation_pipeline_execution():
    command_line_parser = argparse.ArgumentParser(description="Run complete evaluation pipeline")
    command_line_parser.add_argument("--mode", choices=["r1a", "r1b", "both"], default="both",
                       help="Evaluation mode")
    command_line_parser.add_argument("--create-ground-truth", action="store_true",
                       help="Create ground truth templates")
    command_line_parser.add_argument("--skip-extraction", action="store_true",
                       help="Skip PDF extraction, only run evaluation")
    parsed_command_arguments = command_line_parser.parse_args()
    print("🚀 Adobe Hackathon Evaluation Pipeline")
    print("=" * 50)
    print(f"Mode: {parsed_command_arguments.mode}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not validate_system_prerequisites():
        print("❌ Dependencies check failed. Exiting.")
        sys.exit(1)
    if parsed_command_arguments.create_ground_truth:
        print("\n📝 Creating Ground Truth Templates")
        execute_shell_command_with_logging("python create_ground_truth.py --mode both", "Creating ground truth templates")
    pipeline_execution_success = True
    if parsed_command_arguments.mode in ["r1a", "both"] and not parsed_command_arguments.skip_extraction:
        pipeline_execution_success &= execute_round1a_comprehensive_evaluation()
    if parsed_command_arguments.mode in ["r1b", "both"] and not parsed_command_arguments.skip_extraction:
        pipeline_execution_success &= execute_round1b_comprehensive_evaluation()
    compile_comprehensive_evaluation_report()
    if pipeline_execution_success:
        print("\n✅ Evaluation pipeline completed successfully!")
    else:
        print("\n❌ Evaluation pipeline completed with errors!")
        sys.exit(1)

if __name__ == "__main__":
    orchestrate_evaluation_pipeline_execution() 