"""
Document Structure Extractor
Main class for extracting hierarchical structure from PDF documents.
"""

import fitz
import json
import os
import re
from collections import Counter
from typing import List, Dict, Tuple, Any, Optional

# Import utilities
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from utils.text_processing import (
    identify_text_language, normalize_english_text, normalize_indic_script_text,
    sanitize_whitespace_in_text, check_if_all_uppercase
)
from utils.pdf_processing import (
    check_if_bold_formatting, identify_repetitive_content_patterns,
    extract_page_text_content_with_fallback, analyze_document_structure_patterns,
    extract_pdf_metadata, detect_table_structures
)


class DocumentStructureExtractor:
    """
    Extracts hierarchical structure and metadata from PDF documents.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize the document structure extractor.
        
        Args:
            debug: Enable debug mode for verbose output
        """
        self.debug = debug
        self.font_size_thresholds = {}
        self.repetitive_patterns = {}
        
    def categorize_heading_hierarchical_level(self, text_span: Dict, 
                                            font_size_thresholds: Dict, 
                                            repetitive_patterns: Dict) -> Optional[str]:
        """
        Categorize text span into heading levels based on formatting.
        
        Args:
            text_span: Text span with formatting information
            font_size_thresholds: Font size thresholds for heading levels
            repetitive_patterns: Repetitive content patterns to ignore
            
        Returns:
            Heading level ('H1', 'H2', 'H3') or None
        """
        text_content = text_span['text'].strip()
        font_size = text_span.get('size', 0)
        
        # Skip repetitive content (headers/footers)
        if text_content in repetitive_patterns:
            return None
        
        # Skip very short or very long text
        if len(text_content) < 3 or len(text_content) > 200:
            return None
        
        # Check for heading indicators
        is_bold = check_if_bold_formatting(text_span)
        is_uppercase = check_if_all_uppercase(text_content)
        
        # Determine heading level based on font size and formatting
        if font_size >= font_size_thresholds.get('h1', 16) and (is_bold or is_uppercase):
            return 'H1'
        elif font_size >= font_size_thresholds.get('h2', 14) and is_bold:
            return 'H2'
        elif font_size >= font_size_thresholds.get('h3', 12) and (is_bold or is_uppercase):
            return 'H3'
        
        # Additional pattern-based detection
        if re.match(r'^\\d+\\.\\s+[A-Z]', text_content) and len(text_content) < 100:
            return 'H2'
        elif re.match(r'^[A-Z][A-Z\\s]+$', text_content) and len(text_content) < 50:
            return 'H1'
        
        return None
        
    def extract_document_title(self, all_document_spans: List, pdf_metadata: Dict) -> Dict[str, str]:
        """
        Extract document title in multiple languages.
        
        Args:
            all_document_spans: All text spans from document
            pdf_metadata: PDF metadata
            
        Returns:
            Dictionary with title in different languages
        """
        title_candidates = []
        
        # Check PDF metadata first
        metadata_title = pdf_metadata.get('title', '').strip()
        if metadata_title and len(metadata_title) > 3:
            title_candidates.append(metadata_title)
        
        # Look for title in document content
        for span_data in all_document_spans[:20]:  # Check first 20 spans
            text_content = span_data['text'].strip()
            font_size = span_data.get('size', 0)
            
            # Title criteria: large font, not too long, appears early
            if (font_size >= 16 and 
                10 <= len(text_content) <= 150 and
                not text_content.lower().startswith(('page', 'chapter', 'section'))):
                title_candidates.append(text_content)
        
        # Process title candidates
        multilingual_title = {"en": "", "hi": "", "mr": ""}
        
        for candidate in title_candidates[:3]:  # Take top 3 candidates
            detected_language = identify_text_language(candidate)
            
            if detected_language == 'en' and not multilingual_title["en"]:
                multilingual_title["en"] = normalize_english_text(candidate)
            elif detected_language in ['hi', 'mr'] and not multilingual_title[detected_language]:
                multilingual_title[detected_language] = normalize_indic_script_text(candidate, detected_language)
        
        # Fallback to first candidate if no language-specific title found
        if not any(multilingual_title.values()) and title_candidates:
            multilingual_title["en"] = sanitize_whitespace_in_text(title_candidates[0])
        
        return multilingual_title
        
    def extract_document_structure_and_metadata(self, pdf_document_path: str) -> Dict[str, Any]:
        """
        Extract complete document structure and metadata.
        
        Args:
            pdf_document_path: Path to PDF file
            
        Returns:
            Dictionary with extracted structure and metadata
        """
        if self.debug:
            print(f"Reading PDF from: {pdf_document_path}")
        
        try:
            with fitz.open(pdf_document_path) as pdf_document:
                all_document_spans = []
                total_page_count = pdf_document.page_count
                
                # Extract all text spans with formatting information
                for page_index in range(total_page_count):
                    document_page = pdf_document[page_index]
                    
                    # Extract text with formatting
                    text_blocks = document_page.get_text("dict")
                    
                    for block in text_blocks.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line.get("spans", []):
                                    if span["text"].strip():
                                        all_document_spans.append({
                                            'text': sanitize_whitespace_in_text(span["text"]),
                                            'size': span.get('size', 0),
                                            'font': span.get('font', ''),
                                            'page': page_index + 1,
                                            'bbox': span.get('bbox', [])
                                        })
                
                # Analyze document structure
                structure_analysis = analyze_document_structure_patterns(all_document_spans)
                
                # Determine font size thresholds
                common_sizes = structure_analysis['most_common_sizes']
                if common_sizes:
                    base_size = common_sizes[0][0]  # Most common font size
                    self.font_size_thresholds = {
                        'h1': base_size + 4,
                        'h2': base_size + 2,
                        'h3': base_size + 1
                    }
                
                # Identify repetitive patterns
                self.repetitive_patterns = identify_repetitive_content_patterns(
                    all_document_spans, total_page_count
                )
                
                # Extract PDF metadata
                pdf_metadata = extract_pdf_metadata(pdf_document_path)
                
                # Extract title
                document_title = self.extract_document_title(all_document_spans, pdf_metadata)
                
                # Extract headings
                extracted_headings = []
                for span_data in all_document_spans:
                    heading_level = self.categorize_heading_hierarchical_level(
                        span_data, self.font_size_thresholds, self.repetitive_patterns
                    )
                    
                    if heading_level:
                        text_content = span_data['text']
                        detected_language = identify_text_language(text_content)
                        
                        # Normalize text based on language
                        if detected_language == 'en':
                            normalized_text = normalize_english_text(text_content)
                        else:
                            normalized_text = normalize_indic_script_text(text_content, detected_language)
                        
                        # Create multilingual text entry
                        multilingual_text = {"en": "", "hi": "", "mr": ""}
                        multilingual_text[detected_language] = normalized_text
                        
                        extracted_headings.append({
                            "level": heading_level,
                            "text": multilingual_text,
                            "page": span_data['page'],
                            "font_size": span_data.get('size', 0),
                            "detected_language": detected_language
                        })
                
                # Detect tables
                detected_tables = []
                for page_index in range(min(5, total_page_count)):  # Check first 5 pages
                    page_tables = detect_table_structures(pdf_document_path, page_index)
                    for table in page_tables:
                        table['page'] = page_index + 1
                        detected_tables.append(table)
                
                # Compile final result
                extraction_result = {
                    "title": document_title,
                    "outline": extracted_headings,
                    "tables": detected_tables,
                    "metadata": {
                        "file_path": pdf_document_path,
                        "page_count": total_page_count,
                        "extraction_method": "adobe_hackathon_v2",
                        "language_detection": True,
                        "total_headings": len(extracted_headings),
                        "total_tables": len(detected_tables),
                        **pdf_metadata
                    },
                    "structure_analysis": structure_analysis
                }
                
                if self.debug:
                    print(f"Extracted {len(extracted_headings)} headings and {len(detected_tables)} tables")
                
                return extraction_result
                
        except Exception as extraction_error:
            print(f"Error processing {pdf_document_path}: {extraction_error}")
            return {
                "title": {"en": f"Error processing: {os.path.basename(pdf_document_path)}", "hi": "", "mr": ""},
                "outline": [],
                "tables": [],
                "metadata": {"error": str(extraction_error)},
                "structure_analysis": {}
            }


def extract_document_structure_and_metadata(pdf_document_path: str) -> Dict[str, Any]:
    """
    Legacy function wrapper for backward compatibility.
    
    Args:
        pdf_document_path: Path to PDF file
        
    Returns:
        Dictionary with extracted structure and metadata
    """
    extractor = DocumentStructureExtractor()
    return extractor.extract_document_structure_and_metadata(pdf_document_path)
