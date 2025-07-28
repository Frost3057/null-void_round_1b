import os
import json
import time
import fitz
import pdfplumber
from langdetect import detect
import numpy as np
from r1a_outline_extractor import extract_document_structure_and_metadata

def validate_character_encoding_integrity(input_text, language_code):
    if language_code in ['hi', 'mr']:
        return not any('\u0900' <= character <= '\u097F' for character in input_text)
    return False

def identify_text_language(input_text):
    try:
        detected_language = detect(input_text)
        if detected_language in ['hi', 'mr', 'en']:
            return detected_language
    except Exception:
        pass
    return 'en'

def extract_page_text_content(document_page, pdf_document_path, page_index):
    extracted_text = document_page.get_text("text", flags=11)
    detected_language = identify_text_language(extracted_text)
    if validate_character_encoding_integrity(extracted_text, detected_language):
        try:
            with pdfplumber.open(pdf_document_path) as pdf_document:
                extracted_text = pdf_document.pages[page_index].extract_text() or ""
                detected_language = identify_text_language(extracted_text)
        except Exception:
            extracted_text = ""
    return extracted_text, detected_language

def check_section_relevance_against_keywords(input_text, keyword_list):
    lowercase_text = input_text.lower()
    return any(keyword in lowercase_text for keyword in keyword_list)

def compute_basic_relevance_score(input_text, persona_keyword_set, job_description_keywords):
    lowercase_text = input_text.lower()
    calculated_score = 0.0
    for persona_keyword in persona_keyword_set:
        if persona_keyword.lower() in lowercase_text:
            calculated_score += 1.0
    for job_keyword in job_description_keywords:
        if job_keyword.lower() in lowercase_text:
            calculated_score += 2.0
    if len(input_text) > 0:
        calculated_score = calculated_score / (len(input_text.split()) + 1)  
    return calculated_score

def execute_simplified_document_intelligence_pipeline():
    source_input_directory = "input_1B"
    target_output_directory = "output_1B"
    os.makedirs(target_output_directory, exist_ok=True)
    available_pdf_documents = [os.path.join(source_input_directory, document_file) for document_file in os.listdir(source_input_directory) if document_file.lower().endswith(".pdf")]
    persona_configuration_path = os.path.join(source_input_directory, 'persona.txt')
    job_description_path = os.path.join(source_input_directory, 'job.txt')
    researcher_persona_definition = "PhD Researcher in Computational Biology"
    research_task_description = "Review GNNs for drug discovery"
    if os.path.exists(persona_configuration_path):
        with open(persona_configuration_path, 'r', encoding='utf-8') as file_handle:
            researcher_persona_definition = file_handle.read().strip()
    if os.path.exists(job_description_path):
        with open(job_description_path, 'r', encoding='utf-8') as file_handle:
            research_task_description = file_handle.read().strip()
    persona_related_keywords = ["phd", "researcher", "computational", "biology", "research", "scientist"]
    job_domain_keywords = ["gnn", "drug", "discovery", "molecular", "neural", "graph", "network", "machine learning", "ai"]
    relevance_filter_keywords = ["gnn", "drug discovery", "molecular", "neural", "biology"]
    keyword_filtering_enabled = False
    all_extracted_sections = []
    document_metadata_collection = []
    for pdf_document_path in available_pdf_documents:
        document_outline_data = extract_document_structure_and_metadata(pdf_document_path)
        document_outline_structure = document_outline_data.get("outline", [])
        print(f"\n[DEBUG] Outline for {pdf_document_path}: {document_outline_structure}")
        if not document_outline_structure:
            print(f"[WARNING] No outline/headings found in {pdf_document_path}!")
        pdf_document = fitz.open(pdf_document_path)
        page_text_collection = []
        page_language_collection = []
        for page_index, document_page in enumerate(pdf_document):
            extracted_text, detected_language = extract_page_text_content(document_page, pdf_document_path, page_index)
            print(f"[DEBUG] Page {page_index+1} ({detected_language}): {extracted_text[:200]}")
            page_text_collection.append(extracted_text)
            page_language_collection.append(detected_language)
        
        for outline_entry in document_outline_structure:
            page_number = outline_entry["page"]
            section_heading_data = outline_entry["text"]
            section_title_dictionary = {}
            refined_content_dictionary = {}
            if isinstance(section_heading_data, dict):
                for language_code, heading_text in section_heading_data.items():
                    page_content = page_text_collection[page_number-1] if page_number-1 < len(page_text_collection) else ""
                    if not page_content:
                        continue
                    if identify_text_language(page_content) == language_code or language_code == 'en':
                        text_position_index = page_content.find(heading_text)
                        if text_position_index == -1:
                            text_position_index = 0
                        extracted_paragraph = page_content[text_position_index:text_position_index+200].strip()
                        if extracted_paragraph:
                            section_title_dictionary[language_code] = heading_text
                            refined_content_dictionary[language_code] = extracted_paragraph
            else:
                page_content = page_text_collection[page_number-1] if page_number-1 < len(page_text_collection) else ""
                if page_content:
                    language_code = identify_text_language(page_content)
                    if language_code in ['en', 'hi', 'mr']:
                        text_position_index = page_content.find(str(section_heading_data))
                        if text_position_index == -1:
                            text_position_index = 0
                        extracted_paragraph = page_content[text_position_index:text_position_index+200].strip()
                        if extracted_paragraph:
                            section_title_dictionary[language_code] = str(section_heading_data)
                            refined_content_dictionary[language_code] = extracted_paragraph  
            print(f"[DEBUG] Section title: {section_title_dictionary}, Refined: {refined_content_dictionary}")
            if keyword_filtering_enabled and not check_section_relevance_against_keywords(" ".join(refined_content_dictionary.values()), relevance_filter_keywords):
                print(f"[DEBUG] Section filtered out by keywords: {section_title_dictionary}")
                continue
            if not refined_content_dictionary:
                print(f"[WARNING] No refined text found for section: {section_title_dictionary}")
                continue
            all_extracted_sections.append({
                "document": os.path.basename(pdf_document_path),
                "page_number": page_number,
                "section_title": section_title_dictionary,
                "refined_text": refined_content_dictionary
            })
        document_metadata_collection.append({"path": pdf_document_path, "r1a_outline": document_outline_data})
    if not all_extracted_sections:
        print("[WARNING] No sections found after extraction and filtering!")
    sections_with_relevance_scores = []
    for section_item in all_extracted_sections:
        combined_section_texts = []
        for language_code in section_item["section_title"]:
            combined_section_texts.append(section_item["section_title"][language_code])
        for language_code in section_item["refined_text"]:
            combined_section_texts.append(section_item["refined_text"][language_code])
        aggregated_section_text = " ".join(combined_section_texts)
        computed_relevance_score = compute_basic_relevance_score(aggregated_section_text, persona_related_keywords, job_domain_keywords)     
        sections_with_relevance_scores.append({
            **section_item,
            "relevance_score": computed_relevance_score
        })
    priority_ranked_sections = sorted(sections_with_relevance_scores, key=lambda section: section['relevance_score'], reverse=True)
    final_output_sections = []
    detailed_subsection_analysis = []
    for section_index, section_item in enumerate(priority_ranked_sections):
        final_output_sections.append({
            "document": section_item["document"],
            "page_number": section_item["page_number"],
            "section_title": section_item["section_title"],
            "importance_rank": section_index + 1
        })
        detailed_subsection_analysis.append({
            "document": section_item["document"],
            "page_number": section_item["page_number"],
            "refined_text": section_item["refined_text"]
        })
    final_analysis_result = {
        "metadata": {
            "input_documents": [os.path.basename(document_info['path']) for document_info in document_metadata_collection],
            "persona": researcher_persona_definition,
            "job_to_be_done": research_task_description,
            "processing_timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "note": "Simplified version without sentence transformers"
        },
        "extracted_sections": final_output_sections,
        "sub_section_analysis": detailed_subsection_analysis
    }
    json_output_path = os.path.join(target_output_directory, "r1b_output_simple.json")
    with open(json_output_path, 'w', encoding='utf-8') as output_file_handle:
        json.dump(final_analysis_result, output_file_handle, ensure_ascii=False, indent=2)
    print(f"Generated simplified R1B output: {json_output_path}")

if __name__ == "__main__":
    execute_simplified_document_intelligence_pipeline() 