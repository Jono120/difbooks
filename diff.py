# How to use
# - Set `file1_path` and `file2_path` to your files.
# - If files have headers, set `id_column` to the ID column name and keep `use_header = True`.
# - If files do NOT have headers, set `use_header = False` and set `id_index` to the 0-based index of the ID column.
# - Delimiters are auto-detected; you can override with `delimiter1`/`delimiter2`.
# - Run the cells in order. Reports will be saved next to your input files as `id_matches.csv`, `id_only_in_file1.csv`, `id_only_in_file2.csv`, and `id_diff_summary.csv`.

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
    # Try csv.Sniffer to detect delimiter; fall back to default
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(2048)
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
    except Exception:
        # Try tab as common alternative
        return default

def load_file(file_path: str, delimiter_hint: Optional[str], use_header: bool, id_column: Optional[str], id_index: Optional[int]) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')
    delimiter = delimiter_hint or detect_delimiter(file_path)
    header = 0 if use_header else None
    df = pd.read_csv(file_path, sep=delimiter, header=header, dtype=str, engine='python')
    
    # Normalise whitespace and strip IDs
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
    
    # Drop blank IDs
    df_ids = df_ids[df_ids['ID'].astype(str).str.len() > 0]
    
    # Remove duplicates within each file
    df_ids = df_ids.drop_duplicates().reset_index(drop=True)
    return df_ids

print('Libraries loaded. Ready to process files.')

# Fuzzy normalisation configuration
enable_normalization = True  # Set to False to disable

def normalize_id(x: str) -> str:
    # Remove common separators and whitespace, uppercase for case-insensitive matching
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
    df1['ID_norm'] = df1['ID'].apply(normalize_id)
    df2['ID_norm'] = df2['ID'].apply(normalize_id)
    set1 = set(df1['ID_norm'])
    set2 = set(df2['ID_norm'])
else:
    set1 = set(df1['ID'])
    set2 = set(df2['ID'])

matches_norm = sorted(list(set1 & set2))
only_in_1_norm = sorted(list(set1 - set2))
only_in_2_norm = sorted(list(set2 - set1))

# Build display DataFrames preserving original ID values where possible
if enable_normalization:
    # Map normalised back to original examples for display
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
df_summary = pd.DataFrame({
    'Metric': ['Unique in File1', 'Unique in File2', 'Matches', 'Only in File1', 'Only in File2'],
    'Count': [len(set1), len(set2), len(df_matches), len(df_only_in_1), len(df_only_in_2)]
})
df_summary

# Display results with highlighting for non-matching IDs
matches = df_matches['ID'].tolist()
only_in_1_ids = df_only_in_1['ID'].tolist()
only_in_2_ids = df_only_in_2['ID'].tolist()
non_matching_ids = set(only_in_1_ids + only_in_2_ids)

def highlight_non_matching(s):
    return ['background-color: #ffe6e6' if value in non_matching_ids else '' for value in s]

styled_all = pd.concat([
    pd.DataFrame({'ID': matches, 'Status': ['MATCH'] * len(matches)}),
    pd.DataFrame({'ID': only_in_1_ids, 'Status': ['ONLY_IN_FILE1'] * len(only_in_1_ids)}),
    pd.DataFrame({'ID': only_in_2_ids, 'Status': ['ONLY_IN_FILE2'] * len(only_in_2_ids)})
], ignore_index=True)

styled_all = styled_all.style.apply(highlight_non_matching, subset=['ID']).apply(lambda s: ['color: #2b7' if v=='MATCH' else 'color: #b22' for v in s], subset=['Status'])
styled_all


# Save reports next to input files
base_dir = os.path.dirname(file1_path) or os.getcwd()
out_matches = os.path.join(base_dir, './Outputs/id_matches.csv')
out_only_in_1 = os.path.join(base_dir, './Outputs/id_only_in_file1.csv')
out_only_in_2 = os.path.join(base_dir, './Outputs/id_only_in_file2.csv')
out_summary = os.path.join(base_dir, './Outputs/id_diff_summary.csv')

df_matches.to_csv(out_matches, index=False)
df_only_in_1.to_csv(out_only_in_1, index=False)
df_only_in_2.to_csv(out_only_in_2, index=False)
df_summary.to_csv(out_summary, index=False)

print('Saved:')
print(out_matches)
print(out_only_in_1)
print(out_only_in_2)
print(out_summary)