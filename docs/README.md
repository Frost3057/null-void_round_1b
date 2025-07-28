# Adobe India Hackathon 2025: Multilingual Document Intelligence System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-Adobe_Hackathon-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)]()

## 🚀 Overview

This project presents a **comprehensive Multilingual Document Intelligence System** developed for the Adobe India Hackathon 2025. The solution addresses two critical challenges in document processing with a **modular, enterprise-grade architecture**:

1. **Round 1A**: Intelligent extraction of hierarchical document structures from multilingual PDFs
2. **Round 1B**: Persona-driven document intelligence for contextual content ranking

### ✨ Key Features

- 🌐 **Multilingual Support**: Robust handling of English, Hindi, and Marathi content
- 🏗️ **Modular Architecture**: Clean separation of concerns with dedicated modules
- 🚀 **High Performance**: CPU-optimized processing meeting strict time constraints
- 🔧 **Production Ready**: Complete evaluation pipeline with comprehensive metrics
- 📦 **Containerized**: Optimized Docker setup with fast development builds
- 🎯 **Semantic Intelligence**: Advanced NLP techniques for contextual understanding
- ✅ **Quality Assured**: Extensive validation and testing frameworks

## 📁 Project Structure

```
Adobe_Hackathon/
├── 📂 src/                              # Source code modules
│   ├── 📂 document_processing/          # PDF processing and structure extraction
│   │   ├── __init__.py
│   │   └── structure_extractor.py       # DocumentStructureExtractor class
│   ├── 📂 validation/                   # Text validation and integrity checking
│   │   ├── __init__.py
│   │   └── text_integrity.py           # TextEncodingIntegrityChecker class
│   ├── 📂 evaluation/                   # Performance evaluation and metrics
│   │   └── __init__.py
│   ├── 📂 utils/                        # Shared utilities and helpers
│   │   ├── __init__.py
│   │   ├── text_processing.py          # Text normalization and language detection
│   │   └── pdf_processing.py           # PDF parsing and content extraction
│   └── __init__.py
├── 📂 scripts/                          # Executable scripts
│   ├── extract_document_structure.py   # Document structure extraction runner
│   └── validate_multilingual_text.py   # Text validation runner
├── 📂 config/                           # Configuration files
├── 📂 docs/                             # Documentation
│   ├── README.md                        # Main documentation
│   └── technical_approach.md           # Technical implementation details
├── 📂 input_1A/                         # Round 1A: Multilingual PDFs for structure extraction
├── 📂 output_1A/                        # Round 1A: Generated JSON outputs with headings
├── 📂 input_1B/                         # Round 1B: Research documents for semantic analysis
├── 📂 output_1B/                        # Round 1B: Persona-driven extraction results
├── 📂 multilingual_model/               # Pre-trained Sentence Transformer models
├── 🐍 main.py                           # Legacy main orchestrator
├── 🐍 r1a_outline_extractor.py         # Legacy Round 1A extractor
├── 🐍 r1b_document_intelligence.py     # Legacy Round 1B processor
├── 🐍 evaluate_accuracy.py             # Legacy evaluation script
├── 🐍 run_evaluation.py                # Legacy pipeline runner
├── 📋 requirements.txt                  # Production dependencies
├── 🐳 dockerfile                        # Optimized production container
├── 🐳 docker-compose.yml               # Multi-service orchestration
└── 📖 docs/README.md                    # This file
```

## 🏗️ Modular Architecture

### **Core Modules**

#### **📂 src/document_processing/**
**Purpose**: PDF processing and document structure extraction

**Key Components**:
- `DocumentStructureExtractor`: Main class for hierarchical structure extraction
- Advanced PDF parsing with multiple fallback strategies
- Multilingual title extraction with language detection
- Robust error handling for malformed documents

**Technical Specifications**:
- **Input**: PDF files from `input_1A/` directory
- **Output**: Structured JSON files in `output_1A/`
- **Performance**: ~5-8 seconds per document
- **Languages**: English, Hindi, Marathi

#### **📂 src/validation/**
**Purpose**: Text validation and encoding integrity checking

**Key Components**:
- `TextEncodingIntegrityChecker`: Validates multilingual text correctness
- `MultilingualValidationPipeline`: Complete validation workflow
- Unicode corruption detection and script validation
- Comprehensive JSON file validation

**Validation Features**:
- Mixed script analysis
- Encoding consistency verification
- Character set validation
- Corruption pattern detection

#### **📂 src/utils/**
**Purpose**: Shared utilities and helper functions

**Key Components**:
- `text_processing.py`: Language detection, text normalization
- `pdf_processing.py`: PDF parsing, metadata extraction, table detection
- Font analysis and formatting detection
- Repetitive content identification

#### **📂 scripts/**
**Purpose**: Executable command-line scripts

**Key Scripts**:
- `extract_document_structure.py`: Document processing runner
- `validate_multilingual_text.py`: Text validation runner
- Clean interfaces for batch processing

## 🚀 Quick Start Guide

### Prerequisites

- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: 2GB free space for models and data
- **OS**: Windows, macOS, or Linux

### Installation

#### Option 1: Local Setup
```bash
# Clone the repository
git clone <repository-url>
cd Adobe_Hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Download required models (if needed)
python download_model.py
```

#### Option 2: Docker Setup (Recommended)
```bash
# Fast development build (5-6 minutes)
docker build -f dockerfile.dev -t adobe-hackathon:dev .

# Production build (full features)
docker build -f dockerfile -t adobe-hackathon:prod .

# Using docker-compose (fastest)
docker-compose up validation
```

## 💻 Usage Instructions

### 1. Document Structure Extraction (Round 1A)

#### Using Modular Scripts:
```bash
# Extract hierarchical headings from multilingual PDFs
python scripts/extract_document_structure.py

# Expected output: JSON files in output_1A/ directory
# Processing time: ~5-8 seconds per document
```

#### Legacy Method:
```bash
python r1a_outline_extractor.py
```

**Sample Output**:
```json
{
  "title": {
    "en": "Research Methodology",
    "hi": "अनुसंधान पद्धति"
  },
  "outline": [
    {
      "level": "H1",
      "text": {"en": "Introduction", "hi": "परिचय"},
      "page": 1,
      "font_size": 16,
      "detected_language": "en"
    }
  ],
  "metadata": {
    "page_count": 10,
    "total_headings": 15,
    "extraction_method": "adobe_hackathon_v2"
  }
}
```

### 2. Multilingual Text Validation

#### Using Modular Scripts:
```bash
# Comprehensive multilingual validation
python scripts/validate_multilingual_text.py --input_dir output_1A --detailed

# Validate Round 1B outputs
python scripts/validate_multilingual_text.py --input_dir output_1B --detailed

# Custom output file
python scripts/validate_multilingual_text.py --input_dir output_1A --output_file custom_report.json
```

#### Legacy Method:
```bash
python validate_multilingual.py --input_dir output_1A --detailed
```

### 3. Semantic Document Analysis (Round 1B)

```bash
# Full semantic analysis (requires sentence-transformers)
python r1b_document_intelligence.py

# Expected output: Ranked relevant sections in output_1B/
# Processing time: ~15-20 seconds for 3-5 documents
```

### 4. Docker Operations

#### Quick Development Testing:
```bash
# Fast validation with docker-compose (6 seconds!)
docker-compose up validation

# Development container
docker run --rm -v "$(pwd)/output_1A:/app/output_1A" adobe-hackathon:dev

# Production container
docker run --rm -v "$(pwd)/input_1A:/app/input_1A" -v "$(pwd)/output_1A:/app/output_1A" adobe-hackathon:prod
```

### 5. Complete Pipeline Execution

```bash
# Legacy complete pipeline
python run_evaluation.py --mode both

# Modular approach
python scripts/extract_document_structure.py
python scripts/validate_multilingual_text.py --input_dir output_1A
python evaluate_accuracy.py --mode r1a --detailed
```

## 🔍 Module APIs

### DocumentStructureExtractor

```python
from src.document_processing.structure_extractor import DocumentStructureExtractor

# Initialize extractor
extractor = DocumentStructureExtractor(debug=True)

# Extract structure from PDF
result = extractor.extract_document_structure_and_metadata("document.pdf")

# Access results
title = result["title"]
headings = result["outline"]
tables = result["tables"]
metadata = result["metadata"]
```

### TextEncodingIntegrityChecker

```python
from src.validation.text_integrity import TextEncodingIntegrityChecker, MultilingualValidationPipeline

# Initialize checker
checker = TextEncodingIntegrityChecker()

# Validate text
is_valid = checker.verify_devanagari_script_authenticity("text")
analysis = checker.analyze_text_corruption_patterns("text")

# Validate JSON file
result = checker.perform_comprehensive_json_file_validation("file.json")

# Use validation pipeline
pipeline = MultilingualValidationPipeline()
report = pipeline.validate_directory("output_1A", detailed_output=True)
```

## 📊 Performance Specifications

### Benchmark Results

| Metric | Round 1A | Round 1B | Target |
|--------|----------|----------|---------|
| **Processing Speed** | 5-8s/doc | 15-20s/batch | <60s total |
| **Memory Usage** | <500MB | <1GB | <2GB |
| **Model Size** | N/A | 80MB | <1GB |
| **Accuracy (F1)** | 0.85-0.92 | 0.78-0.88 | >0.80 |

### Docker Build Performance

| Build Type | Time | Use Case |
|------------|------|----------|
| **Development** | ~5-6 min | Testing, validation, quick iterations |
| **Cached Development** | ~6 seconds! | Subsequent builds with docker-compose |
| **Production** | ~8-12 min | Full functionality with all ML libraries |

## 🛠️ Development

### Code Organization

- **Separation of Concerns**: Each module has a specific responsibility
- **Clean Interfaces**: Well-defined APIs between modules
- **Type Hints**: Full type annotations for better IDE support
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust error handling with meaningful messages

### Testing

```bash
# Run validation tests
python scripts/validate_multilingual_text.py --input_dir output_1A --detailed

# Test document processing
python scripts/extract_document_structure.py

# Docker testing
docker-compose up validation
```

### Adding New Features

1. **Create module** in appropriate `src/` subdirectory
2. **Add __init__.py** imports
3. **Create script** in `scripts/` directory
4. **Update documentation** in `docs/`
5. **Test with Docker** using development container

## 🔒 Security and Privacy

- **Local Processing**: All data remains on local system
- **No External Calls**: Zero network communication during processing
- **Secure Containerization**: Isolated Docker environment
- **Input Validation**: Comprehensive input sanitization

## 📚 Documentation

- **[Technical Approach](technical_approach.md)**: Detailed methodology and algorithms
- **[Module Documentation](../src/)**: Individual module documentation
- **[Docker Guide](../docker-compose.yml)**: Container orchestration details

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 guidelines
2. **Modular Design**: Add features to appropriate modules
3. **Testing**: Test with both scripts and Docker
4. **Documentation**: Update module and script documentation

## 📄 License and Acknowledgments

This project is developed for the Adobe India Hackathon 2025. All rights reserved to Adobe Inc.

### Project Information
- **Version**: 2.0.1 (Modular Architecture)
- **Architecture**: Microservices-inspired modular design
- **Last Updated**: July 28, 2025
- **Status**: Production Ready with Modular Structure

---

**🚀 Ready to process multilingual documents with intelligence and modularity? Get started with the Quick Start Guide above!**