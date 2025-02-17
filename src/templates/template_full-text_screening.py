import re
import pandas as pd
from typing import Dict, List, Any
import json
from pathlib import Path
import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return ''

def extract_text_sections(text: str) -> Dict[str, str]:
    """Extract different sections from the text."""
    sections = {
        'full_text': text,
        'methods': '',
        'results': '',
        'discussion': '',
        'abstract': ''
    }
    
    section_patterns = {
        'methods': r'(?:materials\s+and\s+)?methods|experimental procedures|study design',
        'results': r'results|findings|outcomes',
        'discussion': r'discussion|conclusion|implications',
        'abstract': r'abstract|summary'
    }
    
    current_section = None
    current_text = []
    
    for line in text.split('\n'):
        for section, pattern in section_patterns.items():
            if re.match(rf'\b{pattern}\b', line.strip().lower()):
                if current_section:
                    sections[current_section] = '\n'.join(current_text).strip()
                current_section = section
                current_text = []
                break
        else:
            if current_section:
                current_text.append(line)
    
    if current_section and current_text:
        sections[current_section] = '\n'.join(current_text).strip()
    
    return sections

def normalize_text(text: str) -> str:
    """Normalize text by converting to lowercase and removing extra spaces."""
    return re.sub(r'\s+', ' ', text.lower()).strip()

def validate_pathway_terms(combined_text: str) -> Dict[str, Any]:
    """Validation for condition-specific pathways."""
    
    normalized_text = normalize_text(combined_text)
    
    # Primary Pathway Terms
    primary_terms = [
        r'\bterm1\b', r'\bterm2\b', r'\bterm3\b',
        r'\bterm4\b', r'\bterm5\b', r'\bterm6\b',
        r'\bterm7\b', r'\bterm8\b', r'\bterm9\b'
    ]
    
    # Secondary Pathway Terms
    secondary_terms = [
        r'\bterm10\b', r'\bterm11\b', r'\bterm12\b',
        r'\bterm13\b', r'\bterm14\b', r'\bterm15\b'
    ]
    
    # Additional Pathway Terms
    additional_terms = [
        r'\bterm16\b', r'\bterm17\b', r'\bterm18\b'
    ]

    all_pathway_terms = primary_terms + secondary_terms + additional_terms
    
    pathway_hits = [term for term in all_pathway_terms if re.search(term, normalized_text)]
    
    print("Pathway term hits:", pathway_hits)
    
    return {
        'is_valid': len(pathway_hits) >= 1,  # Configurable threshold
        'terms_found': pathway_hits
    }

def validate_measurements(text: str, sections: Dict[str, str]) -> Dict[str, Any]:
    """Validation for condition-specific measurements."""
    
    normalized_text = normalize_text(text)
    
    measurement_terms = {
        "Primary Techniques": [
            r'\btechnique1\b', r'\btechnique2\b', r'\btechnique3\b',
            r'\btechnique4\b', r'\btechnique5\b', r'\btechnique6\b',
            r'\btechnique7\b', r'\btechnique8\b', r'\btechnique9\b'
        ],
        
        "Advanced Techniques": [
            r'\badvanced1\b', r'\badvanced2\b', r'\badvanced3\b',
            r'\badvanced4\b', r'\badvanced5\b', r'\badvanced6\b',
            r'\badvanced7\b', r'\badvanced8\b', r'\badvanced9\b'
        ],
        
        "Additional Measurements": [
            r'\bmeasurement1\b', r'\bmeasurement2\b', r'\bmeasurement3\b'
        ]
    }

    all_terms = sum(measurement_terms.values(), [])
    measurement_hits = [term for term in all_terms if re.search(term, normalized_text)]

    print("Measurement hits:", measurement_hits)
    
    return {
        'is_valid': len(measurement_hits) >= 1,  # Configurable threshold
        'terms_found': measurement_hits,
        'category_hits': {
            category: [term for term in terms if re.search(term, normalized_text)]
            for category, terms in measurement_terms.items()
        }
    }

def check_study_relevance(sections: Dict[str, str]) -> Dict[str, Any]:
    combined_text = sections['full_text'].lower()

    experimental_models = {
        'model_type1': [r'term1', r'term2', r'term3', r'term4', r'term5'],
        'model_type2': [r'term6', r'term7', r'term8', r'term9', r'term10']
    }

    model_validation = {}
    for model_type, patterns in experimental_models.items():
        matches = [term for term in patterns if re.search(term, combined_text)]
        model_validation[model_type] = {
            'present': bool(matches),
            'matches': matches
        }

    has_valid_model = any(v['present'] for v in model_validation.values())

    measurement_validation = validate_measurements(combined_text, sections)
    pathway_validation = validate_pathway_terms(combined_text)

    is_relevant = (
        has_valid_model and 
        measurement_validation['is_valid'] and 
        pathway_validation['is_valid']
    )

    return {
        'is_relevant': is_relevant,
        'model_validation': model_validation,
        'has_valid_model': has_valid_model,
        'direct_measurements': measurement_validation,
        'pathways': pathway_validation
    }

def filter_articles(articles_text: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter and categorize articles."""
    
    categories = {
        'included_original': [],
        'included_reviews': [],
        'excluded_not_condition': [],
        'excluded_not_pathway': [],
        'excluded_no_methods': [],
        'processing_failed': []
    }
    
    for article in articles_text:
        try:
            text = article.get('text', '')
            if not text:
                raise ValueError("Empty text content")
            
            sections = extract_text_sections(text)
            
            if re.search(r'\breview\b|meta[ -]analysis|systematic review', text.lower()[:1000]):
                categories['included_reviews'].append({
                    'filename': article.get('filename', ''),
                    'title': sections.get('title', '')[:200]
                })
                continue
            
            relevance = check_study_relevance(sections)
            
            if not relevance['is_relevant']:
                if not relevance['has_valid_model']:
                    categories['excluded_not_condition'].append({
                        'filename': article.get('filename', ''),
                        'reason': 'Not a valid condition model',
                        'model_validation': relevance['model_validation']
                    })
                elif not relevance['pathways']['is_valid']:
                    categories['excluded_not_pathway'].append({
                        'filename': article.get('filename', ''),
                        'reason': 'Insufficient pathway coverage',
                        'pathways': relevance['pathways']
                    })
                elif not relevance['direct_measurements']['is_valid']:
                    categories['excluded_no_methods'].append({
                        'filename': article.get('filename', ''),
                        'reason': 'Insufficient validated measurements',
                        'measurements': relevance['direct_measurements']
                    })
                continue
            
            categories['included_original'].append({
                'filename': article.get('filename', ''),
                'methods_text': sections.get('methods', '')[:500],
                'measurement_validation': relevance['direct_measurements'],
                'pathways': relevance['pathways'],
                'model_validation': relevance['model_validation']
            })
            
        except Exception as e:
            categories['processing_failed'].append({
                'filename': article.get('filename', ''),
                'error': str(e)
            })
    
    return categories

def create_excel_report(categories: Dict[str, List[Dict]], 
                       output_file: str = 'fulltext_screening.xlsx'):
    """Generate detailed screening report."""
    
    with pd.ExcelWriter(output_file) as writer:
        summary_data = {
            'Category': list(categories.keys()),
            'Count': [len(entries) for entries in categories.values()]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', 
                                          index=False)
        
        for sheet_name, entries in categories.items():
            if entries:
                df = pd.DataFrame(entries)
                if sheet_name == 'included_original':
                    for col in ['pathways', 'measurement_validation', 
                              'model_validation']:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: json.dumps(x, indent=2))
                
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)


def main():
    """Main function to process files."""
    try:
        pdf_dir = input("Enter the path to your PDF directory (or press Enter to use current directory): ").strip()
        if not pdf_dir:
            pdf_dir = '.'
        
        path = Path(pdf_dir)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {pdf_dir}")
            
        print(f"\nAnalyzing files in {pdf_dir}...")
        
        articles = process_directory(pdf_dir)
        
        if not articles:
            raise ValueError("No text could be extracted from files")
            
        print("\nFiltering articles...")
        categories = filter_articles(articles)
        
        print("Creating report...")
        create_excel_report(categories)
        
        print("\nScreening complete! Summary:")
        for category, entries in categories.items():
            print(f"{category}: {len(entries)} entries")
            
        print("\nResults saved to 'HFpEF_fulltext_screening.xlsx'")
        
        return categories
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()

