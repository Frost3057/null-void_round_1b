"""
PDF Processing Utilities
Functions for PDF parsing, text extraction, and document analysis.
"""

import fitz
import pdfplumber
import json
import os
import re
from collections import Counter
from typing import List, Dict, Tuple, Any, Optional


def check_if_bold_formatting(text_span: Dict) -> bool:
    """
    Check if text span has bold formatting.
    
    Args:
        text_span: Text span with font information
        
    Returns:
        True if text is bold, False otherwise
    """
    return "bold" in text_span['font'].lower() or "bld" in text_span['font'].lower()


def identify_repetitive_content_patterns(all_document_spans: List, total_page_count: int) -> Dict[str, int]:
    """
    Identify repetitive content across document pages.
    
    Args:
        all_document_spans: All text spans from document
        total_page_count: Total number of pages
        
    Returns:
        Dictionary of repetitive patterns and their frequencies
    """
    page_text_collections = {}
    
    for span_data in all_document_spans:
        page_number = span_data['page']
        text_content = span_data['text'].strip()
        
        if page_number not in page_text_collections:
            page_text_collections[page_number] = []
        page_text_collections[page_number].append(text_content)
    
    # Find common elements across pages
    text_frequency_counter = Counter()
    for page_content in page_text_collections.values():
        for text_item in page_content:
            if len(text_item) > 10:  # Only consider substantial text
                text_frequency_counter[text_item] += 1
    
    # Identify headers/footers (appear on multiple pages)
    repetitive_patterns = {}
    for text_content, frequency_count in text_frequency_counter.items():
        if frequency_count >= max(2, total_page_count * 0.3):
            repetitive_patterns[text_content] = frequency_count
    
    return repetitive_patterns


def extract_page_text_content_with_fallback(document_page, pdf_document_path: str, page_index: int) -> str:
    """
    Extract text from a PDF page with multiple fallback methods.
    
    Args:
        document_page: PDF page object
        pdf_document_path: Path to PDF file
        page_index: Page index number
        
    Returns:
        Extracted text content
    """
    extracted_text_content = ""
    
    try:
        # Primary method: PyMuPDF
        extracted_text_content = document_page.get_text()
        if extracted_text_content.strip():
            return extracted_text_content
    except Exception as extraction_error:
        print(f"PyMuPDF extraction failed for page {page_index}: {extraction_error}")
    
    try:
        # Fallback method: pdfplumber
        with pdfplumber.open(pdf_document_path) as pdf_document:
            if page_index < len(pdf_document.pages):
                fallback_page = pdf_document.pages[page_index]
                fallback_text = fallback_page.extract_text()
                if fallback_text and fallback_text.strip():
                    return fallback_text
    except Exception as fallback_error:
        print(f"pdfplumber extraction failed for page {page_index}: {fallback_error}")
    
    return extracted_text_content


def analyze_document_structure_patterns(all_document_spans: List) -> Dict[str, Any]:
    """
    Analyze document structure and identify heading patterns.
    
    Args:
        all_document_spans: All text spans from document
        
    Returns:
        Dictionary with structure analysis results
    """
    font_size_distribution = Counter()
    formatting_patterns = {'bold': 0, 'italic': 0, 'uppercase': 0}
    
    for span_data in all_document_spans:
        font_size = span_data.get('size', 0)
        font_size_distribution[font_size] += 1
        
        if span_data.get('bold', False):
            formatting_patterns['bold'] += 1
        if span_data.get('italic', False):
            formatting_patterns['italic'] += 1
        if span_data.get('text', '').isupper():
            formatting_patterns['uppercase'] += 1
    
    # Identify common font sizes
    most_common_sizes = font_size_distribution.most_common(5)
    
    return {
        'font_size_distribution': dict(font_size_distribution),
        'most_common_sizes': most_common_sizes,
        'formatting_patterns': formatting_patterns,
        'total_spans': len(all_document_spans)
    }


def extract_pdf_metadata(pdf_document_path: str) -> Dict[str, Any]:
    """
    Extract metadata from PDF document.
    
    Args:
        pdf_document_path: Path to PDF file
        
    Returns:
        Dictionary with PDF metadata
    """
    try:
        with fitz.open(pdf_document_path) as pdf_document:
            metadata = pdf_document.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': pdf_document.page_count,
                'file_size': os.path.getsize(pdf_document_path) if os.path.exists(pdf_document_path) else 0
            }
    except Exception as metadata_error:
        print(f"Failed to extract metadata from {pdf_document_path}: {metadata_error}")
        return {}


def detect_table_structures(pdf_document_path: str, page_index: int) -> List[Dict]:
    """
    Detect table structures in PDF page.
    
    Args:
        pdf_document_path: Path to PDF file
        page_index: Page index to analyze
        
    Returns:
        List of detected table structures
    """
    detected_tables = []
    
    try:
        with pdfplumber.open(pdf_document_path) as pdf_document:
            if page_index < len(pdf_document.pages):
                page = pdf_document.pages[page_index]
                tables = page.extract_tables()
                
                for table_index, table_data in enumerate(tables):
                    if table_data and len(table_data) > 1:  # Valid table with headers and data
                        detected_tables.append({
                            'table_id': table_index,
                            'row_count': len(table_data),
                            'column_count': len(table_data[0]) if table_data else 0,
                            'headers': table_data[0] if table_data else [],
                            'preview_rows': table_data[1:3] if len(table_data) > 1 else []
                        })
    except Exception as table_error:
        print(f"Table detection failed for page {page_index}: {table_error}")
    
    return detected_tables
