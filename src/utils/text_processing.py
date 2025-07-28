"""
Text Processing Utilities
Common text processing functions for multilingual content handling.
"""

import re
import wordninja
from langdetect import detect

try:
    from indicnlp.tokenize import sentence_tokenize, indic_tokenize
    INDICNLP_AVAILABLE = True
except ImportError:
    INDICNLP_AVAILABLE = False
    print('[INFO] IndicNLP not available, using basic whitespace heuristics for Indian languages.')


def identify_text_language(input_text: str) -> str:
    """
    Detect the language of input text.
    
    Args:
        input_text: Text to analyze
        
    Returns:
        Language code ('hi', 'mr', 'en')
    """
    try:
        detected_language = detect(input_text)
        if detected_language in ['hi', 'mr', 'en']:
            return detected_language
    except Exception:
        pass
    return 'en'


def normalize_english_text(input_text: str) -> str:
    """
    Normalize English text by splitting concatenated words.
    
    Args:
        input_text: Text to normalize
        
    Returns:
        Normalized text with proper spacing
    """
    if not input_text or ' ' in input_text:
        return input_text.strip()
    return ' '.join(wordninja.split(input_text)).strip()


def normalize_indic_script_text(input_text: str, language_code: str) -> str:
    """
    Normalize Indic script text with proper tokenization.
    
    Args:
        input_text: Text to normalize
        language_code: Language code ('hi', 'mr')
        
    Returns:
        Normalized text with proper spacing and punctuation
    """
    if INDICNLP_AVAILABLE and language_code in ['hi', 'mr']:
        return ' '.join(indic_tokenize.trivial_tokenize(input_text, lang=language_code)).replace(' ।', '।').strip()
    return re.sub(r'([।,.!?])', r'\\1 ', input_text).replace('  ', ' ').strip()


def validate_devanagari_script_integrity(input_text: str) -> bool:
    """
    Check if text contains valid Devanagari characters.
    
    Args:
        input_text: Text to validate
        
    Returns:
        True if text is valid, False otherwise
    """
    return not any('\\u0900' <= character <= '\\u097F' for character in input_text)


def sanitize_whitespace_in_text(input_text: str) -> str:
    """
    Clean up whitespace in text.
    
    Args:
        input_text: Text to sanitize
        
    Returns:
        Text with normalized whitespace
    """
    return re.sub(r'\\s+', ' ', input_text).strip()


def check_if_all_uppercase(input_text: str) -> bool:
    """
    Check if text is in all uppercase.
    
    Args:
        input_text: Text to check
        
    Returns:
        True if text is uppercase, False otherwise
    """
    return input_text.isupper() and len(input_text) > 2 and any(character.isalpha() for character in input_text)


def validate_character_encoding_integrity(input_text: str, language_code: str) -> bool:
    """
    Validate character encoding integrity for given language.
    
    Args:
        input_text: Text to validate
        language_code: Language code
        
    Returns:
        True if encoding is valid, False otherwise
    """
    if not input_text:
        return True
    
    # Check for basic encoding issues
    try:
        input_text.encode('utf-8').decode('utf-8')
    except UnicodeError:
        return False
    
    # Check for mixed script issues in Devanagari text
    if language_code in ['hi', 'mr']:
        devanagari_chars = sum(1 for char in input_text if '\\u0900' <= char <= '\\u097F')
        latin_chars = sum(1 for char in input_text if char.isalpha() and ord(char) < 128)
        
        # If both scripts present, it might be corrupted
        if devanagari_chars > 0 and latin_chars > 0:
            return False
    
    return True
