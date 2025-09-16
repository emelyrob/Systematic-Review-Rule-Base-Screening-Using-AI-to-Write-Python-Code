# Systematic Review Automation Toolkit

This repository contains Python scripts for accelerating systematic review completion using automated screening and data extraction tools. The toolkit is designed to reduce systematic review completion time while maintaining methodological rigor.

## Overview

Traditional systematic reviews typically require 6-24 months to complete. This toolkit provides a protocol that can significantly accelerate this process through:
- Automated title and abstract screening
- Intelligent duplicate detection
- Structured data extraction
- Customizable screening criteria
- Standardized output generation

## Requirements

### Software Requirements
- Python 3.x
- Jupyter Notebook (recommended)

### Python Dependencies
pandas
numpy
openpyxl
python-docx
PyPDF2
tqdm
scipy
xlsxwriter

## Installation

1. If using Jupyter Notebook, install dependencies:

!pip install pandas numpy openpyxl python-docx PyPDF2 tqdm scipy xlsxwriter

2. Restart your Jupyter kernel after installation

3. Verify installation:

import pandas as pd
import numpy as np
import openpyxl
from docx import Document
import PyPDF2
from tqdm import tqdm
import scipy
import xlsxwriter

## Usage

### Phase 1: Title and Abstract Screening

1. Prepare your EndNote export file in .txt format
2. Upload the .txt file to your working directory
3. Run the title/abstract screening script
4. When prompted, enter your input file name (including .txt extension)
5. Review the generated Excel report: 'articles_classification.xlsx'

### Customizing Search Terms

The scripts include several configurable term lists:
- Primary condition terms
- Model/methodology terms
- Pathway/mechanism terms
- Measurement terms

Modify these terms in the script to match your research focus:

condition_terms = [
    'your_term_1',
    'your_term_2',
    # Add your terms
]

## Output

The screening process generates an Excel file containing:
- Summary statistics
- Categorized articles
- Detailed screening decisions
- Full article metadata

## Example Implementation

See 'Resources/Examples/Title_Abstracts_Screening Script_HFpEF_Cardiac Terms_Example.py' for a complete implementation focused on heart failure with preserved ejection fraction (HFpEF) research.

## Customization Guidelines

1. Term Selection:
   - Include common variations and abbreviations
   - Consider regional spelling differences
   - Include method-specific terminology

2. Screening Logic:
   - Adjust required term thresholds
   - Modify category combinations
   - Customize output categories

3. Testing:
   - Validate on known relevant papers
   - Check for false positives/negatives
   - Document adjustments


