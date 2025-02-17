import pandas as pd
import re
from pathlib import Path
import os
from difflib import SequenceMatcher

def check_condition_terms(entry):
    """Check if entry contains condition terms or models"""
    condition_terms = [
        'term1', 'term2', 'term3', 'term4',
        'term5', 'term6', 'term7', 'term8',
        'term9', 'term10', 'term11', 'term12',
        'term13', 'term14', 'term15'
    ]
    
    model_terms = [
        'model1', 'model2', 'model3',
        'model4', 'model5', 'model6', 'model7'
    ]
    
    text = f"{entry.get('title', '')} {entry.get('abstract', '')}".lower()
    return any(term in text for term in condition_terms) or any(term in text for term in model_terms)
    
def check_pathway_detail(entry):
    """Check if entry contains detailed pathway information"""
    pathway_terms = {
        'pathway1': [
            'term1', 'term2', 'term3',
            'term4', 'term5', 'term6',
            'term7', 'term8', 'term9'
        ],
        'pathway2': [
            'term10', 'term11', 'term12',
            'term13', 'term14', 'term15',
            'term16', 'term17', 'term18'
        ],
        'pathway3': [
            'term19', 'term20', 'term21',
            'term22', 'term23'
        ],
        'pathway4': [
            'term24', 'term25', 'term26',
            'term27', 'term28', 'term29'
        ],
        'pathway5': [
            'term30', 'term31', 'term32',
            'term33', 'term34', 'term35',
            'term36', 'term37', 'term38', 
            'term39'
        ]
    }
    
    text = f"{entry.get('title', '')} {entry.get('abstract', '')}".lower()
    
    pathway_matches = {pathway: 0 for pathway in pathway_terms}
    for pathway, terms in pathway_terms.items():
        pathway_matches[pathway] = sum(1 for term in terms if term in text)

    pathways_covered = sum(1 for count in pathway_matches.values() if count > 0)
    detailed_pathway = any(count >= 3 for count in pathway_matches.values())
    
    return pathways_covered >= 3 or detailed_pathway

def check_methodology_terms(entry):
    """Check if entry contains methodology terms"""
    method_terms = {
        'method1': [
            'term1', 'term2', 'term3',
            'term4', 'term5', 'term6'
        ],
        'method2': [
            'term7', 'term8', 'term9',
            'term10', 'term11', 'term12'
        ],
        'method3': [
            'term13', 'term14', 'term15'
        ],
        'method4': [
            'term16', 'term17', 'term18'
        ],
        'method5': [
            'term19', 'term20', 'term21',
            'term22', 'term23', 'term24',
            'term25', 'term26', 'term27'
        ],
        'direct_measurement_terms': [
            'measurement1', 'measurement2', 'measurement3',
            'measurement4', 'measurement5', 'measurement6',
            'measurement7', 'measurement8', 'measurement9',
            'measurement10', 'measurement11', 'measurement12',
            
            # Additional measurement terms
            'measurement13', 'measurement14', 'measurement15',
            'measurement16', 'measurement17', 'measurement18',
            'measurement19', 'measurement20', 'measurement21'
        ]
    }
    
    text = f"{entry.get('title', '')} {entry.get('abstract', '')}".lower()
    
    # Check each category of terms
    has_pathway_measurement = False
    has_direct_measurement = False
    has_indirect_measurement = False
    
    # Check pathway-specific measurements
    for category in ['method1', 'method2', 'method3', 'method4', 'method5']:
        if any(term in text for term in method_terms[category]):
            has_pathway_measurement = True
            break
    
    # Check for direct measurements and pathway measurements
    has_direct_measurement = any(term in text for term in method_terms['direct_measurement_terms'])
    pathway_measurements = sum(1 for pathway in ['method1', 'method2', 'method3', 'method4', 'method5']
                             if any(term in text for term in method_terms[pathway]))
    
    return has_direct_measurement or pathway_measurements >= 1

def normalize_text(text):
    """Normalize text for comparison, preserving more meaningful variations"""
    if not text:
        return ""
    # Remove punctuation but keep numbers
    text = re.sub(r'[^\w\s\d]', '', text.lower())
    # Normalize whitespace
    text = ' '.join(text.split())
    return text

def text_similarity(text1, text2):
    """Calculate similarity between two texts using SequenceMatcher"""
    if not text1 or not text2:
        return 0
    return SequenceMatcher(None, text1, text2).ratio()

def get_entry_key(entry):
    """Generate a unique key for an entry using both title and abstract"""
    title = normalize_text(entry.get('title', ''))
    abstract = normalize_text(entry.get('abstract', ''))[:300] if entry.get('abstract') else ''
    return f"{title}|{abstract}"


def parse_endnote_entries(text):
    """Parse Endnote format entries
    
    Args:
        text (str): Raw text from Endnote export file
        
    Returns:
        list: List of dictionaries containing parsed article data
    """
    # Split text into individual entries
    entries = re.split(r'\n\n(?=Reference Type:)', text.strip())
    parsed_entries = []
    
    for entry in entries:
        if not entry.strip():
            continue
        
        entry_dict = {}
        
        # Extract reference type
        type_match = re.search(r'Reference Type:\s*(.+)', entry)
        if type_match:
            entry_dict['publication_type'] = type_match.group(1).strip()
        
        # Extract year
        year_match = re.search(r'Year:\s*(\d{4})', entry)
        if year_match:
            entry_dict['year'] = year_match.group(1)
        
        # Extract title
        title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', entry, re.DOTALL)
        if title_match:
            entry_dict['title'] = title_match.group(1).strip().replace('\n', ' ')
        
        # Extract journal
        journal_match = re.search(r'Journal:\s*(.+?)(?:\n|$)', entry)
        if journal_match:
            entry_dict['journal'] = journal_match.group(1).strip()
        
        # Extract volume
        volume_match = re.search(r'Volume:\s*(\d+)', entry)
        if volume_match:
            entry_dict['volume'] = volume_match.group(1)
        
        # Extract issue
        issue_match = re.search(r'Issue:\s*(\d+)', entry)
        if issue_match:
            entry_dict['issue'] = issue_match.group(1)
        
        # Extract authors
        authors_match = re.search(r'Author:\s*(.+?)(?:\n|$)', entry, re.DOTALL)
        if authors_match:
            # Clean up and handle multiple authors
            authors = authors_match.group(1).strip().replace('\n', ' ')
            entry_dict['authors'] = authors
        
        # Extract abstract
        abstract_match = re.search(r'Abstract:\s*(.+?)(?:\n\w+:|$)', entry, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip().replace('\n', ' ')
            entry_dict['abstract'] = abstract
        
        # Additional metadata
        doi_match = re.search(r'DOI:\s*(.+?)(?:\n|$)', entry)
        if doi_match:
            entry_dict['doi'] = doi_match.group(1).strip()
        
        # Add source database
        entry_dict['database'] = 'Endnote'
        
        # Only add entries with at least a title
        if entry_dict.get('title'):
            parsed_entries.append(entry_dict)
    
    return parsed_entries

def filter_articles(entries):
    """Filter and categorize articles with improved metabolic study inclusion"""
    categories = {
        'included': [],
        'systematic_reviews': [],
        'narrative_reviews': [],
        'duplicates': [],
        'not_HFpEF_related': [],
        'no_measurements': []
    }
    
    seen_entries = {}
    
    for entry in entries:
        # Check for near-duplicates
        entry_key = get_entry_key(entry)
        is_duplicate = False
        
        for seen_key in seen_entries:
            if text_similarity(entry_key, seen_key) > 0.85:
                categories['duplicates'].append(entry)
                is_duplicate = True
                break
        
        if is_duplicate:
            continue
            
        seen_entries[entry_key] = entry
        
        # Categorize based on publication type
        pub_type = entry.get('publication_type', '').lower()
        
        if 'review' in pub_type:
            if any(term in pub_type for term in ['systematic', 'meta-analysis']):
                categories['systematic_reviews'].append(entry)
            else:
                categories['narrative_reviews'].append(entry)
            continue
            
        # Modified inclusion criteria:
        # 1. Must be HFpEF-related
        if not check_hfpef_terms(entry):
            categories['not_HFpEF_related'].append(entry)
            continue
            
        # 2. Must have EITHER detailed metabolic pathway coverage OR metabolic measurements
        if not (check_metabolic_detail(entry) or check_metabolic_measurements(entry)):
            categories['no_measurements'].append(entry)
            continue
            
        categories['included'].append(entry)
    
    return categories

def create_excel_report(categories, output_file='articles_classification.xlsx'):
    """Create detailed Excel report with article categorization"""
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Summary sheet
        summary_data = {
            'Category': list(categories.keys()),
            'Count': [len(entries) for entries in categories.values()]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format summary sheet
        workbook = writer.book
        summary_sheet = writer.sheets['Summary']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        summary_sheet.set_column('A:A', 30)
        summary_sheet.set_column('B:B', 15)
        
        # Category sheets
        for category, entries in categories.items():
            if entries:
                df = pd.DataFrame(entries)
                
                # Ensure core columns exist and are ordered first
                core_columns = ['title', 'abstract', 'publication_type', 'database']
                for col in core_columns:
                    if col not in df.columns:
                        df[col] = ''
                
                # Reorder columns
                other_cols = [c for c in df.columns if c not in core_columns]
                df = df[core_columns + other_cols]
                
                sheet_name = category[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:A', 50)  # Title
                worksheet.set_column('B:B', 70)  # Abstract
                worksheet.set_column('C:D', 20)  # Other columns

def main():
    try:
        # Prompt for input file
        input_file = input("Enter the path to your Endnote export text file: ").strip()
        
        # Verify file exists
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} does not exist.")
            return
        
        # Read the input file
        print(f"Reading from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Parse Endnote entries
        print("Parsing entries...")
        all_entries = parse_endnote_entries(text)
        
        # Filter and categorize
        print("\nCategorizing entries...")
        categories = filter_articles(all_entries)
        
        # Create report
        print("\nCreating Excel report...")
        create_excel_report(categories)
        
        print(f"\nProcessing complete! Found {len(all_entries)} total entries")
        
        # Print statistics
        print("\nEntries by database:")
        db_counts = {}
        for entry in all_entries:
            db = entry.get('database', 'unknown')
            db_counts[db] = db_counts.get(db, 0) + 1
        for db, count in db_counts.items():
            print(f"{db}: {count}")
            
        print("\nEntries by category:")
        for category, entries in categories.items():
            print(f"{category}: {len(entries)}")
        
        if categories['included']:
            print("\nSample included papers (first 3):")
            for i, entry in enumerate(categories['included'][:3]):
                print(f"\nPaper {i+1}:")
                print(f"Title: {entry.get('title', '')}")
                print(f"Database: {entry.get('database', '')}")
                print(f"Type: {entry.get('publication_type', '')}")
        
        print("\nDone! Check articles_classification.xlsx for detailed results.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
