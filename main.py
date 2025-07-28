import os
import sys
import json

# Add src directory to path for modular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Modular imports
from document_processing.structure_extractor import DocumentStructureExtractor
from r1b_document_intelligence import execute_advanced_document_intelligence_pipeline

def process_document_outline_extraction(source_directory, target_directory):
    """Executes Round 1A logic: Extracts outline and tables for all PDFs."""
    print("Executing Round 1A: Outline Extraction...")
    os.makedirs(target_directory, exist_ok=True)
    
    # Initialize the modular extractor
    structure_extractor = DocumentStructureExtractor(debug=True)
    
    for document_filename in os.listdir(source_directory):
        if document_filename.lower().endswith(".pdf"):
            pdf_document_path = os.path.join(source_directory, document_filename)
            json_output_filename = document_filename.replace(".pdf", ".json")
            json_output_path = os.path.join(target_directory, json_output_filename)
            try:
                print(f"Processing: {document_filename}")
                extraction_result = structure_extractor.extract_document_structure_and_metadata(pdf_document_path)
                with open(json_output_path, 'w', encoding='utf-8') as file_handle:
                    json.dump(extraction_result, file_handle, ensure_ascii=False, indent=2)
                print(f"R1A: Generated {json_output_path}")
            except Exception as processing_error:
                print(f"R1A Error processing {pdf_document_path}: {processing_error}")

def load_configuration_file_content(file_path, fallback_content):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file_handle:
            return file_handle.read().strip()
    return fallback_content

def process_persona_driven_intelligence(source_directory, target_directory):
    """Executes Round 1B logic: Persona-based document intelligence using semantic search."""
    print("Executing Round 1B: Persona-Driven Document Intelligence...")
    os.makedirs(target_directory, exist_ok=True)
    
    # Initialize the modular extractor
    structure_extractor = DocumentStructureExtractor(debug=True)
    
    persona_config_path = os.path.join(source_directory, 'persona.txt')
    job_config_path = os.path.join(source_directory, 'job.txt')
    researcher_persona_definition = load_configuration_file_content(persona_config_path, "PhD Researcher in Computational Biology")
    research_task_description = load_configuration_file_content(job_config_path, "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks")
    available_pdf_documents = [os.path.join(source_directory, document_file) for document_file in os.listdir(source_directory) if document_file.lower().endswith(".pdf")]
    for pdf_document_path in available_pdf_documents:
        cached_outline_path = os.path.join(target_directory, os.path.basename(pdf_document_path).replace('.pdf', '.json'))
        if os.path.exists(cached_outline_path):
            with open(cached_outline_path, 'r', encoding='utf-8') as file_handle:
                document_outline_data = json.load(file_handle)
            print(f"R1B: Loaded cached R1A outline for {pdf_document_path}")
        else:
            document_outline_data = structure_extractor.extract_document_structure_and_metadata(pdf_document_path)
            with open(cached_outline_path, 'w', encoding='utf-8') as file_handle:
                json.dump(document_outline_data, file_handle, ensure_ascii=False, indent=2)
            print(f"R1B: Extracted and cached R1A outline for {pdf_document_path}")
        document_collection_info = [{"path": pdf_document_path, "r1a_outline": document_outline_data}]
        intelligence_analysis_result = execute_advanced_document_intelligence_pipeline(document_collection_info, researcher_persona_definition, research_task_description)
        intelligence_output_path = os.path.join(target_directory, f"r1_{os.path.basename(pdf_document_path).replace('.pdf', '.json')}")
        with open(intelligence_output_path, 'w', encoding='utf-8') as file_handle:
            json.dump(intelligence_analysis_result, file_handle, ensure_ascii=False, indent=2)
        print(f"R1B: Generated output at {intelligence_output_path}")

if __name__ == "__main__":
    source_input_directory = os.environ.get("INPUT_DIR", "input")
    target_output_directory = os.environ.get("OUTPUT_DIR", "output")
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--round" and sys.argv[2].upper() == "R1A":
        process_document_outline_extraction(source_input_directory, target_output_directory)
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "--round" and sys.argv[2].upper() == "R1B":
        process_persona_driven_intelligence(source_input_directory, target_output_directory)
    else:
        print("No specific round specified. Attempting to run R1B logic which incorporates R1A functionality.")
        process_persona_driven_intelligence(source_input_directory, target_output_directory)
