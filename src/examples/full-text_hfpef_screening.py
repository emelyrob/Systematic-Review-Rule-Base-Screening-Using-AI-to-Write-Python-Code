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

import re
from typing import Dict, Any

def normalize_text(text: str) -> str:
    """Normalize text by converting to lowercase and removing extra spaces."""
    # Remove extra whitespace and collapse multiple spaces into a single space
    normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
    return normalized_text

import re
from typing import Dict, Any

def normalize_text(text: str) -> str:
    """Normalize the text to handle case-insensitivity and extra spaces."""
    return re.sub(r'\s+', ' ', text.lower()).strip()

def validate_metabolic_pathways(combined_text: str) -> Dict[str, Any]:
    """Validation for HFpEF-specific metabolic pathways."""
    
    # Normalize text to handle case-insensitivity and extra spaces
    normalized_text = normalize_text(combined_text)
    
    # Metabolic Pathways
    metabolic_terms = [
        r'\bmitochondrial dysfunction\b', r'\boxidative phosphorylation\b', r'\bfatty acid oxidation dominance\b',
        r'\bglucose oxidation\b', r'\binsulin resistance\b', r'\bpyruvate dehydrogenase modulation\b', r'\bsubstrate inflexibility\b', 
        r'\bmetabolic remodeling\b', r'\bnitrosative stress\b', r'\bfatty acid oxidation\b', r'\bsubstrate oxidation\b', r'\bnitrosylation\b',
        r'\bglucose uptake\b', r'\bglycolysis\b', r'\bglycolytic\b', r'\bketone oxidation\b', r'\bmyocardial fatty acid oxidation\b', 
        r'\bPentose phosphate\b', r'\bglycolytic intermediate\b', r'\bhexokinase\b', r'\bphosphofructokinase\b', r'\bobesity\b', 
        r'\binsulin sensitivity\b', r'\badiposity\b', r'\bdiabetes\b', r'\bpyruvate decarboxylation\b', r'\bacylcarnitine*\b'
    ]
    
    # Oxidative Stress and ROS
    oxidative_stress_terms = [
        r'\boxidative\b', r'\stress\b', r'\breactive oxygen species\b', r'\bROS\b', r'\blipotoxicity\b', r'\bcirculating\b', r'\bnitric oxide\b', 
        r'\binducible nitric oxide synthase\b', r'\biNOS\b', r'\bnitric\b', r'\boxide\b'
    ]
    
    # Ketone and Fatty Acid Metabolism
    ketone_fatty_acid_terms = [
        r'\bβ-Hydroxybutyrate\b', r'\bhydroxybutarate\b',r'\bbeta-hydroxybutyrate\b'
    ]

    # Combine all relevant terms
    all_metabolic_terms = metabolic_terms + oxidative_stress_terms + ketone_fatty_acid_terms
    
    # Find matches
    pathway_hits = [term for term in all_metabolic_terms if re.search(term, normalized_text)]
    
    # Debugging output
    print("Metabolic pathway hits:", pathway_hits)
    
    return {
        'is_valid': len(pathway_hits) >= 1,  # Adjust threshold as needed
        'terms_found': pathway_hits
    }

def validate_measurements(text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Validation for HFpEF-specific measurements."""
        
        # Normalize text to handle case-insensitivity and extra spaces
        normalized_text = normalize_text(text)
        
        # Measurement Terms organized into categories
        measurement_terms = {
            "General Measurement Techniques": [
                r'\bradiolabeled energy substrates\b', 
                r'\bnmr\b', 
                r'\bnuclear magnetic resonance\b', 
                r'\bNMR spectroscopy\b', 
                r'\bpet\b', 
                r'\bwestern blotting\b', 
                r'\boxygen consumption\b',
                r'\bacylcarnitine profiling\b', 
                r'\bmetabolic pathway analysis\b', 
                r'\bfatty acid oxidation\b', 
                r'\bglucose oxidation\b', 
                r'\bpyruvate dehydrogenase\b', 
                r'\boxidation profile\b',  
                r'\bsubstrate utilization\b', 
                r'\bworking heart\b', 
                r'\bisolated heart\b', 
                r'\bisotopomer\b', 
                r'\b13c\b', 
                r'\bcarbon-13\b', 
                r'\b14c\b', 
                r'\bcarbon-14\b', 
                r'\btracer\b', 
                r'\bmass spec\b',
            ],
            
            "Advanced Techniques": [
                r'\bmetabolomic*\b', 
                r'\bmetabolite*\b', 
                r'\bateriovenous metabolite\b', 
                r'\benzyme activity\b', 
                r'\bseahorse\b', 
                r'\bglycolytic profile\b', 
                r'\bbranched-chain amino acids\b', 
                r'\bBCAA\b', 
                r'\blong-chain fatty acids\b', 
                r'\bdoppler imaging\b', 
                r'\bunfolded protein\b', 
                r'\bimmunoblot\b', 
                r'\bechocardiography\b', 
                r'\bacetylation\b', 
                r'\bmetabolomics profiling\b', 
                r'\bnitrosative stress\b', 
                r'\binducible nitric oxide synthase\b', 
                r'\biNOS\b', 
                r'\bs-nitrosylation\b', 
                r'\bl-NAME\b', 
                r'\bunfolded protein response\b', 
                r'\bendoplasmic reticulum stress\b', 
                r'\bconstitutive nitric oxide synthase\b',
                r'\bmetabolic stress\b', 
                r'\bhypertensive stress\b', 
                r'\bfatty acid diet\b', 
                r'\bcardiomyocyte dysfunction\b',
                r'\btargeted metabolomics\b', 
                r'\bprotein expression\b',
            ],
            
            "Additional Measurements": [
                r'\bliquid chromatography\b', 
                r'\bdirect measurements\b', 
                r'\bindirect measurements\b'
            ]
        }
    
        # Collect all terms and search for matches in the normalized text
        all_terms = sum(measurement_terms.values(), [])
        measurement_hits = [term for term in all_terms if re.search(term, normalized_text)]
    
        # Debugging output
        print("Measurement hits:", measurement_hits)
        
        # Return results with categories and validation status
        return {
            'is_valid': len(measurement_hits) >= 1,  # Adjust threshold as needed
            'terms_found': measurement_hits,  # List of matched terms
            'category_hits': {  # Matched terms grouped by category
                category: [term for term in terms if re.search(term, normalized_text)]
                for category, terms in measurement_terms.items()
            }
        }

def check_study_relevance(sections: Dict[str, str]) -> Dict[str, Any]:
    combined_text = sections['full_text'].lower()

    experimental_models = {
        'human_studies': [r'patient', r'clinical', r'cohort', r'hfpef', r'diastolic dysfunction'],
        'animal_models': [r'hfd', r'l-name', r'N(ω)-nitro-l-arginine methyl ester', r'high-fat', r'pressure-overload', 
                          r'aortic constriction', r'diastolic dysfunction']
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

    metabolic_pathways_validation = validate_metabolic_pathways(combined_text)

    is_relevant = (
        has_valid_model and 
        measurement_validation['is_valid'] and 
        metabolic_pathways_validation['is_valid']
    )

    return {
        'is_relevant': is_relevant,
        'model_validation': model_validation,
        'has_valid_model': has_valid_model,
        'direct_measurements': measurement_validation,
        'metabolic_pathways': metabolic_pathways_validation
    }

def filter_articles(articles_text: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter and categorize articles."""
    
    categories = {
        'included_original': [],
        'included_reviews': [],
        'excluded_not_hfpef': [],
        'excluded_not_metabolic': [],
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
                    categories['excluded_not_hfpef'].append({
                        'filename': article.get('filename', ''),
                        'reason': 'Not a valid HFpEF model',
                        'model_validation': relevance['model_validation']
                    })
                elif not relevance['metabolic_pathways']['is_valid']:
                    categories['excluded_not_metabolic'].append({
                        'filename': article.get('filename', ''),
                        'reason': 'Insufficient metabolic pathway coverage',
                        'pathways': relevance['metabolic_pathways']
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
                'metabolic_pathways': relevance['metabolic_pathways'],
                'model_validation': relevance['model_validation']
            })
            
        except Exception as e:
            categories['processing_failed'].append({
                'filename': article.get('filename', ''),
                'error': str(e)
            })
    
    return categories

def create_excel_report(categories: Dict[str, List[Dict]], 
                       output_file: str = 'HFpEF_fulltext_screening.xlsx'):
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
                    for col in ['metabolic_pathways', 'measurement_validation', 
                              'model_validation']:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: json.dumps(x, indent=2))
                
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

def process_directory(directory: str = '.') -> List[Dict[str, str]]:
    """Process all text files in a directory."""
    try:
        path = Path(directory)
        files = list(path.glob('*.txt'))
        files.extend(path.glob('*.pdf'))
        
        if not files:
            raise FileNotFoundError(f"No text or PDF files found in {directory}")
            
        processed_files = []
        for file in files:
            if file.suffix == '.pdf':
                text = extract_text_from_pdf(str(file))
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            if text:
                processed_files.append({
                    'filename': file.name,
                    'text': text
                })
                
        return processed_files
    
    except Exception as e:
        print(f"Error processing directory {directory}: {str(e)}")
        return []

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
