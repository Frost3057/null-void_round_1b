import fitz
import pdfplumber
import json
import os
import re
from collections import Counter
from langdetect import detect
import wordninja

try:
    from indicnlp.tokenize import sentence_tokenize, indic_tokenize
    INDICNLP_AVAILABLE = True
except ImportError:
    INDICNLP_AVAILABLE = False
    print('[INFO] IndicNLP not available, using basic whitespace heuristics for Indian languages.')

DEBUG = False
def identify_text_language(input_text):
    try:
        detected_language = detect(input_text)
        if detected_language in ['hi', 'mr', 'en']:
            return detected_language
    except Exception:
        pass
    return 'en'

def normalize_english_text(input_text):
    if not input_text or ' ' in input_text:
        return input_text.strip()
    return ' '.join(wordninja.split(input_text)).strip()

def normalize_indic_script_text(input_text, language_code):
    if INDICNLP_AVAILABLE and language_code in ['hi', 'mr']:
        return ' '.join(indic_tokenize.trivial_tokenize(input_text, lang=language_code)).replace(' ।', '।').strip()
    return re.sub(r'([।,.!?])', r'\1 ', input_text).replace('  ', ' ').strip()

def validate_devanagari_script_integrity(input_text):
    return not any('\u0900' <= character <= '\u097F' for character in input_text)

def check_if_bold_formatting(text_span):
    return "bold" in text_span['font'].lower() or "bld" in text_span['font'].lower()

def sanitize_whitespace_in_text(input_text):
    return re.sub(r'\s+', ' ', input_text).strip()

def check_if_all_uppercase(input_text):
    return input_text.isupper() and len(input_text) > 2 and any(character.isalpha() for character in input_text)

def identify_repetitive_content_patterns(all_document_spans, total_page_count):
    page_text_collections = {}
    for text_span in all_document_spans:
        page_number = text_span['page']
        page_text_collections.setdefault(page_number, []).append(sanitize_whitespace_in_text(text_span['text']))
    text_frequency_counter = Counter()
    for page_number, text_elements in page_text_collections.items():
        for text_content in set(text_elements):
            text_frequency_counter[text_content] += 1
    repetition_threshold = max(2, int(total_page_count * 0.6))
    repetitive_content_set = set([text_content for text_content, occurrence_count in text_frequency_counter.items() if occurrence_count >= repetition_threshold and len(text_content) > 0 and len(text_content) < 80])
    return repetitive_content_set

def extract_tabular_data_from_document(pdf_document_path):
    extracted_tables = []
    try:
        with pdfplumber.open(pdf_document_path) as pdf_document:
            for page_index, document_page in enumerate(pdf_document.pages):
                page_table_collection = document_page.extract_tables()
                for table_data in page_table_collection:
                    if table_data and len(table_data) > 0 and len(table_data[0]) > 1:
                        table_column_headers = [sanitize_whitespace_in_text(column_header) for column_header in table_data[0] if column_header]
                        detected_language = identify_text_language(' '.join(table_column_headers))
                        if detected_language == 'en':
                            table_column_headers = [normalize_english_text(column_header) for column_header in table_column_headers]
                        else:
                            table_column_headers = [normalize_indic_script_text(column_header, detected_language) for column_header in table_column_headers]
                        table_row_data = [table_row for table_row in table_data[1:] if any(table_row)]
                        if table_column_headers:
                            extracted_tables.append({
                                "page": page_index + 1,
                                "headers": {detected_language: table_column_headers},
                                "data": table_row_data
                            })
    except Exception as extraction_error:
        print(f"[WARN] pdfplumber table extraction failed: {extraction_error}")
    return extracted_tables

def extract_document_structure_and_metadata(pdf_document_path):
    print(f"Reading PDF from: {pdf_document_path}")
    document_title = {}
    document_outline = []
    document_tables = []
    try:
        pdf_document = fitz.open(pdf_document_path)
    except Exception as document_error:
        print(f"[ERROR] Could not open PDF: {document_error}")
        return {"title": {}, "outline": [], "tables": []}
    total_page_count = len(pdf_document)
    all_document_spans = []
    body_text_font_sizes = []
    page_span_collections = {}
    devanagari_fallback_required = False
    for page_index, document_page in enumerate(pdf_document):
        try:
            text_block_collection = document_page.get_text("dict", flags=11)["blocks"]
        except Exception as page_error:
            print(f"[WARN] Could not extract text from page {page_index+1}: {page_error}")
            continue
        for text_block in text_block_collection:
            if text_block['type'] == 0:
                for text_line in text_block['lines']:
                    for text_span in text_line['spans']:
                        span_text_content = sanitize_whitespace_in_text(text_span['text'])
                        if not span_text_content:
                            continue
                        if validate_devanagari_script_integrity(span_text_content):
                            devanagari_fallback_required = True
                        span_metadata = {
                            "text": span_text_content,
                            "size": text_span['size'],
                            "font": text_span['font'],
                            "is_bold": check_if_bold_formatting(text_span),
                            "origin": text_span['origin'],
                            "bbox": text_span['bbox'],
                            "page": page_index + 1,
                            "is_heading_candidate": False
                        }
                        all_document_spans.append(span_metadata)
                        page_span_collections.setdefault(page_index + 1, []).append(span_metadata)
                        if 8 <= text_span['size'] <= 14:
                            body_text_font_sizes.append(text_span['size'])
    if body_text_font_sizes:
        calculated_median_body_font_size = sorted(body_text_font_sizes)[len(body_text_font_sizes) // 2]
    else:
        calculated_median_body_font_size = 12
    repetitive_content_patterns = identify_repetitive_content_patterns(all_document_spans, total_page_count)
    first_page_text_spans = [text_span for text_span in all_document_spans if text_span['page'] == 1 and text_span['text'] not in repetitive_content_patterns]
    maximum_font_size_found = 0
    potential_title_candidates = []
    for text_span in first_page_text_spans:
        if text_span['size'] > maximum_font_size_found:
            maximum_font_size_found = text_span['size']
            potential_title_candidates = [text_span['text']]
        elif text_span['size'] == maximum_font_size_found:
            potential_title_candidates.append(text_span['text'])
    if potential_title_candidates:
        for title_text in set(potential_title_candidates):
            detected_language = identify_text_language(title_text)
            if detected_language == 'en':
                document_title[detected_language] = normalize_english_text(title_text)
            else:
                document_title[detected_language] = normalize_indic_script_text(title_text, detected_language)
    preliminary_heading_structure = []
    for page_number in range(1, total_page_count + 1):
        page_text_spans = page_span_collections.get(page_number, [])
        for span_index, span_metadata in enumerate(page_text_spans):
            span_text_content = span_metadata['text']
            span_font_size = span_metadata['size']
            span_has_bold_formatting = span_metadata['is_bold']
            if span_text_content in repetitive_content_patterns or len(span_text_content) < 2:
                continue
            qualifies_as_heading = False
            if span_has_bold_formatting and span_font_size > calculated_median_body_font_size * 1.1:
                qualifies_as_heading = True
            elif span_font_size > calculated_median_body_font_size * 1.2 and span_index == 0:
                qualifies_as_heading = True
            elif check_if_all_uppercase(span_text_content) and span_font_size >= calculated_median_body_font_size:
                qualifies_as_heading = True
            if not qualifies_as_heading and span_index + 1 < len(page_text_spans):
                following_span_text = page_text_spans[span_index + 1]['text']
                if re.match(r'^[\u2022\u2023\u25E6\u2043\u2219\-\*\d]', following_span_text.strip()):
                    qualifies_as_heading = True
            if qualifies_as_heading:
                detected_language = identify_text_language(span_text_content)
                if detected_language == 'en':
                    normalized_text_content = normalize_english_text(span_text_content)
                else:
                    normalized_text_content = normalize_indic_script_text(span_text_content, detected_language)
                preliminary_heading_structure.append({"level": None, "text": {detected_language: normalized_text_content}, "page": page_number, "size": span_font_size})
    if preliminary_heading_structure:
        unique_font_sizes = sorted({heading_item['size'] for heading_item in preliminary_heading_structure}, reverse=True)
        for heading_item in preliminary_heading_structure:
            if heading_item['size'] >= unique_font_sizes[0] * 0.95:
                heading_item['level'] = "H1"
            elif len(unique_font_sizes) > 1 and heading_item['size'] >= unique_font_sizes[1] * 0.95:
                heading_item['level'] = "H2"
            else:
                heading_item['level'] = "H3"
    finalized_outline_structure = []
    processed_heading_keys = set()
    for heading_item in preliminary_heading_structure:
        heading_unique_key = (heading_item['level'], tuple(heading_item['text'].items()), heading_item['page'])
        if heading_unique_key not in processed_heading_keys:
            finalized_outline_structure.append({"level": heading_item['level'], "text": heading_item['text'], "page": heading_item['page']})
            processed_heading_keys.add(heading_unique_key)
    document_tables = extract_tabular_data_from_document(pdf_document_path)
    return {"title": document_title, "outline": finalized_outline_structure, "tables": document_tables}

def execute_round1a_processing_pipeline():
    source_input_directory = "input_1A"
    target_output_directory = "output_1A"
    os.makedirs(target_output_directory, exist_ok=True)
    for document_filename in os.listdir(source_input_directory):
        if document_filename.lower().endswith(".pdf"):
            pdf_document_path = os.path.join(source_input_directory, document_filename)
            json_output_filename = document_filename.replace(".pdf", ".json")
            json_output_path = os.path.join(target_output_directory, json_output_filename)
            print(f"Processing {pdf_document_path} for R1A...")
            try:
                extraction_result = extract_document_structure_and_metadata(pdf_document_path)
                with open(json_output_path, 'w', encoding='utf-8') as output_file_handle:
                    json.dump(extraction_result, output_file_handle, ensure_ascii=False, indent=2)
                print(f"Generated R1A output: {json_output_path}")
            except Exception as processing_error:
                print(f"Error processing {pdf_document_path}: {processing_error}")

if __name__ == "__main__":
    execute_round1a_processing_pipeline()