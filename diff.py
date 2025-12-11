# CSV/TXT ID Comparison Script
# 
# This script loads two CSV/TXT files, compares ID values between them,
# identifies matches and non-matches, and saves detailed reports.
#
# How to use:
# - Set `file1_path` and `file2_path` to your files.
# - If files have headers, set `id_column` to the ID column name and keep `use_header = True`.
# - If files do NOT have headers, set `use_header = False` and set `id_index` to the 0-based index of the ID column.
# - Delimiters are auto-detected; you can override with `delimiter1`/`delimiter2`.
# - Run the script. Reports will be saved to the ./Outputs folder as:
#   - `id_matches.csv` - IDs found in both files
#   - `id_only_in_file1.csv` - IDs unique to File 1
#   - `id_only_in_file2.csv` - IDs unique to File 2
#   - `id_diff_summary.csv` - Statistical summary

# Configuration: set your file paths and ID column
file1_path = r'.\file1.csv'  # e.g., 'd:\Scripts\listA.csv'
file2_path = r'.\file2.csv'  # e.g., 'd:\Scripts\listB.txt'

# If your files have a header row with the ID column name, set id_column
id_column = 'ID'  # e.g., 'id', 'accountNumber'

# If files do NOT have headers, set this to the 0-based index of the ID column and set header=None
use_header = True  # Set to False if there is no header
id_index = 0  # only used when use_header=False

# Optional: delimiter hints; set to None for auto-detection
delimiter1 = None
delimiter2 = None


# Import libraries
import os
import csv
import pandas as pd
from typing import Optional

def detect_delimiter(file_path: str, default: str = ',') -> str:
    """
    Auto-detect the delimiter used in a CSV/TXT file.
    
    Uses csv.Sniffer to detect common delimiters (comma, tab, pipe, semicolon).
    Falls back to the default delimiter if detection fails.
    
    Note: This is a simplified version. The notebook version includes more robust
    validation and fallback logic to handle edge cases like line-ending delimiters.
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(2048)
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
    except Exception:
        return default

def load_file(file_path: str, delimiter_hint: Optional[str], use_header: bool, id_column: Optional[str], id_index: Optional[int]) -> pd.DataFrame:
    """
    Load a CSV/TXT file and extract the ID column.
    
    Args:
        file_path: Path to the input file
        delimiter_hint: Optional delimiter override (None for auto-detection)
        use_header: Whether the file has a header row
        id_column: Name of the ID column (if use_header=True)
        id_index: Zero-based index of the ID column (if use_header=False)
    
    Returns:
        DataFrame with a single 'ID' column containing cleaned, deduplicated IDs
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If ID column/index is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')
    
    # Auto-detect or use provided delimiter
    delimiter = delimiter_hint or detect_delimiter(file_path)
    header = 0 if use_header else None
    df = pd.read_csv(file_path, sep=delimiter, header=header, dtype=str, engine='python')
    
    # Extract and normalise ID column
    if use_header:
        if id_column is None or id_column not in df.columns:
            raise ValueError(f'ID column "{id_column}" not found. Available columns: {list(df.columns)}')
        df[id_column] = df[id_column].astype(str).str.strip()
        df_ids = df[[id_column]].copy()
        df_ids.columns = ['ID']
    else:
        if id_index is None or id_index < 0 or id_index >= df.shape[1]:
            raise ValueError(f'Invalid id_index {id_index}; file has {df.shape[1]} columns')
        df_ids = df.iloc[:, [id_index]].copy()
        df_ids.columns = ['ID']
        df_ids['ID'] = df_ids['ID'].astype(str).str.strip()
    
    # Data cleaning: drop blank IDs and remove duplicates
    df_ids = df_ids[df_ids['ID'].astype(str).str.len() > 0]
    df_ids = df_ids.drop_duplicates().reset_index(drop=True)
    return df_ids

print('Libraries loaded. Ready to process files.')

# Fuzzy normalisation configuration
enable_normalization = True  # Set to False to disable fuzzy matching

def normalize_id(x: str) -> str:
    """
    Normalize an ID for fuzzy matching.
    
    Removes common separators (-, _, spaces), converts to uppercase for
    case-insensitive comparison. Enables matching IDs like "ABC-123" with "ABC123".
    """
    if pd.isna(x):
        return ''
    return (str(x)
            .replace('-', '')
            .replace('_', '')
            .replace(' ', '')
            .strip()
            .upper())

# Load both files
df1 = load_file(file1_path, delimiter1, use_header, id_column if use_header else None, id_index if not use_header else None)
df2 = load_file(file2_path, delimiter2, use_header, id_column if use_header else None, id_index if not use_header else None)

print(f'File1: {len(df1)} unique IDs')
print(f'File2: {len(df2)} unique IDs')

# Prepare sets for comparison (optionally normalised)
if enable_normalization:
    # Create normalised versions for comparison
    df1['ID_norm'] = df1['ID'].apply(normalize_id)
    df2['ID_norm'] = df2['ID'].apply(normalize_id)
    set1 = set(df1['ID_norm'])
    set2 = set(df2['ID_norm'])
else:
    # Use exact ID matching
    set1 = set(df1['ID'])
    set2 = set(df2['ID'])

# Identify matches and differences
matches_norm = sorted(list(set1 & set2))
only_in_1_norm = sorted(list(set1 - set2))
only_in_2_norm = sorted(list(set2 - set1))

# Build display DataFrames preserving original ID values
if enable_normalization:
    # Map normalised IDs back to their original forms for reporting
    map1 = df1.drop_duplicates('ID_norm').set_index('ID_norm')['ID']
    map2 = df2.drop_duplicates('ID_norm').set_index('ID_norm')['ID']
    df_matches = pd.DataFrame({'ID': [map1.get(x, map2.get(x, x)) for x in matches_norm]})
    df_only_in_1 = pd.DataFrame({'ID': [map1.get(x, x) for x in only_in_1_norm]})
    df_only_in_2 = pd.DataFrame({'ID': [map2.get(x, x) for x in only_in_2_norm]})
else:
    df_matches = pd.DataFrame({'ID': sorted(list(set1 & set2))})
    df_only_in_1 = pd.DataFrame({'ID': sorted(list(set1 - set2))})
    df_only_in_2 = pd.DataFrame({'ID': sorted(list(set2 - set1))})

print('Comparison complete.')

# Create summary statistics
df_summary = pd.DataFrame({
    'Metric': ['Unique in File1', 'Unique in File2', 'Matches', 'Only in File1', 'Only in File2'],
    'Count': [len(set1), len(set2), len(df_matches), len(df_only_in_1), len(df_only_in_2)]
})
print(df_summary)

# Prepare styled output (for console display)
matches = df_matches['ID'].tolist()
only_in_1_ids = df_only_in_1['ID'].tolist()
only_in_2_ids = df_only_in_2['ID'].tolist()
non_matching_ids = set(only_in_1_ids + only_in_2_ids)

def highlight_non_matching(s):
    """Apply background color to non-matching IDs in styled DataFrame"""
    return ['background-color: #ffe6e6' if value in non_matching_ids else '' for value in s]

# Create combined DataFrame with status labels
styled_all = pd.concat([
    pd.DataFrame({'ID': matches, 'Status': ['MATCH'] * len(matches)}),
    pd.DataFrame({'ID': only_in_1_ids, 'Status': ['ONLY_IN_FILE1'] * len(only_in_1_ids)}),
    pd.DataFrame({'ID': only_in_2_ids, 'Status': ['ONLY_IN_FILE2'] * len(only_in_2_ids)})
], ignore_index=True)

# Apply styling (green for matches, red for non-matches)
styled_all = styled_all.style.apply(highlight_non_matching, subset=['ID']).apply(lambda s: ['color: #2b7' if v=='MATCH' else 'color: #b22' for v in s], subset=['Status'])
print(styled_all)

# Save reports to ./Outputs folder
base_dir = os.path.dirname(file1_path) or os.getcwd()
# Create Outputs directory if it doesn't exist
output_dir = os.path.join(base_dir, 'Outputs')
os.makedirs(output_dir, exist_ok=True)

out_matches = os.path.join(base_dir, './Outputs/id_matches.csv')
out_only_in_1 = os.path.join(base_dir, './Outputs/id_only_in_file1.csv')
out_only_in_2 = os.path.join(base_dir, './Outputs/id_only_in_file2.csv')
out_summary = os.path.join(base_dir, './Outputs/id_diff_summary.csv')

df_matches.to_csv(out_matches, index=False)
df_only_in_1.to_csv(out_only_in_1, index=False)
df_only_in_2.to_csv(out_only_in_2, index=False)
df_summary.to_csv(out_summary, index=False)

print('\nReports saved:')
print(out_matches)
print(out_only_in_1)
print(out_only_in_2)
print(out_summary)